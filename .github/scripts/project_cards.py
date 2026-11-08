"""Draw the project cards from cards.toml and update the grid in README.md.

Run locally: `python3 .github/scripts/project_cards.py`.
Missing fields in cards.toml are filled from the GitHub API (GITHUB_TOKEN is
optional locally, but unauthenticated requests are rate limited).
"""
import json
import os
import re
import sys
import textwrap
import tomllib
import urllib.error
import urllib.request
from html import escape

OWNER = os.environ.get("USERNAME", "Duarters07")
TOKEN = os.environ.get("GITHUB_TOKEN")
CONFIG, README, ASSETS = "cards.toml", "README.md", "assets/projects"
START, END = "<!-- projects:start -->", "<!-- projects:end -->"

PALETTE = ["#ff7b72", "#58a6ff", "#f0883e", "#e3b341", "#39d353", "#bc8cff", "#56d4dd"]
W, H = 440, 220
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
# roughly how many monospace characters fit on one line of the card
MAX_LINE, MAX_HEADLINE, MAX_STATUS = 46, 44, 40


def warn(msg):
    # shows up as an annotation on the workflow run
    print(f"::warning::{msg}" if os.environ.get("GITHUB_ACTIONS") else f"warning: {msg}")


def fit(text, limit, what):
    if len(text) <= limit:
        return text
    warn(f"{what} is {len(text)} characters, cut to {limit}: {text!r}")
    return text[: limit - 1] + "…"


def github(repo):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}")
    if TOKEN:
        req.add_header("Authorization", f"bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.URLError as e:
        warn(f"could not fetch {repo} from GitHub ({e}), using cards.toml only")
        return {}


def resolve(p, i):
    full = p["repo"] if "/" in p["repo"] else f"{OWNER}/{p['repo']}"
    name = full.split("/")[1]
    gh = github(full)
    status = p.get("status") or " | ".join(
        x for x in (f"★ {gh.get('stargazers_count', 0)}", gh.get("language"),
                    f"pushed {gh['pushed_at'][:10]}" if gh.get("pushed_at") else None) if x
    )
    desc = p.get("description") or gh.get("description") or ""
    lines = textwrap.wrap(desc, MAX_LINE)
    if len(lines) > 3:
        warn(f"{name}: description is longer than 3 lines, the rest is cut")
        lines = lines[:2] + [fit(" ".join(lines[2:]), MAX_LINE, f"{name} description")]
    tags = p.get("tags") or gh.get("topics") or [t for t in [gh.get("language")] if t]
    return {
        "slug": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
        "url": gh.get("html_url") or f"https://github.com/{full}",
        "path": f"~/projects/{name}",
        "accent": p.get("accent") or PALETTE[i % len(PALETTE)],
        "cmd": fit(p.get("cmd") or f"cd ~/projects/{name}", MAX_LINE - 17, f"{name} cmd"),
        "headline": fit(p.get("headline") or name, MAX_HEADLINE, f"{name} headline"),
        "desc": lines,
        "status": fit(status, MAX_STATUS, f"{name} status"),
        "tags": [t.lower() for t in tags],
        "name": name,
    }


def card(c):
    a = c["accent"]
    lines = []
    # each revealed line gets an increasing animation delay
    delay = 0.2

    def text(x, y, body, cls):
        nonlocal delay
        lines.append(
            f'<text x="{x}" y="{y}" class="{cls} r" style="animation-delay:{delay:.1f}s">{body}</text>'
        )
        delay += 0.35

    text(20, 62, f'<tspan class="p">duarte@santos</tspan><tspan class="d">:~$</tspan> {escape(c["cmd"])}', "t")
    text(20, 88, escape(c["headline"]), "h")
    for i, d in enumerate(c["desc"]):
        text(20, 110 + i * 18, escape(d), "d")
    text(20, 176, f'<tspan class="ok">[  OK  ]</tspan> {escape(c["status"])} <tspan class="cur">█</tspan>', "t")

    tags, x = [], 20
    for t in c["tags"]:
        w = len(t) * 6.7 + 16
        if x + w > W - 20:
            warn(f"{c['name']}: tag {t!r} does not fit and was left out")
            break
        tags.append(
            f'<g class="r" style="animation-delay:{delay:.1f}s">'
            f'<rect x="{x}" y="190" width="{w:.0f}" height="18" rx="9" class="tag"/>'
            f'<text x="{x + w / 2:.1f}" y="203" class="tt" text-anchor="middle">{escape(t)}</text></g>'
        )
        x += w + 8

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(c["path"])}">
<style>
  text {{ font-family: {FONT}; font-size: 12.5px; fill: #c9d1d9; }}
  .h {{ fill: #f0f6fc; font-weight: 700; font-size: 13.5px; }}
  .d {{ fill: #8b949e; }}
  .p, .ok {{ fill: {a}; font-weight: 700; }}
  .bar {{ fill: #8b949e; font-size: 11.5px; }}
  .tag {{ fill: {a}; fill-opacity: .14; stroke: {a}; stroke-opacity: .5; }}
  .tt {{ fill: {a}; font-size: 11px; }}
  .r {{ animation: in .45s ease-out both; }}
  .cur {{ fill: {a}; animation: blink 1s step-end infinite; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-6px); }} to {{ opacity: 1; transform: none; }} }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="#161b22"/>
<line x1="0.5" y1="30.5" x2="{W - 0.5}" y2="30.5" stroke="#30363d"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" class="bar" text-anchor="middle">{escape(c["path"])}</text>
<rect x="{W - 4}" y="44" width="2" height="150" rx="1" fill="{a}" opacity=".6"/>
{chr(10).join(lines)}
{chr(10).join(tags)}
</svg>
'''


def main():
    with open(CONFIG, "rb") as f:
        projects = tomllib.load(f).get("project", [])
    cards = [resolve(p, i) for i, p in enumerate(projects)]

    # start clean so removed projects do not leave stale SVGs behind
    os.makedirs(ASSETS, exist_ok=True)
    for old in os.listdir(ASSETS):
        if old.endswith(".svg"):
            os.remove(os.path.join(ASSETS, old))
    for c in cards:
        with open(os.path.join(ASSETS, f"{c['slug']}.svg"), "w") as f:
            f.write(card(c))
        print("wrote", f"{ASSETS}/{c['slug']}.svg")

    grid = "\n".join(
        f'  <a href="{c["url"]}"><img src="{ASSETS}/{c["slug"]}.svg" width="49%" alt="{escape(c["name"])}" /></a>'
        for c in cards
    )
    with open(README) as f:
        readme = f.read()
    if START not in readme or END not in readme:
        sys.exit(f"README.md needs {START} and {END} around the project grid")
    block = f'{START}\n<p align="center">\n{grid}\n</p>\n{END}'
    readme = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, readme, flags=re.S)
    with open(README, "w") as f:
        f.write(readme)
    print(f"updated {README} with {len(cards)} cards")


if __name__ == "__main__":
    main()
