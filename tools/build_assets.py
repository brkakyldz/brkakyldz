#!/usr/bin/env python3
"""Build the animated SVGs that the profile README shows.

    python tools/build_assets.py

Writes assets/hero-*.svg and assets/glyph-*.svg, each in a light and a dark
version. The look follows the portfolio (brkakyldz.github.io): limestone,
dark ink, one field of deep sea, clay for small marks, Newsreader for text and
IBM Plex Mono for data.

GitHub shows README images through <img>, so an SVG cannot load web fonts or
run scripts. Each file therefore carries its own subset of the fonts it uses
(woff2 in a data: URI, only the characters on that image), and every motion is
CSS or SMIL inside the file. Everything switches off under
prefers-reduced-motion.

Needs: pip install fonttools brotli
"""

from __future__ import annotations

import base64
import io
import math
import pathlib
import random
import re

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
FONTS = TOOLS / "fonts"
OUT = ROOT / "assets"

SERIF = {
    400: [FONTS / "newsreader-latin-400-normal.woff2", FONTS / "newsreader-latin-ext-400-normal.woff2"],
    500: [FONTS / "newsreader-latin-500-normal.woff2", FONTS / "newsreader-latin-ext-500-normal.woff2"],
}
MONO = [FONTS / "ibm-plex-mono-latin-400-normal.woff2", FONTS / "ibm-plex-mono-latin-ext-400-normal.woff2"]

# Portfolio tokens (assets/site.css), plus a night version of the same wall.
LIGHT = dict(
    page="#ffffff", card="#e7e0d3", jamb="#d6cdbc", sill="#d9d0c0", ink="#1c2124", ink_soft="#3a4043",
    muted="#5d5950", rule="#cdc4b3", horizon="#978d7b", clay="#b0573a",
    sky_top="#d9e1e4", sky_low="#f1eadf", haze="#fff6e6", ridge="#9aa9b4", ridge_far="#b9c3c8",
    sea_top="#2c537c", sea="#1c3d63", sea_low="#15304f", glint="#f4ecdd",
    leaf="#000000", leaf_a=0.13, leaf_b=0.09, warm=0.55, grain=0.09,
    g_line="#978d7b", g_node="#ffffff", g_stroke="#3a4043", g_pk="#b0573a",
)
DARK = dict(
    page="#0d1117", card="#151b21", jamb="#0f1419", sill="#1b232b", ink="#ece5d7", ink_soft="#cfc7b8",
    muted="#9d978b", rule="#2a333b", horizon="#5d666d", clay="#d0714e",
    sky_top="#0f1925", sky_low="#1e3043", haze="#41566b", ridge="#16222d", ridge_far="#1b2a37",
    sea_top="#1d3a58", sea="#132b46", sea_low="#0c1d31", glint="#e3e9ee",
    leaf="#000000", leaf_a=0.38, leaf_b=0.26, warm=0.0, grain=0.05,
    g_line="#6b7480", g_node="#0d1117", g_stroke="#c9d1d9", g_pk="#d6774f",
)

REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


# ----------------------------------------------------------------- fonts --

def font_face(family: str, files: list[pathlib.Path], text: str, weight: int = 400) -> str:
    """@font-face rules carrying only the characters in `text`.

    Fontsource splits a family into latin and latin-ext files, so a name like
    "Akyıldız" needs both: each character goes to the first file that has it,
    and each rule gets a unicode-range so the browser picks the right one.
    """
    wanted = set(text) | {" "}
    rules = []
    for path in files:
        font = TTFont(path)
        cmap = font.getBestCmap()
        here = sorted(c for c in wanted if ord(c) in cmap)
        if not here:
            continue
        wanted -= set(here)
        options = subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["kern", "liga", "calt", "pnum", "lnum"]
        options.name_IDs = []
        options.hinting = False
        subsetter = subset.Subsetter(options)
        subsetter.populate(unicodes=[ord(c) for c in here])
        subsetter.subset(font)
        buf = io.BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        ranges = ",".join(f"U+{ord(c):04X}" for c in here)
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:{weight};font-style:normal;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');unicode-range:{ranges}}}"
        )
    missing = "".join(sorted(wanted - {" "}))
    if missing:
        raise SystemExit(f"{family}: no glyph for {missing!r}")
    return "".join(rules)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ------------------------------------------------------------------ hero --

NAME = "Berke Akyıldız"
SENTENCE = (
    "I build AI agent systems in Python: the tools an agent can call, "
    "the rules it can’t talk past, and the evals that check what it actually did."
)
TAGS = "agent systems · LLM evals · observability · integrations"
PLACE = "Antalya, Türkiye"
SHIFT = 9  # how far the view sits behind the jamb

# Two layouts of the same card: a wide one for the desktop profile, and a
# taller one that the README swaps in on narrow screens, where the wide card
# would shrink its text below reading size.
WIDE = dict(
    W=960, H=360,
    arch=(706, 880, 62, 318), horizon=236,
    name=[(54, 104, "Berke Akyıldız")], name_size=60,
    body=[
        "I build AI agent systems in Python: the tools an agent",
        "can call, the rules it can’t talk past, and the evals",
        "that check what it actually did.",
    ],
    body_xy=(56, 152), body_size=21.5, body_step=29,
    tags=[TAGS], tags_xy=(56, 257), mono_size=13, tags_step=0,
    rule=(56, 656, 284), place_y=314,
    leaves="translate(470 -6) scale(.82)",
)
TALL = dict(
    W=600, H=596,
    arch=(436, 560, 40, 252), horizon=190,
    name=[(36, 118, "Berke"), (36, 186, "Akyıldız")], name_size=68,
    body=[
        "I build AI agent systems in Python:",
        "the tools an agent can call, the rules",
        "it can’t talk past, and the evals that",
        "check what it actually did.",
    ],
    body_xy=(40, 312), body_size=26, body_step=35,
    tags=["agent systems · LLM evals", "observability · integrations"], tags_xy=(40, 476), mono_size=16, tags_step=25,
    rule=(40, 560, 516), place_y=556,
    leaves="translate(250 -6) scale(.62)",
)


def leaves(name: str) -> str:
    raw = (TOOLS / name).read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", raw, re.S).group(1)
    return inner


def glints(L: dict, mode: str, sun_x: float) -> str:
    """Light on the water: small strokes, larger and sparser as they come closer."""
    ax0, ax1, _, abot = L["arch"]
    horizon = L["horizon"]
    scale = (ax1 - ax0) / 174
    rng = random.Random(7 if mode == "light" else 11)
    out = []
    for _ in range(round(46 * scale)):
        depth = rng.random() ** 1.7  # 0 at the horizon, 1 at the sill
        y = horizon + 3 + depth * (abot - horizon - 8)
        spread = (10 + depth * 70) * scale
        x = rng.gauss(sun_x, spread * 0.55)
        w = (2.5 + depth * 15 * rng.uniform(0.5, 1.1)) * max(scale, 0.8)
        h = 0.9 + depth * 1.1
        dur = rng.uniform(3.2, 6.8)
        delay = -rng.uniform(0, dur)
        peak = 0.95 if abs(x - sun_x) < spread * 0.4 else 0.55
        out.append(
            f'<rect class="gl" x="{x - w / 2:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.2f}" '
            f'style="animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s;--peak:{peak}"/>'
        )
    return "".join(out)


def hero(t: dict, mode: str, L: dict) -> str:
    W, H = L["W"], L["H"]
    ax0, ax1, atop, abot = L["arch"]
    horizon = L["horizon"]
    r = (ax1 - ax0) / 2
    arch = f"M{ax0} {abot}V{atop + r:.0f}A{r:.0f} {r:.0f} 0 0 1 {ax1} {atop + r:.0f}V{abot}Z"
    fonts = (
        font_face("Newsreader", SERIF[500], NAME, 500)
        + font_face("Newsreader", SERIF[400], "".join(L["body"]), 400)
        + font_face("Plex Mono", MONO, "".join(L["tags"]) + PLACE)
    )
    name = "".join(f'<text class="name" x="{x}" y="{y}">{esc(s)}</text>' for x, y, s in L["name"])
    bx, by = L["body_xy"]
    body = "".join(
        f'<text class="body" x="{bx}" y="{by + i * L["body_step"]}">{esc(line)}</text>'
        for i, line in enumerate(L["body"])
    )
    tx, ty = L["tags_xy"]
    tags = "".join(
        f'<text class="mono" x="{tx}" y="{ty + i * L["tags_step"]}">{esc(line)}</text>'
        for i, line in enumerate(L["tags"])
    )
    r0, r1, ry = L["rule"]
    py = L["place_y"]
    sun_x = ax0 + SHIFT + (ax1 - ax0) * (0.62 if mode == "dark" else 0.46)
    vx0, vx1 = ax0 + SHIFT - 2, ax1 + SHIFT + 2
    hz = horizon
    # Beydağları across the bay: a far ridge and a nearer one, low on the horizon.
    ridge_far = f"M{vx0} {hz}L{vx0} {hz - 9}L{vx0 + 20} {hz - 15}L{vx0 + 38} {hz - 11}L{vx0 + 56} {hz - 21}L{vx0 + 74} {hz - 13}L{vx0 + 92} {hz - 9}L{vx0 + 112} {hz - 4}L{vx0 + 128} {hz - 1}L{vx0 + 128} {hz}Z"
    ridge = f"M{vx0} {hz}L{vx0} {hz - 6}L{vx0 + 14} {hz - 9}L{vx0 + 30} {hz - 6}L{vx0 + 44} {hz - 11}L{vx0 + 62} {hz - 5}L{vx0 + 80} {hz - 2}L{vx0 + 86} {hz}Z"
    moon_y = atop + r + (hz - atop - r) * 0.25
    light_source = (
        f'<circle cx="{sun_x:.0f}" cy="{moon_y:.0f}" r="30" fill="url(#glow)"/>'
        f'<circle cx="{sun_x:.0f}" cy="{moon_y:.0f}" r="8.5" fill="{t["glint"]}" opacity=".92"/>'
        if mode == "dark"
        else ""
    )
    warm = f'<rect width="{W}" height="{H}" fill="url(#warm)"/>' if t["warm"] else ""
    rule_len = r1 - r0
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(NAME)}. {esc(SENTENCE)} {esc(PLACE)}.">
<title>{esc(NAME)}</title>
<style>
{fonts}
.name{{font-family:'Newsreader',Georgia,serif;font-weight:500;font-size:{L["name_size"]}px;letter-spacing:-.6px;fill:{t["ink"]}}}
.body{{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:{L["body_size"]}px;fill:{t["ink_soft"]}}}
.mono{{font-family:'Plex Mono',ui-monospace,Consolas,monospace;font-size:{L["mono_size"]}px;letter-spacing:.15px;fill:{t["muted"]}}}
.leaf-a,.leaf-b{{transform-box:fill-box;transform-origin:100% 0}}
.leaf-a{{animation:sway-a 11s ease-in-out infinite alternate}}
.leaf-b{{animation:sway-b 7.5s ease-in-out -3s infinite alternate}}
@keyframes sway-a{{from{{transform:rotate(-1.6deg)}}to{{transform:rotate(1.3deg) translate(-5px,3px)}}}}
@keyframes sway-b{{from{{transform:rotate(1.4deg)}}to{{transform:rotate(-2deg) translate(4px,2px)}}}}
.gl{{fill:{t["glint"]};opacity:0;transform-box:fill-box;transform-origin:50% 50%;animation-name:glint;animation-timing-function:ease-in-out;animation-iteration-count:infinite}}
@keyframes glint{{0%,100%{{opacity:0;transform:translateX(-1.5px) scaleX(.6)}}50%{{opacity:var(--peak);transform:translateX(1.5px) scaleX(1)}}}}
.swell{{animation:swell 9s ease-in-out infinite alternate}}
@keyframes swell{{from{{transform:translateX(-6px)}}to{{transform:translateX(6px)}}}}
.rule{{stroke-dasharray:{rule_len};stroke-dashoffset:{rule_len};animation:draw 1.8s cubic-bezier(.2,.7,.2,1) .25s forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.rule{{stroke-dashoffset:0}}.gl{{opacity:calc(var(--peak) * .7)}}}}
</style>
<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<clipPath id="win"><path d="{arch}"/></clipPath>
<mask id="wall"><rect width="{W}" height="{H}" fill="#fff"/><path d="{arch}" fill="#000"/></mask>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .3 0 0 0 0 .25 0 0 0 0 .18 0 0 0 {t["grain"]} 0"/></filter>
<filter id="blur-a" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="blur-b" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="9"/></filter>
<radialGradient id="warm" cx="80%" cy="18%" r="45%"><stop offset="0" stop-color="#fff4de" stop-opacity="{t["warm"]}"/><stop offset="1" stop-color="#fff4de" stop-opacity="0"/></radialGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{t["glint"]}" stop-opacity=".22"/><stop offset="1" stop-color="{t["glint"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["sky_top"]}"/><stop offset="1" stop-color="{t["sky_low"]}"/></linearGradient>
<radialGradient id="haze" cx="{(sun_x - vx0) / (vx1 - vx0):.2f}" cy="1" r=".75"><stop offset="0" stop-color="{t["haze"]}" stop-opacity=".9"/><stop offset="1" stop-color="{t["haze"]}" stop-opacity="0"/></radialGradient>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t["sea_top"]}"/><stop offset=".35" stop-color="{t["sea"]}"/><stop offset="1" stop-color="{t["sea_low"]}"/></linearGradient>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{t["card"]}"/>
{warm}
<rect width="{W}" height="{H}" filter="url(#grain)"/>
<path d="{arch}" fill="{t["jamb"]}"/>
<g clip-path="url(#win)"><g transform="translate({SHIFT} 0)">
<rect x="{ax0 - 4}" y="{atop - 4}" width="{ax1 - ax0 + 8}" height="{hz - atop + 4}" fill="url(#sky)"/>
<rect x="{ax0 - 4}" y="{hz - 70}" width="{ax1 - ax0 + 8}" height="70" fill="url(#haze)"/>
{light_source}
<path d="{ridge_far}" fill="{t["ridge_far"]}" transform="translate({-SHIFT} 0)"/>
<path d="{ridge}" fill="{t["ridge"]}" transform="translate({-SHIFT} 0)"/>
<rect x="{ax0 - 4}" y="{hz}" width="{ax1 - ax0 + 8}" height="{abot - hz + 4}" fill="url(#sea)"/>
<g class="swell" opacity=".12" stroke="{t["glint"]}" stroke-width=".8" fill="none">
<path d="M{ax0 - 20} {hz + 14}q12 -2 24 0t24 0t24 0t24 0t24 0t24 0t24 0t24 0t24 0"/>
<path d="M{ax0 - 20} {hz + 34}q16 -3 32 0t32 0t32 0t32 0t32 0t32 0t32 0"/>
<path d="M{ax0 - 20} {hz + 60}q22 -4 44 0t44 0t44 0t44 0t44 0"/>
</g>
{glints(L, mode, sun_x)}
</g></g>
<rect x="{ax0 - 12}" y="{abot}" width="{ax1 - ax0 + 24}" height="7" fill="{t["sill"]}"/>
<rect x="{ax0 - 12}" y="{abot + 7}" width="{ax1 - ax0 + 24}" height="1" fill="{t["rule"]}"/>
<g mask="url(#wall)">
<g transform="{L["leaves"]}"><g transform="translate(-30 40) scale(.8)"><g class="leaf-b" filter="url(#blur-b)" opacity="{t["leaf_b"]}" fill="{t["leaf"]}">{leaves("leaves-b.svg")}</g></g></g>
<g transform="{L["leaves"]}"><g class="leaf-a" filter="url(#blur-a)" opacity="{t["leaf_a"]}" fill="{t["leaf"]}">{leaves("leaves-a.svg")}</g></g>
</g>
{name}
{body}
{tags}
<path class="rule" d="M{r0} {ry}H{r1}" stroke="{t["horizon"]}" stroke-width="1" fill="none"/>
<rect x="{r0}" y="{py - 8}" width="7" height="7" fill="{t["clay"]}"/>
<text class="mono" x="{r0 + 16}" y="{py}">{esc(PLACE)}</text>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="{t["rule"]}"/>
</svg>
"""


# ---------------------------------------------------------------- glyphs --
# Small drawings of each system at work, in the portfolio's vocabulary:
# lines are the paths work takes, open nodes are steps, filled ones are where
# code decides, and the clay dot is one request moving through.

def pk(path: str, dur: float, key_times: str, key_points: str, vis: str, vis_times: str, begin: float = 0.0) -> str:
    return (
        f'<circle class="pk" r="2.3" opacity="0">'
        f'<animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" calcMode="linear" '
        f'keyTimes="{key_times}" keyPoints="{key_points}" path="{path}"/>'
        f'<animate attributeName="opacity" dur="{dur}s" begin="{begin}s" repeatCount="indefinite" '
        f'values="{vis}" keyTimes="{vis_times}"/></circle>'
    )


GLYPHS = {
    # Copied from the portfolio home page, where each project has this drawing.
    "hotel": (
        "A guest's message passes the agent and reaches a code gate before it is written to the database; "
        "one branch goes to a manager's approval, and a change at the hotel sends a message back to the guest.",
        '<path class="ln" d="M6 30H120"/>'
        '<path class="ln" d="M76 30C76 40 80 44 90 44H100"/>'
        '<path class="ln faint" d="M124 26C112 6 18 6 8 26"/>'
        '<circle class="nd" cx="6" cy="30" r="2.6"/>'
        '<circle class="nd" cx="38" cy="30" r="3.8"/>'
        '<rect class="nd solid" x="72" y="26" width="8" height="8"/>'
        '<circle class="nd" cx="102" cy="44" r="2.6"/>'
        '<rect class="nd" x="120" y="26" width="8" height="8"/>'
        + pk("M6 30H120", 8, "0;.18;.26;.42;1", "0;.3;.3;1;1", "0;1;1;0;0", "0;.02;.4;.44;1")
        + pk("M76 30C76 40 80 44 90 44H100", 8, "0;.26;.34;1", "0;0;1;1", "0;0;1;0;0", "0;.25;.27;.36;1")
        + pk("M124 26C112 6 18 6 8 26", 8, "0;.36;1", "0;1;1", "0;1;1;0;0", "0;.03;.34;.38;1", begin=4),
    ),
    "experiments": (
        "An agent's run goes from the request through three tool calls to its reply. A judge reads only the reply "
        "and passes it; a plain check over the trace below stops at the second tool call and flags it.",
        '<path class="ln" d="M6 22H120"/>'
        '<path class="ln faint" d="M124 18C121 6 110 4 100 4"/>'
        '<path class="ln" d="M6 22C14 22 16 40 26 40H108"/>'
        '<circle class="nd" cx="6" cy="22" r="2.6"/>'
        '<circle class="nd" cx="34" cy="22" r="2.4"/>'
        '<rect class="nd solid" x="55" y="19" width="6" height="6"/>'
        '<circle class="nd" cx="82" cy="22" r="2.4"/>'
        '<rect class="nd" x="120" y="18" width="8" height="8"/>'
        '<circle class="nd" cx="98" cy="4" r="2.6"/>'
        '<rect class="nd" x="108" y="36" width="8" height="8">'
        '<animate attributeName="fill" dur="8s" repeatCount="indefinite" calcMode="discrete" '
        'values="{NODE};{PK};{NODE}" keyTimes="0;.62;.95"/></rect>'
        '<circle class="ring" cx="58" cy="22" r="3" opacity="0">'
        '<animate attributeName="r" dur="8s" repeatCount="indefinite" values="3;3;10;10" keyTimes="0;.3;.42;1"/>'
        '<animate attributeName="opacity" dur="8s" repeatCount="indefinite" values="0;0;.8;0;0" keyTimes="0;.3;.31;.42;1"/></circle>'
        + pk("M6 22H120", 8, "0;.5;1", "0;1;1", "0;1;1;0;0", "0;.02;.49;.52;1")
        + pk("M124 18C121 6 110 4 100 4", 8, "0;.52;.64;1", "0;0;1;1", "0;0;1;0;0", "0;.51;.53;.66;1")
        + pk("M6 22C14 22 16 40 26 40H108", 8, "0;.62;1", "0;1;1", "0;1;1;0;0", "0;.02;.6;.63;1"),
    ),
    "digest": (
        "A pipeline: collect, dedupe and enrich, then summarise in parallel branches, rank and persist.",
        '<path class="ln" d="M6 24H126"/>'
        '<path class="ln" d="M52 24C62 24 62 10 72 10H88C98 10 98 24 106 24"/>'
        '<path class="ln" d="M52 24C62 24 62 38 72 38H88C98 38 98 24 106 24"/>'
        '<circle class="nd" cx="6" cy="24" r="2.6"/>'
        '<circle class="nd" cx="22" cy="24" r="2.6"/>'
        '<circle class="nd" cx="38" cy="24" r="2.6"/>'
        '<circle class="nd" cx="80" cy="10" r="2.6"/>'
        '<circle class="nd" cx="80" cy="24" r="2.6"/>'
        '<circle class="nd" cx="80" cy="38" r="2.6"/>'
        '<circle class="nd" cx="116" cy="24" r="2.6"/>'
        '<circle class="nd" cx="126" cy="24" r="2.6"/>'
        + pk("M6 24H52C62 24 62 10 72 10H88C98 10 98 24 106 24H126", 6, "0;.28;.58;.72;1", "0;.35;.85;1;1", "0;1;1;0;0", "0;.03;.7;.76;1")
        + pk("M6 24H126", 6, "0;.28;.58;.72;1", "0;.383;.833;1;1", "0;1;1;0;0", "0;.03;.7;.76;1")
        + pk("M6 24H52C62 24 62 38 72 38H88C98 38 98 24 106 24H126", 6, "0;.28;.58;.72;1", "0;.35;.85;1;1", "0;1;1;0;0", "0;.03;.7;.76;1"),
    ),
    "brain": (
        "Three inputs, one output: notes pass a check before they reach the memory file that every session loads.",
        '<path class="ln" d="M6 8C30 8 34 24 58 24"/>'
        '<path class="ln" d="M6 24H58"/>'
        '<path class="ln" d="M6 40C30 40 34 24 58 24"/>'
        '<path class="ln" d="M58 24H120"/>'
        '<path class="ln" d="M90 15V33"/>'
        '<circle class="nd" cx="6" cy="8" r="2.6"/>'
        '<circle class="nd" cx="6" cy="24" r="2.6"/>'
        '<circle class="nd" cx="6" cy="40" r="2.6"/>'
        '<circle class="nd" cx="58" cy="24" r="3.8"/>'
        '<rect class="nd solid" x="120" y="20" width="8" height="8"/>'
        + pk("M6 8C30 8 34 24 58 24H120", 6, "0;.7;1", "0;1;1", "0;1;1;0;0", "0;.04;.66;.71;1", 0)
        + pk("M6 40C30 40 34 24 58 24H120", 6, "0;.7;1", "0;1;1", "0;1;1;0;0", "0;.04;.66;.71;1", 2)
        + pk("M6 24H120", 6, "0;.7;1", "0;1;1", "0;1;1;0;0", "0;.04;.66;.71;1", 4),
    ),
    "techinves": (
        "Two pipelines: model-free scoring along the top, and a researched report below that passes a rule gate "
        "before it is published.",
        '<path class="ln" d="M6 24C16 24 18 10 28 10H124"/>'
        '<path class="ln" d="M46 6.5V13.5M64 6.5V13.5M82 6.5V13.5M100 6.5V13.5"/>'
        '<path class="ln" d="M6 24C16 24 18 38 28 38H40"/>'
        '<path class="ln faint" d="M40 38C50 38 52 30 62 30H72C82 30 84 38 94 38"/>'
        '<path class="ln faint" d="M40 38H94"/>'
        '<path class="ln faint" d="M40 38C50 38 52 46 62 46H72C82 46 84 38 94 38"/>'
        '<path class="ln" d="M100 38H124"/>'
        '<rect class="nd" x="94" y="35" width="6" height="6"/>'
        '<circle class="nd" cx="6" cy="24" r="2.6"/>'
        '<circle class="nd solid" cx="126" cy="10" r="2.6"/>'
        '<circle class="nd" cx="126" cy="38" r="2.6"/>'
        + pk("M6 24C16 24 18 10 28 10H124", 7, "0;.6;1", "0;1;1", "0;1;1;0;0", "0;.03;.58;.62;1")
        + pk("M6 24C16 24 18 38 28 38H40C50 38 52 30 62 30H72C82 30 84 38 94 38", 7, "0;.5;1", "0;1;1", "0;1;1;0;0", "0;.03;.5;.52;1", 0.6)
        + pk("M6 24C16 24 18 38 28 38H94", 7, "0;.5;1", "0;1;1", "0;1;1;0;0", "0;.03;.5;.52;1", 0.6)
        + pk("M6 24C16 24 18 38 28 38H40C50 38 52 46 62 46H72C82 46 84 38 94 38", 7, "0;.5;1", "0;1;1", "0;1;1;0;0", "0;.03;.5;.52;1", 0.6)
        + pk("M100 38H124", 7, "0;.58;.74;1", "0;0;1;1", "0;0;1;0;0", "0;.57;.59;.76;1", 0.6),
    ),
}


def glyph(name: str, t: dict) -> str:
    label, inner = GLYPHS[name]
    inner = inner.replace("{NODE}", t["g_node"]).replace("{PK}", t["g_pk"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 -8 144 64" width="288" height="128" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<style>
.ln{{fill:none;stroke:{t["g_line"]};stroke-width:1.15;vector-effect:non-scaling-stroke}}
.faint{{stroke-dasharray:2 3}}
.nd{{fill:{t["g_node"]};stroke:{t["g_stroke"]};stroke-width:1.15;vector-effect:non-scaling-stroke}}
.solid{{fill:{t["g_stroke"]}}}
.pk{{fill:{t["g_pk"]}}}
.ring{{fill:none;stroke:{t["g_pk"]};stroke-width:1.1;vector-effect:non-scaling-stroke}}
</style>
{inner}
</svg>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for mode, t in (("light", LIGHT), ("dark", DARK)):
        (OUT / f"hero-{mode}.svg").write_text(hero(t, mode, WIDE))
        (OUT / f"hero-{mode}-narrow.svg").write_text(hero(t, mode, TALL))
        for name in GLYPHS:
            (OUT / f"glyph-{name}-{mode}.svg").write_text(glyph(name, t))
    for p in sorted(OUT.glob("*.svg")):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
