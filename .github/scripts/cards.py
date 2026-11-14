#!/usr/bin/env python3
"""Генератор неоновых SVG-карточек для profile README.

Данные берутся из GitHub API, картинки кладутся в assets/.
Запуск: GITHUB_TOKEN=... python .github/scripts/cards.py
"""

import datetime
import html
import json
import math
import os
import pathlib
import urllib.request

LOGIN = os.environ.get("GH_LOGIN", "Bugulmekas")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

W = 1000
BG = "#0D1117"
PANEL = "#0B1120"
PANEL2 = "#0E1626"
BORDER = "#1C2B45"
CYAN = "#00F5FF"
MAGENTA = "#FF2BD6"
VIOLET = "#7A5CFF"
TEXT = "#E7F2FF"
MUTED = "#7C8DA6"
FONT = "'Cascadia Code','JetBrains Mono',Consolas,'Courier New',monospace"

PROJECTS = [
    {
        "repo": "zapret-gui",
        "index": "01",
        "accent": CYAN,
        "title": "zapret-gui",
        "desc": "GUI-управлятор zapret: служба, стратегии, IPSet, тест стратегий и автообновление.",
    },
    {
        "repo": "Lavka_helper",
        "index": "02",
        "accent": VIOLET,
        "title": "Lavka_helper",
        "desc": "Lavka Helper — удобное приложение для курьеров Яндекс Лавки.",
    },
    {
        "repo": "LoveApp",
        "index": "03",
        "accent": MAGENTA,
        "title": "LoveApp",
        "desc": "Поздравление с 8 марта или 14 февраля — маленькое приложение с большим смыслом.",
    },
    {
        "repo": "dpi-bypass",
        "index": "04",
        "accent": CYAN,
        "title": "dpi-bypass",
        "desc": "Android-обход DPI без root: VpnService + локальный SOCKS5 ByeDPI, стратегии split и disorder.",
    },
]

LANG_LABEL = {
    "PowerShell": "POWERSHELL",
    "C++": "C++",
    "Java": "JAVA",
    "C#": "C#",
    "Python": "PYTHON",
    "Kotlin": "KOTLIN",
    "JavaScript": "JAVASCRIPT",
    "HTML": "HTML",
    "CSS": "CSS",
}

STACK = ["PowerShell", "C++", "Java", "Kotlin", "Android", "WinForms", "Windows", "Git", "GitHub", "Photoshop"]


# ---------------------------------------------------------------- api

def api(path):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-cards",
            **({"Authorization": "Bearer " + TOKEN} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def graphql(query, variables):
    data = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Content-Type": "application/json",
            "User-Agent": "profile-cards",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.loads(r.read().decode("utf-8"))
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def collect():
    user = api(f"/users/{LOGIN}")
    repos = api(f"/users/{LOGIN}/repos?per_page=100&sort=updated")
    stars = sum(r["stargazers_count"] for r in repos)

    langs = {}
    for r in repos:
        if r.get("fork"):
            continue
        try:
            for name, size in api(f"/repos/{LOGIN}/{r['name']}/languages").items():
                langs[name] = langs.get(name, 0) + size
        except Exception:
            pass

    stats = {"repos": user["public_repos"], "followers": user["followers"], "stars": stars, "commits": 0}
    days = []
    weeks = []
    if TOKEN:
        q = """
        query($login:String!, $from:DateTime!, $to:DateTime!) {
          user(login:$login) {
            contributionsCollection(from:$from, to:$to) {
              totalCommitContributions
              contributionCalendar { weeks { contributionDays { date contributionCount } } }
            }
          }
        }
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        data = graphql(q, {
            "login": LOGIN,
            "from": (now - datetime.timedelta(days=365)).isoformat(),
            "to": now.isoformat(),
        })
        cc = data["user"]["contributionsCollection"]
        for week in cc["contributionCalendar"]["weeks"]:
            col = []
            for d in week["contributionDays"]:
                col.append(d["contributionCount"])
                days.append(d["contributionCount"])
            weeks.append(col)
        stats["commits"] = sum(days) or cc["totalCommitContributions"]

    return {"stats": stats, "langs": langs, "days": days, "weeks": weeks, "repos": repos}


# ---------------------------------------------------------------- svg helpers

def esc(s):
    return html.escape(str(s), quote=True)


def defs(extra=""):
    return f"""
  <defs>
    <linearGradient id="neon" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CYAN}"/>
      <stop offset="55%" stop-color="{VIOLET}"/>
      <stop offset="100%" stop-color="{MAGENTA}"/>
    </linearGradient>
    <linearGradient id="neonV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{MAGENTA}" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{PANEL2}"/>
      <stop offset="100%" stop-color="{PANEL}"/>
    </linearGradient>
    <radialGradient id="haloC">
      <stop offset="0%" stop-color="{CYAN}" stop-opacity="0.20"/>
      <stop offset="60%" stop-color="{CYAN}" stop-opacity="0.06"/>
      <stop offset="100%" stop-color="{CYAN}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="haloM">
      <stop offset="0%" stop-color="{MAGENTA}" stop-opacity="0.18"/>
      <stop offset="60%" stop-color="{MAGENTA}" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="{MAGENTA}" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{BORDER}" stroke-width="1" stroke-opacity="0.55"/>
    </pattern>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="2.4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {extra}
  </defs>"""


def header_svg(stats):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="300" viewBox="0 0 {W} 300" role="img" aria-label="Bugulmek">
{defs()}
  <rect width="{W}" height="300" fill="{BG}"/>
  <rect width="{W}" height="300" fill="url(#grid)" opacity="0.35"/>
  <ellipse cx="290" cy="150" rx="360" ry="170" fill="url(#haloC)"/>
  <ellipse cx="740" cy="110" rx="320" ry="160" fill="url(#haloM)"/>

  <rect x="12.5" y="12.5" width="{W-25}" height="275" rx="18" fill="none" stroke="{BORDER}"/>
  <path d="M12 60V24a12 12 0 0 1 12-12h48" fill="none" stroke="{CYAN}" stroke-width="2.5" filter="url(#soft)"/>
  <path d="M{W-12} 60V24a12 12 0 0 0-12-12h-48" fill="none" stroke="{MAGENTA}" stroke-width="2.5" filter="url(#soft)"/>
  <path d="M12 240v36a12 12 0 0 0 12 12h48" fill="none" stroke="{VIOLET}" stroke-width="2.5" opacity="0.8"/>
  <path d="M{W-12} 240v36a12 12 0 0 1-12 12h-48" fill="none" stroke="{VIOLET}" stroke-width="2.5" opacity="0.8"/>

  <g font-family="{FONT}">
    <text x="56" y="86" fill="{CYAN}" font-size="13" letter-spacing="5" opacity="0.9">// CYBER PROFILE v2.0</text>

    <g filter="url(#glow)">
      <text x="54" y="164" fill="{MAGENTA}" opacity="0.5" font-size="72" font-weight="700" letter-spacing="4">BUGULMEK</text>
      <text x="60" y="164" fill="{CYAN}" opacity="0.5" font-size="72" font-weight="700" letter-spacing="4">BUGULMEK</text>
      <text x="57" y="164" fill="{TEXT}" font-size="72" font-weight="700" letter-spacing="4">BUGULMEK</text>
    </g>

    <text x="58" y="199" fill="{MUTED}" font-size="17" letter-spacing="2">powershell · c++ · java · kotlin · android</text>

    <g opacity="0.95">
      <rect x="648" y="64" width="300" height="150" rx="12" fill="{PANEL}" stroke="{BORDER}"/>
      <circle cx="668" cy="84" r="4" fill="{MAGENTA}"/>
      <circle cx="682" cy="84" r="4" fill="{VIOLET}"/>
      <circle cx="696" cy="84" r="4" fill="{CYAN}"/>
      <line x1="648" y1="98" x2="948" y2="98" stroke="{BORDER}"/>
      <text x="668" y="122" fill="{CYAN}" font-size="13">$ whoami</text>
      <text x="668" y="144" fill="{TEXT}" font-size="13">Bugulmek</text>
      <text x="668" y="168" fill="{CYAN}" font-size="13">$ status</text>
      <circle cx="674" cy="186" r="4" fill="{CYAN}" filter="url(#soft)">
        <animate attributeName="opacity" values="1;0.25;1" dur="2.2s" repeatCount="indefinite"/>
      </circle>
      <text x="688" y="191" fill="{TEXT}" font-size="13">online · {stats['repos']} repos</text>
    </g>

    <g clip-path="url(#tick)">
      <text x="0" y="271" fill="{MUTED}" font-size="12" letter-spacing="3" opacity="0.85">
        ✦ НЕОН ВКЛЮЧЁН ✦ POWERSHELL ✦ C++ ✦ JAVA ✦ GUI ДЛЯ ZAPRET ✦ НЕОН ВКЛЮЧЁН ✦ POWERSHELL ✦ C++ ✦ JAVA ✦ GUI ДЛЯ ZAPRET
        <animate attributeName="x" from="1000" to="-980" dur="26s" repeatCount="indefinite"/>
      </text>
    </g>
  </g>
  <clipPath id="tick"><rect x="16" y="252" width="{W-32}" height="24"/></clipPath>
</svg>
"""


def divider_svg():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="26" viewBox="0 0 {W} 26">
{defs()}
  <rect width="{W}" height="26" fill="{BG}"/>
  <line x1="0" y1="13" x2="440" y2="13" stroke="url(#neon)" stroke-width="1.5" opacity="0.55"/>
  <line x1="560" y1="13" x2="{W}" y2="13" stroke="url(#neon)" stroke-width="1.5" opacity="0.55"/>
  <path d="M500 5l8 8-8 8-8-8z" fill="{BG}" stroke="{CYAN}" stroke-width="1.6" filter="url(#soft)"/>
  <circle cx="440" cy="13" r="2" fill="{MAGENTA}"/>
  <circle cx="560" cy="13" r="2" fill="{MAGENTA}"/>
</svg>
"""


def stack_svg():
    per_row = 5
    gap = 12
    row_h = 48
    top = 40
    rows = [STACK[i:i + per_row] for i in range(0, len(STACK), per_row)]
    pills = []
    for r, names in enumerate(rows):
        widths = [26 + len(name) * 10.6 for name in names]
        x = 28
        y = top + r * row_h
        for name, w in zip(names, widths):
            pills.append(
                f'<g><rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="38" rx="19" '
                f'fill="{PANEL}" stroke="{BORDER}"/>'
                f'<rect x="{x:.0f}" y="{y}" width="26" height="38" rx="19" fill="{CYAN}" opacity="0.10"/>'
                f'<text x="{x + 14:.0f}" y="{y + 25}" fill="{CYAN}" font-size="13">▹</text>'
                f'<text x="{x + 30:.0f}" y="{y + 25}" fill="{TEXT}" font-size="14" letter-spacing="1">{esc(name)}</text></g>'
            )
            x += w + gap
    panel_h = top + row_h * (len(rows) - 1) + 38 + 14
    height = panel_h + 12
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}">
{defs()}
  <rect width="{W}" height="{height}" fill="{BG}"/>
  <rect x="0.5" y="12.5" width="{W-1}" height="{panel_h - 12}" rx="14" fill="url(#panel)" stroke="{BORDER}"/>
  <text x="28" y="30" fill="{MUTED}" font-size="11" letter-spacing="4">СТЕК</text>
  {''.join(pills)}
</svg>
"""


def stats_svg(stats):
    items = [
        ("REPOS", stats["repos"], CYAN, "публичных"),
        ("COMMITS", stats["commits"], MAGENTA, "за год"),
        ("STARS", stats["stars"], VIOLET, "набрано"),
        ("FOLLOWERS", stats["followers"], CYAN, "подписчиков"),
    ]
    cells = []
    for i, (label, value, accent, caption) in enumerate(items):
        x = 16 + i * 247
        cells.append(f"""
    <g>
      <rect x="{x}" y="16" width="230" height="128" rx="12" fill="url(#panel)" stroke="{BORDER}"/>
      <path d="M{x + 16} 16H{x + 78}" stroke="{accent}" stroke-width="2.5" filter="url(#soft)"/>
      <text x="{x + 18}" y="46" fill="{MUTED}" font-size="11" letter-spacing="4">{label}</text>
      <text x="{x + 18}" y="98" fill="{TEXT}" font-size="46" font-weight="700" filter="url(#glow)">{value}</text>
      <text x="{x + 18}" y="124" fill="{accent}" font-size="11" letter-spacing="2" opacity="0.85">{caption}</text>
    </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="160" viewBox="0 0 {W} 160">
{defs()}
  <rect width="{W}" height="160" fill="{BG}"/>
  {''.join(cells)}
</svg>
"""


def langs_svg(langs):
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)[:5]
    rows = []
    for i, (name, size) in enumerate(top):
        pct = size / total * 100
        y = 58 + i * 34
        rows.append(f"""
    <g font-family="{FONT}">
      <text x="28" y="{y + 4}" fill="{TEXT}" font-size="14" letter-spacing="1">{esc(LANG_LABEL.get(name, name.upper()))}</text>
      <rect x="196" y="{y - 9}" width="700" height="12" rx="6" fill="{PANEL2}" stroke="{BORDER}"/>
      <rect x="196" y="{y - 9}" width="{max(6, 700 * pct / 100):.0f}" height="12" rx="6" fill="url(#neon)" filter="url(#soft)"/>
      <text x="920" y="{y + 4}" fill="{CYAN}" font-size="13" text-anchor="end">{pct:.0f}%</text>
    </g>""")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="224" viewBox="0 0 {W} 224">
{defs()}
  <rect width="{W}" height="224" fill="{BG}"/>
  <rect x="0.5" y="12.5" width="{W-1}" height="200" rx="14" fill="url(#panel)" stroke="{BORDER}"/>
  <text x="28" y="42" fill="{MUTED}" font-size="11" letter-spacing="4">ЯЗЫКИ · ПО ОБЪЁМУ КОДА</text>
  {''.join(rows)}
</svg>
"""


def activity_svg(weeks):
    cell, gap = 13, 4
    pitch = cell + gap
    grid_w = max(len(weeks), 1) * pitch
    x0 = (W - grid_w) / 2 + gap / 2
    y0 = 66
    total = sum(sum(col) for col in weeks)
    ramp = ["#0F1728", "#2A1B5E", "#5B21B6", "#A21CAF", MAGENTA]
    cells = []
    for wi, col in enumerate(weeks):
        for di, count in enumerate(col):
            if count == 0:
                level = 0
            elif count <= 1:
                level = 1
            elif count <= 3:
                level = 2
            elif count <= 6:
                level = 3
            else:
                level = 4
            x = x0 + wi * pitch
            y = y0 + di * pitch
            stroke = f' stroke="{BORDER}"' if level == 0 else ""
            cells.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="3" '
                f'fill="{ramp[level]}"{stroke}/>'
            )

    legend_w = 62 + 5 * (cell + 6) + 66
    legend_x = W - 30 - legend_w
    legend = "".join(
        f'<rect x="{legend_x + 62 + i * (cell + 6):.1f}" y="207" width="{cell}" height="{cell}" rx="3" '
        f'fill="{ramp[i]}"' + (f' stroke="{BORDER}"' if i == 0 else "") + "/>"
        for i in range(5)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="238" viewBox="0 0 {W} 238">
{defs()}
  <rect width="{W}" height="238" fill="{BG}"/>
  <rect x="0.5" y="12.5" width="{W-1}" height="212" rx="14" fill="url(#panel)" stroke="{BORDER}"/>
  <text x="28" y="42" fill="{MUTED}" font-size="11" letter-spacing="4">АКТИВНОСТЬ · 365 ДНЕЙ</text>
  <text x="972" y="42" fill="{MAGENTA}" font-size="12" text-anchor="end" letter-spacing="1">Σ {total} commits</text>
  {''.join(cells)}
  <g font-family="{FONT}">
    <text x="{legend_x:.0f}" y="218" fill="{MUTED}" font-size="10" letter-spacing="2">МЕНЬШЕ</text>
    {legend}
    <text x="{legend_x + 62 + 5 * (cell + 6) + 4:.0f}" y="218" fill="{MUTED}" font-size="10" letter-spacing="2">БОЛЬШЕ</text>
  </g>
</svg>
"""


def project_svg(p, repo_info):
    accent = p["accent"]
    desc = p["desc"]
    words, lines, line = desc.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 <= 38:
            line = (line + " " + w).strip()
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    lines = lines[:3]
    text_lines = "".join(
        f'<text x="26" y="{132 + i*19}" fill="{MUTED}" font-size="13">{esc(t)}</text>'
        for i, t in enumerate(lines)
    )
    lang = repo_info.get("language") or "—"
    stars = repo_info.get("stargazers_count", 0)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="236" viewBox="0 0 320 236">
{defs()}
  <rect width="320" height="236" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="319" height="235" rx="14" fill="url(#panel)" stroke="{BORDER}"/>
  <path d="M1 44V15a14 14 0 0 1 14-14h44" fill="none" stroke="{accent}" stroke-width="2.5" filter="url(#soft)"/>
  <path d="M319 44V15a14 14 0 0 0-14-14h-44" fill="none" stroke="{accent}" stroke-width="1.5" opacity="0.35"/>
  <text x="294" y="34" fill="{accent}" font-size="11" text-anchor="end" letter-spacing="2" opacity="0.8">{p['index']}</text>
  <text x="26" y="38" fill="{MUTED}" font-size="10" letter-spacing="4">PROJECT</text>
  <text x="26" y="86" fill="{TEXT}" font-size="23" font-weight="700" filter="url(#glow)">{esc(p['title'])}</text>
  {text_lines}
  <rect x="26" y="186" width="{26 + len(lang) * 8.4:.0f}" height="26" rx="13" fill="{accent}" opacity="0.14"/>
  <text x="40" y="204" fill="{accent}" font-size="12">{esc(lang)}</text>
  <text x="294" y="204" fill="{MUTED}" font-size="12" text-anchor="end">★ {stars}</text>
</svg>
"""


def footer_svg():
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="120" viewBox="0 0 {W} 120">
{defs()}
  <rect width="{W}" height="120" fill="{BG}"/>
  <path d="M0 92 Q250 52 500 92 T1000 92" fill="none" stroke="url(#neon)" stroke-width="2" opacity="0.5"/>
  <path d="M0 100 Q250 60 500 100 T1000 100" fill="none" stroke="url(#neon)" stroke-width="1" opacity="0.22"/>
  <text x="500" y="56" fill="{MUTED}" font-size="12" text-anchor="middle" letter-spacing="6">// END OF TRANSMISSION</text>
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = collect()
    stats = data["stats"]
    by_name = {r["name"]: r for r in data["repos"]}

    files = {
        "header.svg": header_svg(stats),
        "divider.svg": divider_svg(),
        "stack.svg": stack_svg(),
        "stats.svg": stats_svg(stats),
        "langs.svg": langs_svg(data["langs"]),
        "activity.svg": activity_svg(data["weeks"]),
        "footer.svg": footer_svg(),
    }
    for p in PROJECTS:
        files[f"project-{p['repo'].lower().replace('_', '-')}.svg"] = project_svg(p, by_name.get(p["repo"], {}))

    for name, content in files.items():
        (OUT / name).write_text(content, encoding="utf-8")
    print(f"generated {len(files)} svg into {OUT}")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
