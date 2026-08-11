"""
Build a unified neofetch-style info card + streak & contribution graph SVG
in a SINGLE terminal window container.

Top half: Original info card (Edu, Focus, Location, Stack, Tools, Projects).
Bottom half: Streak metrics, 32-week contribution heatmap grid, and activity totals.

Reads real GitHub contribution data from data/contributions.json.
Runs daily via .github/workflows/update-profile-art.yml.
"""
import datetime
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
DATA_PATH = os.path.join(HERE, "..", "data", "contributions.json")
STATIC = bool(os.environ.get("STATIC"))

W = 860
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"      # orange keys
SECTION = "#58a6ff"  # blue section headers
GREEN = "#3fb950"
ACCENT = "#22d3ee"
GOLD = "#f2cc60"

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


def esc(s):
    return html.escape(str(s))


def load_contributions():
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

    WEEKS, DAYS = 32, 7
    needed_days = WEEKS * DAYS
    recent_days = days_list[-needed_days:] if len(days_list) >= needed_days else days_list

    grid = [[0 for _ in range(WEEKS)] for _ in range(DAYS)]
    months_labels = {}

    if recent_days:
        first_date = datetime.date.fromisoformat(recent_days[0]["date"])
        start_dow = (first_date.weekday() + 1) % 7

        idx = 0
        for w in range(WEEKS):
            for d in range(DAYS):
                if w == 0 and d < start_dow:
                    continue
                if idx < len(recent_days):
                    item = recent_days[idx]
                    grid[d][w] = level_for(item["count"])
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


def rise(inner, delay):
    if STATIC:
        return f"<g>{inner}</g>"
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


def make_svg():
    cdata = load_contributions()
    cur_streak = cdata["cur_streak"]
    long_streak = cdata["long_streak"]
    active_days = cdata["active_days"]
    total_contribs = cdata["total_contribs"]
    grid = cdata["grid"]
    months = cdata["months"]

    # Top Half: Original Info Card Content
    TOP_ROWS = [
        ("host",),
        ("kv", "Edu", "B.Tech CSE, VIT Chennai '28"),
        ("kv", "Focus", "Fullstack & Blockchain Dev"),
        ("kv", "Location", "Chennai, India"),
        ("gap",),
        ("sec", "Stack"),
        ("kv", "Languages", "C, C++, JavaScript, TS, Python, Java, Solidity, HTML, CSS"),
        ("kv", "Web Dev", "React.js, Node.js, Express.js, Tailwind, Firebase"),
        ("kv", "Database", "PostgreSQL, MongoDB, Supabase, MySQL"),
        ("kv", "Web3", "Solidity, Ethers.js, Hardhat"),
        ("gap",),
        ("sec", "Tools"),
        ("kv", "DevOps/VC", "Git, GitHub, Docker, Postman, Linux"),
        ("gap",),
        ("sec", "Projects"),
        ("bul", "Autom8: AI automata learning platform"),
        ("bul", "Decvosys: Decentralized voting platform"),
        ("bul", "Landroid: AI AgriTech IoT app"),
        ("bul", "SnapFit: AI size recommender platform"),
    ]

    H = 715

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>',
        f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]

    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">ninja1029@github: ~$ neofetch</text>')

    y = TITLEBAR_H + 30
    row_idx = 0

    # Render Top Half
    for row in TOP_ROWS:
        kind = row[0]
        if kind == "gap":
            y += LINE_H * 0.5
            continue
        if kind == "host":
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                     f'<tspan fill="{GREEN}">ninja1029</tspan><tspan fill="{MUTED}">@</tspan>'
                     f'<tspan fill="{ACCENT}">github</tspan></text>'
                     f'<line x1="{KEY_X+150}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                     f'stroke="{FRAME}" stroke-opacity="0.8"/>')
        elif kind == "sec":
            title = esc(row[1])
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                     f'&#8212; {title}</text>'
                     f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                     f'stroke="{FRAME}" stroke-opacity="0.8"/>')
        elif kind == "kv":
            key, val = esc(row[1]), esc(row[2])
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                     f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{val}</text>')
        elif kind == "bul":
            txt = esc(row[1])
            inner = (f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                     f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
        else:
            continue

        parts.append(rise(inner, 0.10 + row_idx * 0.04))
        row_idx += 1
        y += LINE_H

    # Bottom Half: Streak & Contributions Section (Seamless continuation!)
    y += 8
    # — Streak section
    inner_streak_sec = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                        f'&#8212; Streak</text>'
                        f'<line x1="{KEY_X + 70}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                        f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    parts.append(rise(inner_streak_sec, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 24

    # Current streak row + progress bar
    bar_w = int(180 * min(1.0, cur_streak / max(1, long_streak)))
    inner_cur = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Current</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{cur_streak} days</text>'
                 f'<rect x="270" y="{y-11:.1f}" width="180" height="13" rx="2" fill="#21262d"/>'
                 f'<rect x="270" y="{y-11:.1f}" width="{bar_w}" height="13" rx="2" fill="{GREEN}"/>')
    parts.append(rise(inner_cur, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 22

    # Longest streak
    inner_long = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Longest</text>'
                  f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{long_streak} days</text>')
    parts.append(rise(inner_long, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 22

    # Active days
    inner_act = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Active</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">{active_days} days this year</text>')
    parts.append(rise(inner_act, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 28

    # — Contributions section
    inner_contrib_sec = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                         f'&#8212; Contributions</text>'
                         f'<line x1="{KEY_X + 115}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                         f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    parts.append(rise(inner_contrib_sec, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 18

    # Heatmap Grid
    cell, gap = 10, 3
    sx, sy = VAL_X, y + 10

    heatmap_parts = [f'<text x="{VAL_X}" y="{y+4}" fill="{MUTED}" font-size="9">RECENT ACTIVITY</text>']

    for week, month in months.items():
        mx = sx + week * (cell + gap)
        heatmap_parts.append(f'<text x="{mx}" y="{sy - 3}" fill="{MUTED}" font-size="8">{month}</text>')

    for day_i, label in {1: "M", 3: "W", 5: "F"}.items():
        dy = sy + day_i * (cell + gap) + 8
        heatmap_parts.append(f'<text x="{VAL_X - 15}" y="{dy}" fill="{MUTED}" font-size="8">{label}</text>')

    for d in range(7):
        for w in range(32):
            cx = sx + w * (cell + gap)
            cy = sy + d * (cell + gap)
            lvl = grid[d][w]
            heatmap_parts.append(f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" '
                                 f'rx="2" fill="{LEVELS[lvl]}"/>')

    leg_y = sy + 7 * (cell + gap) + 6
    heatmap_parts.append(f'<text x="{VAL_X}" y="{leg_y + 8}" fill="{MUTED}" font-size="9">Less</text>')
    for i, color in enumerate(LEVELS):
        lx = VAL_X + 30 + i * 15
        heatmap_parts.append(f'<rect x="{lx}" y="{leg_y}" width="10" height="10" rx="2" fill="{color}"/>')
    heatmap_parts.append(f'<text x="{VAL_X + 110}" y="{leg_y + 8}" fill="{MUTED}" font-size="9">More</text>')

    parts.append(rise("".join(heatmap_parts), 0.10 + row_idx * 0.04))
    row_idx += 1
    y = leg_y + 32

    # — Activity Totals section
    inner_act_tot = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                     f'&#8212; Activity</text>'
                     f'<line x1="{KEY_X + 80}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                     f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    parts.append(rise(inner_act_tot, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 22

    inner_tot = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Total Contribs</text>'
                 f'<text x="{VAL_X + 40}" y="{y:.1f}" fill="{INK}" font-size="12.5">{total_contribs:,}</text>')
    parts.append(rise(inner_tot, 0.10 + row_idx * 0.04))
    row_idx += 1
    y += 22

    inner_act_d = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Active Days</text>'
                   f'<text x="{VAL_X + 40}" y="{y:.1f}" fill="{INK}" font-size="12.5">{active_days} days this year</text>')
    parts.append(rise(inner_act_d, 0.10 + row_idx * 0.04))

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
