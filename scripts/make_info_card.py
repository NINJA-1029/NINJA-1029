"""
Build a unified neofetch-style info card + RPG Developer Level & XP System SVG
in a SINGLE terminal window container.

Top half: Original info card (Edu, Focus, Location, Stack, Tools, Projects).
Bottom half: RPG Developer Level (Level, Title, XP progress bar, Streak Buff, Activity totals).

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
PURPLE = "#a371f7"


def esc(s):
    return html.escape(str(s))


def calculate_rpg_stats():
    cur_streak = 0
    long_streak = 0
    active_days = 0
    total_xp = 0

    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
                cur_streak = d.get("current_streak", {}).get("length", 0)
                long_streak = d.get("longest_streak", {}).get("length", 0)
                active_days = d.get("active_days", 0)
                total_xp = d.get("total_contributions", 0)
        except Exception:
            pass

    # Level calculation: 100 XP per level
    level = (total_xp // 100) + 1
    xp_in_level = total_xp % 100
    next_level_xp = 100
    level_pct = round((xp_in_level / next_level_xp) * 100, 1)

    # Class Titles
    if level >= 20:
        title = "Grandmaster Architect"
    elif level >= 15:
        title = "Systems Architect"
    elif level >= 10:
        title = "Code Wizard"
    elif level >= 7:
        title = "Fullstack Adventurer"
    elif level >= 4:
        title = "Apprentice Dev"
    else:
        title = "Novice Coder"

    return {
        "cur_streak": cur_streak,
        "long_streak": long_streak,
        "active_days": active_days,
        "total_xp": total_xp,
        "level": level,
        "title": title,
        "xp_in_level": xp_in_level,
        "level_pct": level_pct,
    }


def make_svg():
    rpg = calculate_rpg_stats()
    cur_streak = rpg["cur_streak"]
    long_streak = rpg["long_streak"]
    active_days = rpg["active_days"]
    total_xp = rpg["total_xp"]
    level = rpg["level"]
    title = rpg["title"]
    xp_in_level = rpg["xp_in_level"]
    level_pct = rpg["level_pct"]

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

    H = 610

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
                 f'text-anchor="middle">ninja1029@github: ~$ neofetch --rpg</text>')

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
            title_text = esc(row[1])
            inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                     f'&#8212; {title_text}</text>'
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

    # Bottom Half: RPG Developer Stats & XP Progress
    y += 10

    # — Developer Level & XP section header
    inner_rpg_sec = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                     f'&#8212; Developer Level &amp; XP</text>'
                     f'<line x1="{KEY_X + 185}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                     f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    parts.append(f'<g>{inner_rpg_sec}</g>')
    y += 24

    # Level & Title Row
    inner_lvl = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Level</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" font-size="12.5">'
                 f'<tspan fill="{ACCENT}" font-weight="700">Level {level}</tspan> '
                 f'<tspan fill="{PURPLE}">· {title}</tspan></text>')
    parts.append(f'<g>{inner_lvl}</g>')
    y += 24

    # XP Progress Bar
    bar_total_w = 260
    filled_w = max(10, int(bar_total_w * (xp_in_level / 100.0)))
    next_level = level + 1

    inner_xp = (
        f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">XP Progress</text>'
        f'<rect x="{VAL_X}" y="{y-11:.1f}" width="{bar_total_w}" height="13" rx="3" fill="#21262d"/>'
        f'<rect x="{VAL_X}" y="{y-11:.1f}" width="{filled_w}" height="13" rx="3" fill="{GREEN}"/>'
        f'<text x="{VAL_X + bar_total_w + 14}" y="{y:.1f}" font-size="12.5">'
        f'<tspan fill="{INK}">{total_xp:,} XP</tspan> '
        f'<tspan fill="{GOLD}">({level_pct}% to Lvl {next_level})</tspan></text>'
    )
    parts.append(f'<g>{inner_xp}</g>')
    y += 24

    # Active Buff / Streak
    inner_buff = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Active Buff</text>'
                  f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">'
                  f'🔥 {cur_streak}-Day Streak (+25% XP Boost)  ·  ⚡ Record: {long_streak} days</text>')
    parts.append(f'<g>{inner_buff}</g>')
    y += 24

    # Summary
    inner_summary = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">Activity</text>'
                     f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="12.5">'
                     f'{total_xp:,} total XP earned across {active_days} active days this year</text>')
    parts.append(f'<g>{inner_summary}</g>')

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    svg = make_svg()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {OUT} ({len(svg)} bytes)")
