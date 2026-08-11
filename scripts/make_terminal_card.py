"""
Build the terminal-style streak & contribution graph card SVG matching the user design.
Reads REAL live GitHub contribution data from data/contributions.json
(updated automatically via GitHub Actions).
"""
import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_SVG = os.path.join(HERE, "..", "github-terminal.svg")

WIDTH, HEIGHT = 860, 440
USERNAME = "ninja1029"

WEEKS, DAYS = 32, 7

BG = "#0d1117"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#7d8590"
GREEN = "#3fb950"
ORANGE = "#ffa657"
BLUE = "#58a6ff"
CYAN = "#22d3ee"

LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def level_for(count):
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    return 4


def esc(v):
    return html.escape(str(v))


def load_data():
    cur_streak = 0
    long_streak = 0
    active_days = 0
    total_contribs = 0
    days_list = []

    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
                cur_streak = d.get("current_streak", {}).get("length", 0)
                long_streak = d.get("longest_streak", {}).get("length", 0)
                active_days = d.get("active_days", 0)
                total_contribs = d.get("total_contributions", 0)
                days_list = d.get("days", [])
        except Exception:
            pass

    # Build 7-row x 32-column matrix for recent weeks
    # Pad or slice to WEEKS * DAYS
    needed_days = WEEKS * DAYS
    recent_days = days_list[-needed_days:] if len(days_list) >= needed_days else days_list

    # Initialize 7 x 32 grid with level 0
    grid = [[0 for _ in range(WEEKS)] for _ in range(DAYS)]
    months_labels = {}

    if recent_days:
        first_date = datetime.date.fromisoformat(recent_days[0]["date"])
        # Calculate starting day of week (Sunday=0)
        start_dow = (first_date.weekday() + 1) % 7

        idx = 0
        for w in range(WEEKS):
            for d in range(DAYS):
                if w == 0 and d < start_dow:
                    continue
                if idx < len(recent_days):
                    item = recent_days[idx]
                    cnt = item["count"]
                    grid[d][w] = level_for(cnt)
                    # Month label detection
                    dt = datetime.date.fromisoformat(item["date"])
                    if dt.day <= 7 and w not in months_labels:
                        months_labels[w] = dt.strftime("%b").upper()
                    idx += 1

    return {
        "cur_streak": cur_streak,
        "long_streak": long_streak,
        "active_days": active_days,
        "total_contribs": total_contribs,
        "grid": grid,
        "months": months_labels,
    }


def make_svg():
    data = load_data()
    cur_streak = data["cur_streak"]
    long_streak = data["long_streak"]
    active_days = data["active_days"]
    total_contribs = data["total_contribs"]
    grid = data["grid"]
    months = data["months"]

    activity = [
        ("Total Contributions", f"{total_contribs:,}"),
        ("Active Days", f"{active_days} days this year"),
        ("Current Streak", f"🔥 {cur_streak} days"),
        ("Longest Streak", f"⚡ {long_streak} days"),
    ]

    s = [f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"
font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#111722"/>
    <stop offset="1" stop-color="#0d1117"/>
  </linearGradient>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="12" fill="url(#bg)"/>
<rect x=".5" y=".5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="12"
      fill="none" stroke="{BORDER}"/>
<line x1="0" y1="30" x2="{WIDTH}" y2="30" stroke="{BORDER}"/>
<circle cx="20" cy="15" r="5" fill="#ff5f56"/>
<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>
<circle cx="52" cy="15" r="5" fill="#27c93f"/>
<text x="430" y="19" fill="{MUTED}" font-size="12" text-anchor="middle">
  {USERNAME}@github: ~$ streak --activity
</text>

<text x="20" y="60" fill="{GREEN}" font-size="14" font-weight="700">{USERNAME}</text>
<text x="102" y="60" fill="{MUTED}" font-size="14">@</text>
<text x="112" y="60" fill="{CYAN}" font-size="14" font-weight="700">github</text>
<line x1="170" y1="56" x2="840" y2="56" stroke="{BORDER}" stroke-opacity=".8"/>

<text x="20" y="88" fill="{BLUE}" font-size="12.5" font-weight="700">— Streak</text>
<line x1="78" y1="84" x2="840" y2="84" stroke="{BORDER}" stroke-opacity=".8"/>

<text x="20" y="112" fill="{ORANGE}" font-size="12.5" font-weight="700">Current</text>
<text x="112" y="112" fill="{TEXT}" font-size="12.5">{cur_streak} days</text>

<text x="20" y="134" fill="{ORANGE}" font-size="12.5" font-weight="700">Longest</text>
<text x="112" y="134" fill="{TEXT}" font-size="12.5">{long_streak} days</text>

<text x="20" y="156" fill="{ORANGE}" font-size="12.5" font-weight="700">Active</text>
<text x="112" y="156" fill="{TEXT}" font-size="12.5">{active_days} days this year</text>
''']

    # Streak bar calculation
    bar_width = int(180 * min(1.0, cur_streak / max(1, long_streak)))
    s.append(f'''<rect x="270" y="101" width="180" height="13" rx="2" fill="#21262d"/>
<rect x="270" y="101" width="{bar_width}" height="13" rx="2" fill="{GREEN}"/>

<text x="20" y="184" fill="{BLUE}" font-size="12.5" font-weight="700">— Contributions</text>
<line x1="112" y1="180" x2="840" y2="180" stroke="{BORDER}" stroke-opacity=".8"/>
<text x="112" y="203" fill="{MUTED}" font-size="9">RECENT ACTIVITY</text>
''')

    cell, gap = 10, 3
    sx, sy = 112, 214

    for week, month in months.items():
        x = sx + week * (cell + gap)
        s.append(f'<text x="{x}" y="211" fill="{MUTED}" font-size="8">{month}</text>')

    for day, label in {1: "M", 3: "W", 5: "F"}.items():
        y = sy + day * (cell + gap) + 8
        s.append(f'<text x="97" y="{y}" fill="{MUTED}" font-size="8">{label}</text>')

    for day in range(DAYS):
        for week in range(WEEKS):
            x = sx + week * (cell + gap)
            y = sy + day * (cell + gap)
            lvl = grid[day][week]
            s.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'rx="2" fill="{LEVELS[lvl]}"/>'
            )

    s.append(f'''<text x="112" y="302" fill="{MUTED}" font-size="9">Less</text>''')

    for i, color in enumerate(LEVELS):
        x = 142 + i * 15
        s.append(f'<rect x="{x}" y="293" width="10" height="10" rx="2" fill="{color}"/>')

    s.append(f'''<text x="220" y="302" fill="{MUTED}" font-size="9">More</text>

<text x="20" y="328" fill="{BLUE}" font-size="12.5" font-weight="700">— Activity</text>
<line x1="92" y1="324" x2="840" y2="324" stroke="{BORDER}" stroke-opacity=".8"/>
''')

    y_pos = 351
    for label, value in activity[:2]:
        s.append(
            f'<text x="20" y="{y_pos}" fill="{ORANGE}" font-size="12.5" font-weight="700">{esc(label)}</text>'
        )
        s.append(
            f'<text x="170" y="{y_pos}" fill="{TEXT}" font-size="12.5">{esc(value)}</text>'
        )
        y_pos += 22

    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    svg_content = make_svg()
    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"wrote {OUT_SVG} ({len(svg_content)} bytes)")
