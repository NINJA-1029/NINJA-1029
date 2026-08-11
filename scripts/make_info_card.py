"""
Build a unified neofetch-style info card + streak & consistency meter SVG
in a SINGLE terminal window container.

Top half: Original info card (Edu, Focus, Location, Stack, Tools, Projects).
Bottom half: Streak metrics, Consistency Meter (terminal progress bar + rank), and Activity totals.

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

W = 860
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 115
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


def esc(s):
    return html.escape(str(s))


def load_stats():
    cur_streak = 0
    long_streak = 0
    active_days = 0
    total_contribs = 0
    days_count = 365

    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
                cur_streak = d.get("current_streak", {}).get("length", 0)
                long_streak = d.get("longest_streak", {}).get("length", 0)
                active_days = d.get("active_days", 0)
                total_contribs = d.get("total_contributions", 0)
                days_list = d.get("days", [])
                if days_list:
                    days_count = len(days_list)
        except Exception:
            pass

    consistency_pct = round((active_days / max(1, days_count)) * 100, 1)

    # Rank calculation
    if consistency_pct >= 85:
        rank = "S-Rank"
    elif consistency_pct >= 70:
        rank = "A-Rank"
    elif consistency_pct >= 50:
        rank = "B-Rank"
    else:
        rank = "Active"

    return {
        "cur_streak": cur_streak,
        "long_streak": long_streak,
        "active_days": active_days,
        "total_contribs": total_contribs,
        "days_count": days_count,
        "consistency_pct": consistency_pct,
        "rank": rank,
    }


def make_svg():
    stats = load_stats()
    cur_streak = stats["cur_streak"]
    long_streak = stats["long_streak"]
    active_days = stats["active_days"]
    total_contribs = stats["total_contribs"]
    consistency_pct = stats["consistency_pct"]
    rank = stats["rank"]

    # Top Half: Original Info Card Content (Untouched)
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

    H = 590

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

    # Render Top Half (Original Info Card)
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

        parts.append(f'<g>{inner}</g>')
        y += LINE_H

    # Bottom Half: Streak & Consistency Meter
    y += 10

    # — Streak & Consistency section header
    inner_streak_sec = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                        f'&#8212; Streak &amp; Consistency</text>'
                        f'<line x1="{KEY_X + 165}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                        f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    parts.append(f'<g>{inner_streak_sec}</g>')
    y += 24

    # Current streak row
    inner_cur = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Streak</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">'
                 f'🔥 {cur_streak} days current  ·  ⚡ {long_streak} days longest</text>')
    parts.append(f'<g>{inner_cur}</g>')
    y += 24

    # Consistency Meter Progress Bar
    bar_total_w = 260
    filled_w = max(10, int(bar_total_w * min(1.0, consistency_pct / 100.0)))

    inner_meter = (
        f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Consistency</text>'
        f'<rect x="{VAL_X}" y="{y-11:.1f}" width="{bar_total_w}" height="13" rx="3" fill="#21262d"/>'
        f'<rect x="{VAL_X}" y="{y-11:.1f}" width="{filled_w}" height="13" rx="3" fill="{GREEN}"/>'
        f'<text x="{VAL_X + bar_total_w + 14}" y="{y:.1f}" font-size="12.5">'
        f'<tspan fill="{ACCENT}" font-weight="700">{consistency_pct}%</tspan> '
        f'<tspan fill="{GOLD}">({rank})</tspan></text>'
    )
    parts.append(f'<g>{inner_meter}</g>')
    y += 24

    # Activity Summary
    inner_act = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Activity</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">'
                 f'{total_contribs:,} contributions across {active_days} active days this year</text>')
    parts.append(f'<g>{inner_act}</g>')

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
