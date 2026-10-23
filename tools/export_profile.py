#!/usr/bin/env python3
"""Export the profile README images from assets/profile/design.html.

    python tools/export_profile.py            # everything
    python tools/export_profile.py --stills   # PNGs only (no animation)

Writes to assets/profile/:

    hello.webp, hello-mobile.webp   animated hero, 5 s loop
    hello.png,  hello-mobile.png    still hero (reduced motion) = the loop's first frame
    issuepilot.png, brain.png, hotel.png, digest.png      project cards
    issuepilot-mobile.png, ...                            phone layout of the cards

Everything is rendered at device scale factor 2: desktop images are drawn at
846 px, phone images at 343 px, where the page's @container (max-width:600px)
rules switch to the phone layout. Corners are transparent.

The hero motion is CSS. Frames are captured deterministically: every
animation is paused through document.getAnimations() and stepped with
currentTime, so the result does not depend on how fast the machine renders.
The frames are then assembled into an animated WebP, which keeps full colour
(a GIF has 256) and a smooth alpha edge. Lossy WebP softens fine text, so the
file is built in two halves: the first frame (the whole artwork) is lossless
and every later frame is a lossy patch over only the part that moves, made by
ffmpeg (libwebp_anim). Everything outside that patch, the lettering included,
is therefore pixel-exact in every frame.

Needs: Python 3 with playwright (and its Chromium), ffmpeg with libwebp on PATH
(or set FFMPEG), and the Windows system fonts the artwork uses: Bahnschrift,
Segoe UI Variable, Segoe Print, Consolas.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import struct
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "profile"
DESIGN = (OUT / "design.html").as_uri()

SCALE = 2
LOOP_MS = 5000          # the hero's CSS loop
FPS = 25                # 40 ms per frame
WEBP_QUALITY = 98       # lossy patches; below ~96 the glass gets blotchy

# Page widths and the browser viewport that holds them.
VARIANTS = {
    "desktop": {"width": 846, "viewport": 900, "suffix": ""},
    "phone": {"width": 343, "viewport": 400, "suffix": "-mobile"},
}
CARDS = ["issuepilot", "brain", "hotel", "digest"]


def freeze(page, t_ms: float) -> None:
    """Pause every animation and put it at t_ms."""
    page.evaluate(
        "t => document.getAnimations().forEach(a => { a.pause(); a.currentTime = t })",
        t_ms,
    )


def open_page(browser, variant: dict):
    context = browser.new_context(
        viewport={"width": variant["viewport"], "height": 1000},
        device_scale_factor=SCALE,
        reduced_motion="no-preference",  # the page switches the motion off otherwise
    )
    page = context.new_page()
    page.goto(f"{DESIGN}?w={variant['width']}")
    page.evaluate("document.fonts.ready")
    return page


def find_ffmpeg() -> str:
    ffmpeg = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not ffmpeg:
        sys.exit("ffmpeg not found: put it on PATH or set FFMPEG")
    return ffmpeg


def run_ffmpeg(ffmpeg: str, *args: str) -> None:
    subprocess.run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def riff_chunks(data: bytes) -> list[tuple[bytes, bytes]]:
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a WebP file")
    chunks, pos = [], 12
    while pos + 8 <= len(data):
        tag = data[pos:pos + 4]
        (size,) = struct.unpack("<I", data[pos + 4:pos + 8])
        chunks.append((tag, data[pos + 8:pos + 8 + size]))
        pos += 8 + size + (size & 1)
    return chunks


def riff_chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack("<I", len(payload)) + payload + (b"\0" if len(payload) & 1 else b"")


def merge_webp(lossless_still: bytes, lossy_animation: bytes) -> bytes:
    """First frame from a lossless still, every other frame from a lossy animation.

    Each ANMF chunk is a 16-byte header (offset, size, duration, blend/dispose
    flags) followed by the frame's image chunks. Frame 1 keeps the animation's
    header, so the canvas rules the encoder planned for frame 2 onwards still
    hold, and gets the lossless pixels instead. A later frame only replaces the
    area it covers, so everything outside the moving part stays lossless.
    """
    still = [c for c in riff_chunks(lossless_still) if c[0] in (b"ALPH", b"VP8 ", b"VP8L")]
    chunks = riff_chunks(lossy_animation)
    head = [c for c in chunks if c[0] in (b"VP8X", b"ANIM")]
    frames = [payload for tag, payload in chunks if tag == b"ANMF"]
    first = frames[0][:16] + b"".join(riff_chunk(t, d) for t, d in still)
    body = (
        b"WEBP"
        + b"".join(riff_chunk(t, d) for t, d in head)
        + riff_chunk(b"ANMF", first)
        + b"".join(riff_chunk(b"ANMF", f) for f in frames[1:])
    )
    return b"RIFF" + struct.pack("<I", len(body)) + body


def assemble_webp(frames: pathlib.Path, count: int, target: pathlib.Path, ffmpeg: str) -> None:
    patches, still = frames / "patches.webp", frames / "first.webp"
    run_ffmpeg(
        ffmpeg, "-framerate", str(FPS), "-i", str(frames / "f%04d.png"), "-frames:v", str(count),
        "-c:v", "libwebp_anim", "-lossless", "0", "-quality", str(WEBP_QUALITY),
        "-compression_level", "6", "-loop", "0", "-pix_fmt", "bgra", str(patches),
    )
    run_ffmpeg(
        ffmpeg, "-i", str(frames / "f0001.png"), "-c:v", "libwebp", "-lossless", "1",
        "-compression_level", "6", "-pix_fmt", "bgra", str(still),
    )
    target.write_bytes(merge_webp(still.read_bytes(), patches.read_bytes()))


def check_webp(path: pathlib.Path, count: int) -> None:
    """The file must loop forever and last one full CSS loop."""
    chunks = riff_chunks(path.read_bytes())
    anim = next(p for t, p in chunks if t == b"ANIM")
    (loops,) = struct.unpack("<H", anim[4:6])
    frames = [p for t, p in chunks if t == b"ANMF"]
    total = sum(int.from_bytes(f[12:15], "little") for f in frames)
    kinds = [[t for t, _ in riff_chunks(b"RIFF\0\0\0\0WEBP" + f[16:])] for f in frames]
    if loops != 0 or total != LOOP_MS or kinds[0] != [b"VP8L"] or any(b"VP8L" in k for k in kinds[1:]):
        raise SystemExit(f"{path.name}: unexpected structure (loops={loops}, ms={total}, first={kinds[0]})")
    print(f"  {len(frames)} stored frames for {count} steps, {total} ms, loops forever, first frame lossless")


def export(stills_only: bool) -> None:
    ffmpeg = None if stills_only else find_ffmpeg()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for name, variant in VARIANTS.items():
            suffix = variant["suffix"]
            page = open_page(browser, variant)

            # Cards.
            for card in CARDS:
                page.locator(f"#{card}").screenshot(
                    path=OUT / f"{card}{suffix}.png", omit_background=True
                )
                print(f"{card}{suffix}.png")

            # Hero: the still is the loop's first frame (what reduced motion shows).
            hero = page.locator("#hero-wrap")
            freeze(page, 0)
            page.wait_for_timeout(200)
            hero.screenshot(path=OUT / f"hello{suffix}.png", omit_background=True)
            print(f"hello{suffix}.png")

            if stills_only:
                page.context.close()
                continue

            # Hero: animated loop.
            count = LOOP_MS * FPS // 1000
            with tempfile.TemporaryDirectory(prefix="hero-frames-") as tmp:
                tmp_dir = pathlib.Path(tmp)
                for i in range(count):
                    freeze(page, i * 1000 / FPS)
                    hero.screenshot(path=tmp_dir / f"f{i + 1:04d}.png", omit_background=True)
                target = OUT / f"hello{suffix}.webp"
                assemble_webp(tmp_dir, count, target, ffmpeg)
            print(f"hello{suffix}.webp  {target.stat().st_size / 1024:.0f} KB")
            check_webp(target, count)
            page.context.close()
        browser.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--stills", action="store_true", help="export the PNGs only")
    export(ap.parse_args().stills)
