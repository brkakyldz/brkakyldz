#!/usr/bin/env python3
"""Draw the last year of GitHub contributions as light on the sea.

    GITHUB_TOKEN=... python scripts/activity.py --user brkakyldz --out dist

Run daily by .github/workflows/activity.yml, which publishes the result to the
`output` branch. Each day is one mark: a quiet day is a faint point, and a busy
day is a longer, brighter glint. A slow band of light moves across the weeks.

Standard library only. `--sample` draws made-up data, for checking the layout
without a token; the workflow never uses it.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import pathlib
import random
import sys
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
FONT = HERE / "plex-mono-ascii.woff2"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

# The portfolio's sea, and the light on it.
SEA_TOP, SEA, SEA_LOW = "#24496f", "#1c3d63", "#132b47"
INK, MUTED, WARM = "#ece5d7", "#a9b9c6", "#f6e3bf"


def fetch(user: str, token: str) -> tuple[int, list[list[dict]]]:
    body = json.dumps({"query": QUERY, "variables": {"login": user}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": user},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise SystemExit(f"GraphQL error: {data['errors']}")
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [
        [{"date": d["date"], "count": d["contributionCount"], "level": LEVEL[d["contributionLevel"]]} for d in w["contributionDays"]]
        for w in cal["weeks"]
    ]
    return cal["totalContributions"], weeks


def sample() -> tuple[int, list[list[dict]]]:
    rng = random.Random(4)
    end = dt.date.today()
    start = end - dt.timedelta(days=364 + (end.weekday() + 1) % 7)
    weeks, week, total = [], [], 0
    day = start
    while day <= end:
        busy = 0.15 if day < end - dt.timedelta(days=150) else 0.75
        count = 0 if rng.random() > busy else rng.choice([1, 2, 3, 5, 8, 13, 21])
        total += count
        level = 0 if count == 0 else 1 if count < 3 else 2 if count < 6 else 3 if count < 12 else 4
        week.append({"date": day.isoformat(), "count": count, "level": level})
        if len(week) == 7:
            weeks.append(week)
            week = []
        day += dt.timedelta(days=1)
    if week:
        weeks.append(week)
    return total, weeks


def render(total: int, weeks: list[list[dict]], today: dt.date) -> str:
    W, H = 960, 236
    pitch_x, pitch_y = 16, 14
    cols = len(weeks)
    x0 = (W - cols * pitch_x) / 2 + pitch_x / 2
    y0 = 92
    period = 9.0  # seconds for the band of light to cross the year

    font = base64.b64encode(FONT.read_bytes()).decode()
    marks = []
    months = []
    seen_month = None
    for c, week in enumerate(weeks):
        x = x0 + c * pitch_x
        first = dt.date.fromisoformat(week[0]["date"])
        if first.month != seen_month and first.day <= 7 and c < cols - 1:
            months.append(f'<text class="m" x="{x - 4:.1f}" y="{y0 + 7 * pitch_y + 14}">{first.strftime("%b")}</text>')
            seen_month = first.month
        elif seen_month is None:
            seen_month = first.month
        cells = []
        for day in week:
            d = dt.date.fromisoformat(day["date"])
            row = (d.weekday() + 1) % 7  # Sunday on top, as on GitHub
            y = y0 + row * pitch_y
            lv = day["level"]
            title = f'<title>{day["date"]}: {day["count"]} contribution{"" if day["count"] == 1 else "s"}</title>'
            if lv == 0:
                cells.append(f'<circle cx="{x:.1f}" cy="{y}" r="1" class="q">{title}</circle>')
            else:
                w = (4, 7, 10, 13)[lv - 1]
                h = (1.5, 1.7, 1.9, 2.1)[lv - 1]
                cells.append(
                    f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.2f}" width="{w}" height="{h}" rx="{h / 2:.2f}" class="l{lv}">{title}</rect>'
                )
        delay = c / cols * period - period
        marks.append(f'<g class="w" style="animation-delay:{delay:.2f}s">{"".join(cells)}</g>')

    total_text = f"{total:,} contributions in the last year"
    stamp = f"redrawn {today.isoformat()}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total_text}, drawn as light on the sea.">
<title>{total_text}</title>
<style>
@font-face{{font-family:'Plex Mono';src:url(data:font/woff2;base64,{font}) format('woff2')}}
text{{font-family:'Plex Mono',ui-monospace,Consolas,monospace}}
.t{{font-size:13px;fill:{INK};letter-spacing:.15px}}
.s{{font-size:11.5px;fill:{MUTED}}}
.m{{font-size:11px;fill:{MUTED}}}
.q{{fill:{INK};opacity:.2}}
.l1{{fill:{INK};opacity:.42}}
.l2{{fill:{INK};opacity:.62}}
.l3{{fill:{INK};opacity:.82}}
.l4{{fill:{WARM}}}
.w{{opacity:.62;animation:light {period}s ease-in-out infinite}}
@keyframes light{{0%,100%{{opacity:.62}}12%{{opacity:1}}26%{{opacity:.62}}}}
@media (prefers-reduced-motion: reduce){{.w{{animation:none;opacity:.9}}}}
</style>
<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SEA_TOP}"/><stop offset=".4" stop-color="{SEA}"/><stop offset="1" stop-color="{SEA_LOW}"/></linearGradient>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="url(#sea)"/>
<text class="t" x="{x0 - 4:.1f}" y="50">{total_text}</text>
<text class="s" x="{W - x0 + 4:.1f}" y="50" text-anchor="end">{stamp}</text>
{"".join(marks)}
{"".join(months)}
</g>
</svg>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="brkakyldz")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--sample", action="store_true", help="draw made-up data (layout check only)")
    args = ap.parse_args()

    if args.sample:
        total, weeks = sample()
    else:
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            sys.exit("GITHUB_TOKEN is not set")
        total, weeks = fetch(args.user, token)

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "activity.svg").write_text(render(total, weeks, dt.date.today()))
    print(f"{out / 'activity.svg'}: {total} contributions, {len(weeks)} weeks")


if __name__ == "__main__":
    main()
