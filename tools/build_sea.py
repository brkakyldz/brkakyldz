#!/usr/bin/env python3
"""Draws the profile README's sea artwork into assets/.

Run from anywhere: python tools/build_sea.py

Every sparkle is placed by a seeded generator, so a rebuild draws the same
picture. GitHub shows these SVGs as images, which cannot load web fonts, so
each file embeds its own fonts, cut down to the characters it uses.
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
ASSETS = ROOT / "assets"
MANROPE = FONTS / "Manrope-wght.ttf"
PLEX = FONTS / "ibm-plex-mono-latin-400-normal.woff2"

SANS = "'Manrope Sea'"
MONO = "'Plex Sea'"


# ---------------------------------------------------------------- fonts

def _manrope(weight):
    return instancer.instantiateVariableFont(TTFont(MANROPE), {"wght": weight})


def font_face(family, weight, text, source=None, kern=True):
    """An @font-face rule embedding only the glyphs `text` needs."""
    font = TTFont(source) if source else _manrope(weight)
    opts = subset.Options()
    opts.flavor = "woff2"
    if not kern:
        opts.layout_features = []
    sub = subset.Subsetter(opts)
    sub.populate(text="".join(sorted(set(text))))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:{family};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


_metrics = {}


def text_width(text, size, weight, spacing=0.0):
    """Advance width of `text` without kerning, in user units."""
    if weight not in _metrics:
        f = _manrope(weight)
        _metrics[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[weight]
    adv = sum(hmtx[cmap[ord(c)]][0] for c in text)
    return adv * size / upm + spacing * len(text)


# ---------------------------------------------------------------- random

def mulberry32(seed):
    state = [seed & 0xFFFFFFFF]

    def rand():
        state[0] = (state[0] + 0x6D2B79F5) & 0xFFFFFFFF
        a = state[0]
        t = ((a ^ (a >> 15)) * (1 | a)) & 0xFFFFFFFF
        t = ((t + (((t ^ (t >> 7)) * (61 | t)) & 0xFFFFFFFF)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rand


def gauss(r):
    return (r() + r() + r() + r() - 2) / 2


def n(x, d=1):
    s = f"{x:.{d}f}"
    return "0" if s in ("-0", "-0.0", "-0.00") else s


# ---------------------------------------------------------------- palettes

# The hero is midday. The four cards walk through a day, left to right and
# top to bottom: morning, noon, afternoon, dusk.
NOON = dict(sky=("#74a9d4", "#d6eaf5"), sun="#fff7e2", sun_a=.8,
            sea=("#07235a", "#113882", "#1d50a4"), glow="#fff2d2", col_a=.26,
            glit="#ffffff", name=("#d6e3fa", "#ffffff"), body="#c3d3f0",
            sub="#8aa6d2", hull="#e2362b", vig=.3, grain=.05)
MORNING = dict(NOON, sky=("#9cc2e3", "#e8f0f5"), sun="#fff6e6", glow="#fff3dc",
               sea=("#0a2a62", "#13408c", "#1f56aa"))
AFTERNOON = dict(NOON, sky=("#8fb3d8", "#f3dcae"), sun="#ffe2a6", glow="#ffe0a0",
                 glit="#fff3d6", sea=("#0a2558", "#173f80", "#2a5799"), body="#d3dcec")
DUSK = dict(NOON, sky=("#6f6aa6", "#f2b39b"), sun="#ffc4a3", glow="#ffc0a0",
            glit="#ffe6d8", sea=("#14214f", "#22306b", "#334186"),
            body="#ddd3e8", sub="#a69bc8", vig=.36)

CSS = """
.gtw{animation:gtw 2s ease-in-out infinite alternate}
@keyframes gtw{from{opacity:.04}to{opacity:1}}
.fl{animation:fl 6s ease-out infinite}
@keyframes fl{0%,84%{transform:scale(0);opacity:0}91%{transform:scale(1);opacity:1}100%{transform:scale(.2);opacity:0}}
.bdr{animation:bdr 20s ease-in-out infinite alternate}
@keyframes bdr{from{transform:translateX(-14px)}to{transform:translateX(10px)}}
.bob{animation:bob 3.6s ease-in-out infinite alternate}
@keyframes bob{from{transform:rotate(-2deg)}to{transform:rotate(1.6deg) translateY(1.2px)}}
.flap{animation:flap .9s ease-in-out infinite}
@keyframes flap{0%,100%{transform:scaleY(1)}50%{transform:scaleY(-.6)}}
.sh{stroke-dasharray:3 15;animation:sh 6s linear infinite}
@keyframes sh{to{stroke-dashoffset:-180}}
.wind{animation:wind 8s ease-in-out infinite}
@keyframes wind{from{transform:translateX(-260px)}to{transform:translateX(560px)}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

RIPPLE = "M4 4h22M58 9h12M94 3h28M18 13h16M78 14h24M122 10h10M40 1h8"


# ---------------------------------------------------------------- pieces

def sea_defs(T, W, H, HZ, SX, sun_r, col_w):
    return (
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["sky"][0]}"/><stop offset="1" stop-color="{T["sky"][1]}"/></linearGradient>'
        f'<radialGradient id="sun" gradientUnits="userSpaceOnUse" cx="{SX}" cy="{HZ}" r="{sun_r}"><stop offset="0" stop-color="{T["sun"]}" stop-opacity="{T["sun_a"]}"/><stop offset=".28" stop-color="{T["sun"]}" stop-opacity="{n(T["sun_a"] * .28, 3)}"/><stop offset="1" stop-color="{T["sun"]}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["sea"][0]}"/><stop offset=".45" stop-color="{T["sea"][1]}"/><stop offset="1" stop-color="{T["sea"][2]}"/></linearGradient>'
        f'<linearGradient id="col" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{T["glow"]}" stop-opacity="{T["col_a"]}"/><stop offset="1" stop-color="{T["glow"]}" stop-opacity=".03"/></linearGradient>'
        '<filter id="blur" x="-50%" y="-30%" width="200%" height="160%"><feGaussianBlur stdDeviation="9"/></filter>'
        '<filter id="soft" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.2"/></filter>'
        f'<radialGradient id="vig" cx=".45" cy=".5" r=".78"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{T["vig"]}"/></radialGradient>'
        '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 0 0 0 1 0"/></filter>'
    )


def sea_body(T, W, H, HZ, SX, col_w, bands):
    """Sky, water, moving ripples, sun haze and the light column."""
    defs = "".join(
        f'<pattern id="r{i}" width="140" height="16" patternUnits="userSpaceOnUse" patternTransform="scale({s})"><path d="{RIPPLE}" stroke="#ffffff" stroke-opacity="{op}" stroke-width="1.1" stroke-linecap="round"/></pattern>'
        for i, (y, h, s, dur, op) in enumerate(bands))
    body = f'<rect width="{W}" height="{HZ}" fill="url(#sky)"/>' if HZ else ""
    body += f'<rect y="{HZ}" width="{W}" height="{H - HZ}" fill="url(#sea)"/>'
    for i, (y, h, s, dur, op) in enumerate(bands):
        rw = 140 * s
        body += (f'<g><rect x="{n(-rw * 2)}" y="{y}" width="{n(W + rw * 4)}" height="{h}" fill="url(#r{i})"/>'
                 f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{n(rw)} 0" dur="{dur}s" repeatCount="indefinite"/></g>')
    if col_w:
        body += f'<rect width="{W}" height="{H}" fill="url(#sun)"/>'
        body += f'<path d="M{SX - 8} {HZ}L{SX + 8} {HZ}L{SX + col_w} {H}L{SX - col_w} {H}Z" fill="url(#col)" filter="url(#blur)"/>'
        body += f'<rect x="{SX - 95}" y="{HZ - .6}" width="190" height="1.6" fill="{T["glow"]}" opacity=".75" filter="url(#soft)"/>'
    return defs, body


def glitter(r, T, W, H, HZ, SX, count, slope, scatter):
    out = []
    for _ in range(count):
        t = r()
        y = HZ + 1 + t ** 1.7 * (H - HZ - 2)
        k = (y - HZ) / (H - HZ)
        hw = 6 + (y - HZ) * slope
        dx = gauss(r) * hw * .9
        x = SX + dx
        e = min(1, abs(dx) / hw)
        w = .8 + k * (3 + r() * 7)
        h = .55 + k * 1.2
        pk = (.35 + .65 * (1 - e)) * (.6 + .4 * r())
        dur, delay = .7 + r() * 2.6, -r() * 3
        out.append(f'<rect class="gtw" x="{n(x - w / 2)}" y="{n(y)}" width="{n(w)}" height="{n(h, 2)}" rx="{n(h / 2, 2)}" fill="{T["glit"]}" fill-opacity="{n(pk, 2)}" style="animation-duration:{n(dur, 2)}s;animation-delay:{n(delay, 2)}s"/>')
    for _ in range(scatter):
        y = HZ + 3 + r() * (H - HZ - 6)
        k = (y - HZ) / (H - HZ)
        w = .8 + k * 3.5 * r()
        x = r() * W
        dur, delay = 1.4 + r() * 2.6, -r() * 3
        out.append(f'<rect class="gtw" x="{n(x)}" y="{n(y)}" width="{n(w)}" height=".8" fill="{T["glit"]}" fill-opacity=".28" style="animation-duration:{n(dur, 2)}s;animation-delay:{n(delay, 2)}s"/>')
    return "".join(out)


def glints(r, T, H, HZ, SX, count, slope, size=1.0):
    out = []
    for _ in range(count):
        t = .04 + r() * .5
        y = HZ + t ** 1.3 * (H - HZ)
        k = (y - HZ) / (H - HZ)
        hw = 6 + (y - HZ) * slope
        x = SX + gauss(r) * hw * .6
        sc = (.55 + k * .9) * size
        du = 4 + r() * 6
        out.append(f'<g transform="translate({n(x)} {n(y)}) scale({n(sc, 2)})"><g class="fl" style="animation-duration:{n(du, 2)}s;animation-delay:{n(-r() * du, 2)}s"><circle r="5" fill="{T["glow"]}" opacity=".6" filter="url(#soft)"/><path d="M0-7L.7-.7L7 0L.7.7L0 7L-.7.7L-7 0L-.7-.7Z" fill="#fff"/></g></g>')
    return "".join(out)


def boat(T, x, y, scale):
    sail, jib = "#fbfbf8", "#e6ebf3"
    refl = ""
    rows = [(4, 16, .5, T["hull"]), (7.5, 11, .4, T["hull"]), (11, 14, .28, sail),
            (15, 9, .22, sail), (19.5, 12, .18, sail), (24, 6, .14, sail), (29, 8, .1, sail)]
    for i, (ry, rw, op, c) in enumerate(rows):
        refl += f'<rect class="gtw" x="{n(-rw / 2 + (2 if i % 2 else -1))}" y="{ry}" width="{rw}" height="1.6" rx=".8" fill="{c}" fill-opacity="{op}" style="animation-duration:{n(1.6 + i * .3)}s"/>'
    return (f'<g transform="translate({x} {y}) scale({scale})"><g class="bdr">{refl}<g class="bob">'
            '<path d="M0 -47v43" stroke="#d6dbe4" stroke-width="1.2"/>'
            f'<path d="M1 -46c7 12 12 27 14 40H1z" fill="{sail}"/><path d="M-1 -42L-13 -6h12z" fill="{jib}"/>'
            f'<path d="M-17 -4h34l-4 6h-26z" fill="{T["hull"]}"/><path d="M-17 -4h34" stroke="#00000055" stroke-width="1"/>'
            '</g></g></g>')


def gulls(paths):
    out = ""
    for values, dur, scale in paths:
        out += (f'<g><animateTransform attributeName="transform" type="translate" values="{values}" dur="{dur}s" repeatCount="indefinite"/>'
                f'<g transform="scale({scale})"><path class="flap" d="M-6 0Q-3-3.2 0 0Q3-3.2 6 0" fill="none" stroke="#eef4fb" stroke-width="1.1" stroke-linecap="round" style="animation-duration:{n(.9 / scale, 2)}s"/></g></g>')
    return out


def finish(T, W, H):
    return (f'<rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{T["grain"]}"/>')


def svg(W, H, radius, label, faces, defs, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">'
            f'<title>{label}</title><style>{faces}{CSS}</style>'
            f'<defs><clipPath id="frame"><rect width="{W}" height="{H}" rx="{radius}"/></clipPath>{defs}</defs>'
            f'<g clip-path="url(#frame)">{body}</g></svg>')


def check_clear(label, x, width, top, SX, HZ, slope):
    """Warn when a line of text runs into the glitter column."""
    edge = SX - .8 * (6 + max(0, top - HZ) * slope)
    if x + width > edge:
        print(f"  ! {label}: ends at {x + width:.0f}, glitter starts near {edge:.0f}")


# ---------------------------------------------------------------- artwork

def hero():
    W, H, HZ, SX = 680, 250, 40, 510
    T, r = NOON, mulberry32(7)
    name, coords = "Berke Akyıldız", "36.89° N · 30.71° E"
    bands = [(HZ, 45, .45, 34, .11), (HZ + 45, 70, .75, 24, .09), (HZ + 115, H - HZ - 115, 1.15, 16, .08)]
    defs = sea_defs(T, W, H, HZ, SX, 180, 128)
    pdefs, body = sea_body(T, W, H, HZ, SX, 128, bands)
    defs += pdefs
    body += glitter(r, T, W, H, HZ, SX, 280, .56, 46)
    body += glints(r, T, H, HZ, SX, 9, .56)
    body += boat(T, SX + 80, 106, .64)
    body += gulls([("-40 60;720 46", 46, 1), ("-140 72;700 62", 58, .75)])
    body += finish(T, W, H)
    defs += (f'<linearGradient id="nm" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="240" y2="0" gradientTransform="translate(-280 0)">'
             f'<stop offset="0" stop-color="{T["name"][0]}"/><stop offset=".42" stop-color="{T["name"][0]}"/><stop offset=".5" stop-color="{T["name"][1]}"/><stop offset=".58" stop-color="{T["name"][0]}"/><stop offset="1" stop-color="{T["name"][0]}"/>'
             '<animateTransform attributeName="gradientTransform" type="translate" values="-280 0;720 0;720 0" keyTimes="0;.5;1" dur="9s" begin="1.8s" repeatCount="indefinite"/></linearGradient>'
             '<linearGradient id="rg"><stop offset=".8" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
             f'<mask id="rev" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect x="-900" y="0" width="900" height="{H}" fill="url(#rg)">'
             '<animate attributeName="x" values="-900;0" keyTimes="0;1" calcMode="spline" keySplines=".25 .6 .2 1" dur="2.6s" fill="freeze"/></rect></mask>')
    body += (f'<g mask="url(#rev)"><text x="44" y="136" font-family="{SANS}" font-weight="300" font-size="54" letter-spacing="-1" fill="url(#nm)">{name}</text>'
             f'<line x1="47" y1="161" x2="75" y2="161" stroke="{T["sub"]}" stroke-width="1"/>'
             f'<text x="86" y="165" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{T["sub"]}">{coords}</text></g>')
    check_clear("hero name", 44, text_width(name, 54, 300, -1), 136 - 40, SX, HZ, .56)
    faces = font_face(SANS, 300, name) + font_face(MONO, 400, coords, source=PLEX)
    return svg(W, H, 16, "Berke Akyıldız", faces, defs, body)


CARDS = [
    ("hotel", "Hotel Operations Agent",
     ["An AI concierge for a small hotel.", "Hotel rules run as code, and a", "manager approves what it asks for."],
     "Python · OpenAI Agents SDK · FastAPI", MORNING, 21, "boat"),
    ("experiments", "LLM Experiments",
     ["Small experiments on how agents", "behave at work, graded on the", "trace as well as the reply."],
     "Python · OpenAI · Anthropic", NOON, 34, "glints"),
    ("brain", "Second Brain OS",
     ["A memory for Claude Code and Codex", "that a person can read, correct", "and undo. Git is the database."],
     "Markdown · Git · Node · Obsidian", AFTERNOON, 55, "gulls"),
    ("digest", "AI Digest",
     ["Reads the day's AI news, merges", "the duplicates, then summarises", "and ranks it into one page."],
     "Python · LangGraph · FastAPI · HTMX", DUSK, 89, "stars"),
]


def card(slug, title, lines, stack, T, seed, motif, narrow=False):
    W, H, HZ, SX, slope = 400, 230, 26, 330, .42
    r = mulberry32(seed)
    bands = [(HZ, 40, .45, 34, .1), (HZ + 40, H - HZ - 40, .8, 22, .085)]
    defs = sea_defs(T, W, H, HZ, SX, 140, 92)
    pdefs, body = sea_body(T, W, H, HZ, SX, 92, bands)
    defs += pdefs
    body += glitter(r, T, W, H, HZ, SX, 150, slope, 22)
    if motif == "boat":
        body += boat(T, SX - 34, 66, .5)
    elif motif == "glints":
        body += glints(r, T, H, HZ, SX, 7, slope, 1.1)
    elif motif == "gulls":
        body += gulls([("-30 46;430 36", 34, .9), ("-110 56;420 50", 42, .7)])
    elif motif == "stars":
        for _ in range(9):
            body += f'<circle class="gtw" cx="{n(r() * W)}" cy="{n(3 + r() * (HZ - 9))}" r="{n(.4 + r() * .5, 2)}" fill="#fff" style="animation-duration:{n(2 + r() * 3, 2)}s;animation-delay:{n(-r() * 4, 2)}s"/>'
    body += finish(T, W, H)
    x = 28
    if narrow:
        rows, row = [], ""
        for word in title.split():
            test = (row + " " + word).strip()
            if row and text_width(test, 40, 400, -.6) > 270:
                rows.append(row)
                row = word
            else:
                row = test
        rows.append(row)
        top = 198 - 46 * (len(rows) - 1)
        for i, row in enumerate(rows):
            body += f'<text x="{x}" y="{top + i * 46}" font-family="{SANS}" font-weight="400" font-size="40" letter-spacing="-.6" fill="#ffffff">{row}</text>'
            check_clear(f"{slug} narrow row {i + 1}", x, text_width(row, 40, 400, -.6), top + i * 46 - 30, SX, HZ, slope)
        return svg(W, H, 14, title, font_face(SANS, 400, title), defs, body)
    body += f'<text x="{x}" y="104" font-family="{SANS}" font-weight="400" font-size="22" letter-spacing="-.2" fill="#ffffff">{title}</text>'
    check_clear(f"{slug} title", x, text_width(title, 22, 400, -.2), 104 - 17, SX, HZ, slope)
    for i, line in enumerate(lines):
        y = 132 + i * 19
        body += f'<text x="{x}" y="{y}" font-family="{SANS}" font-weight="400" font-size="13" fill="{T["body"]}">{line.replace(chr(39), "&#8217;")}</text>'
        check_clear(f"{slug} line {i + 1}", x, text_width(line, 13, 400), y - 10, SX, HZ, slope)
    body += f'<text x="{x}" y="204" font-family="{MONO}" font-size="10.5" letter-spacing=".4" fill="{T["sub"]}">{stack}</text>'
    text = title + "".join(lines).replace("'", "’")
    faces = font_face(SANS, 400, text) + font_face(MONO, 400, stack, source=PLEX)
    return svg(W, H, 14, f"{title}. {' '.join(lines)}", faces, defs, body)


TOOLS = ["Python", "TypeScript", "OpenAI Agents SDK", "LangGraph", "LangChain",
         "Deep Agents", "MCP", "OpenAI API", "Anthropic API", "FastAPI", "SQLAlchemy",
         "Pydantic", "PostgreSQL", "LangSmith", "pytest", "Docker", "Claude Code", "Codex"]


def stack_strip(H=54, size=15):
    W = 680
    T, r = NOON, mulberry32(144)
    sep = "   ·   "
    run = "".join(t + sep for t in TOOLS)
    w = text_width(run, size, 400)
    bands = [(0, H, .6, 26, .08)]
    defs = sea_defs(T, W, H, 0, W / 2, 0, 0)
    pdefs, body = sea_body(T, W, H, 0, W / 2, 0, bands)
    defs += pdefs
    for _ in range(30):
        body += f'<rect class="gtw" x="{n(r() * W)}" y="{n(4 + r() * (H - 8))}" width="{n(1 + r() * 3)}" height=".8" fill="#fff" fill-opacity=".3" style="animation-duration:{n(1.4 + r() * 2.6, 2)}s;animation-delay:{n(-r() * 3, 2)}s"/>'
    defs += ('<linearGradient id="fade"><stop offset="0" stop-color="#000"/><stop offset=".09" stop-color="#fff"/>'
             '<stop offset=".91" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>'
             f'<mask id="edge" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>')

    def tspans():
        return "".join(f'<tspan fill="#dbe6fb">{t}</tspan><tspan fill="#6f8fc4">{sep}</tspan>' for t in TOOLS)

    body += (f'<g mask="url(#edge)"><g class="mq" font-family="{SANS}" font-weight="400" font-size="{size}" style="font-kerning:none" xml:space="preserve">'
             f'<text x="0" y="{n(H / 2 + size * .36)}">{tspans()}</text><text x="{n(w, 2)}" y="{n(H / 2 + size * .36)}">{tspans()}</text></g></g>')
    body += f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{T["grain"]}"/>'
    faces = font_face(SANS, 400, run, kern=False)
    faces += f".mq{{animation:mq {n(w / 34)}s linear infinite}}@keyframes mq{{to{{transform:translateX(-{n(w, 2)}px)}}}}"
    return svg(W, H, 12, "Tools: " + ", ".join(TOOLS), faces, defs, body)


def shore():
    W, H = 680, 130
    T, r = NOON, mulberry32(233)
    curve = "M0 70C130 66 270 72 340 92C390 106 418 120 426 130"
    bands = [(0, 60, .6, 30, .1), (60, H - 60, .95, 18, .085)]
    defs = sea_defs(T, W, H, 0, 560, 0, 0)
    pdefs, body = sea_body(T, W, H, 0, 560, 0, bands)
    defs += pdefs
    defs += ('<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#74b940"/><stop offset=".45" stop-color="#4c9a2b"/><stop offset="1" stop-color="#2a6c1a"/></linearGradient>'
             '<linearGradient id="gust" x1="0" x2="1"><stop offset="0" stop-color="#fff4c2" stop-opacity="0"/><stop offset=".5" stop-color="#fff4c2" stop-opacity=".2"/><stop offset="1" stop-color="#fff4c2" stop-opacity="0"/></linearGradient>'
             '<filter id="haze" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="4"/></filter>'
             '<filter id="foam" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation=".7"/></filter>'
             f'<clipPath id="land"><path d="{curve}H0z"/></clipPath>')
    for _ in range(40):
        y = 4 + r() * (H - 8)
        body += f'<rect class="gtw" x="{n(r() * W)}" y="{n(y)}" width="{n(1 + r() * 3.5)}" height=".8" fill="#fff" fill-opacity=".3" style="animation-duration:{n(1.4 + r() * 2.6, 2)}s;animation-delay:{n(-r() * 3, 2)}s"/>'
    body += boat(T, 560, 50, .45)
    # Shallow water: wide blurred bands, darker away from the land, like the reference photo.
    body += (f'<path d="{curve}" fill="none" stroke="#2a8fd8" stroke-width="40" opacity=".55" filter="url(#haze)"/>'
             f'<path d="{curve}" fill="none" stroke="#3aa7e8" stroke-width="22" filter="url(#haze)"/>'
             f'<path d="{curve}" fill="none" stroke="#9adcf7" stroke-width="9" opacity=".75" filter="url(#haze)"/>'
             f'<path class="sh" d="{curve}" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.6" stroke-linecap="round" filter="url(#foam)" transform="translate(6 -6)" style="stroke-dasharray:18 11 6 14 26 9"/>')
    # Grass: a gradient field, then seeded blades in four tones, clipped to the land.
    tones = {"#9ad35e": [], "#7cc44a": [], "#3d8424": [], "#2f6f1d": []}
    keys = list(tones)
    for _ in range(1500):
        x, y = r() * 440, 60 + r() * 72
        h = 2.5 + r() * 4.5
        tones[keys[int(r() * 4)]].append(f"M{n(x)} {n(y)}l{n((r() - .5) * 1.6)} {n(-h)}")
    blades = "".join(f'<path d="{"".join(d)}" stroke="{c}" stroke-width=".7" stroke-linecap="round" opacity=".55"/>' for c, d in tones.items())
    body += (f'<g clip-path="url(#land)"><rect width="440" height="{H}" fill="url(#grass)"/>{blades}'
             f'<g class="wind"><rect width="170" height="{H + 60}" y="-30" fill="url(#gust)" transform="skewX(-22)"/></g></g>'
             f'<path d="{curve}" fill="none" stroke="#e8c97e" stroke-width="5" opacity=".35" filter="url(#foam)"/>'
             f'<path d="{curve}" fill="none" stroke="#d6b36a" stroke-width="2"/>')
    body += f'<rect width="{W}" height="{H}" filter="url(#grain)" opacity="{T["grain"]}"/>'
    return svg(W, H, 12, "A green shore meeting the sea", "", defs, body)


def main():
    ASSETS.mkdir(exist_ok=True)
    out = {"sea-hero.svg": hero(), "sea-stack.svg": stack_strip(),
           "sea-stack-narrow.svg": stack_strip(H=90, size=30), "sea-shore.svg": shore()}
    for c in CARDS:
        out[f"sea-card-{c[0]}.svg"] = card(*c)
        out[f"sea-card-{c[0]}-narrow.svg"] = card(*c, narrow=True)
    for name, data in out.items():
        (ASSETS / name).write_text(data, encoding="utf-8")
        print(f"{name:28} {len(data.encode()) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
