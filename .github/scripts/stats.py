"""Render a compact, terminal-style GitHub stats card (assets/stats.svg).

Runs in the profile-stats workflow with GITHUB_TOKEN and USERNAME set.
`python stats.py --mock` renders sample data, for local previews.
"""
import json
import os
import sys
import urllib.request
from datetime import date
from html import escape

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if "errors" in body:
        sys.exit(f"GraphQL error: {body['errors']}")
    u = body["data"]["user"]
    cc = u["contributionsCollection"]

    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            size, _ = langs.get(name, (0, None))
            langs[name] = (size + e["size"], e["node"]["color"] or "#8b949e")

    days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "login": login,
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "langs": langs,
        "days": [(d["date"], d["contributionCount"]) for d in days],
    }


def streaks(days):
    best = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        best = max(best, run)
    current = 0
    # today may not have contributions yet without breaking the streak
    for i, (_, n) in enumerate(reversed(days)):
        if n:
            current += 1
        elif i > 0:
            break
    return current, best


W, H = 900, 230
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
ACCENT = "#39d353"


def render(s):
    current, best = streaks(s["days"])
    rows = [
        ("contributions", f'{s["contributions"]} in the last year'),
        ("commits", str(s["commits"])),
        ("pull requests", str(s["prs"])),
        ("issues", str(s["issues"])),
        ("public repos", f'{s["repos"]} | {s["stars"]} ★'),
        ("streak", f"{current} day{'s' * (current != 1)} | best {best}"),
    ]
    left = [
        f'<text x="24" y="{92 + i * 21}"><tspan class="k">{k}</tspan>'
        f'<tspan x="170">{escape(v)}</tspan></text>'
        for i, (k, v) in enumerate(rows)
    ]

    # languages: one stacked bar plus a legend of the top five
    total = sum(sz for sz, _ in s["langs"].values()) or 1
    top = sorted(s["langs"].items(), key=lambda kv: -kv[1][0])[:5]
    rest = total - sum(sz for _, (sz, _) in top)
    parts = [(n, sz, c) for n, (sz, c) in top] + ([("other", rest, "#484f58")] if rest > 0 else [])
    bx, bw, x = 470, 406, 470.0
    bar = [f'<clipPath id="bc"><rect x="{bx}" y="80" width="{bw}" height="8" rx="4"/></clipPath><g clip-path="url(#bc)">']
    legend = []
    for i, (n, sz, c) in enumerate(parts):
        w = bw * sz / total
        bar.append(f'<rect x="{x:.1f}" y="80" width="{w + 0.5:.1f}" height="8" fill="{c}"/>')
        x += w
        lx, ly = bx + (i % 3) * 136, 110 + (i // 3) * 20
        legend.append(
            f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4" fill="{c}"/>'
            f'<text x="{lx + 14}" y="{ly}" class="s">{escape(n)} <tspan class="k">{100 * sz / total:.1f}%</tspan></text>'
        )
    bar.append("</g>")

    # activity: weekly totals for the last 52 weeks, as a tiny bar chart
    weeks = [sum(n for _, n in s["days"][i:i + 7]) for i in range(0, len(s["days"]), 7)][-52:]
    peak = max(weeks) or 1
    spark = []
    for i, n in enumerate(weeks):
        h = 2 + 34 * n / peak
        spark.append(
            f'<rect x="{bx + i * 7.8:.1f}" y="{204 - h:.1f}" width="5.4" height="{h:.1f}" rx="1.5" '
            f'fill="{ACCENT}" fill-opacity="{0.25 + 0.75 * n / peak:.2f}"/>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats for {escape(s["login"])}">
<style>
  text {{ font-family: {FONT}; font-size: 13px; fill: #c9d1d9; }}
  .k {{ fill: #8b949e; }}
  .s {{ font-size: 12px; }}
  .h {{ fill: {ACCENT}; font-weight: 700; }}
  .bar {{ fill: #8b949e; font-size: 11.5px; }}
  .fade {{ animation: in .6s ease-out both; }}
  @keyframes in {{ from {{ opacity: 0; }} }}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="#161b22"/>
<line x1="0.5" y1="30.5" x2="{W - 0.5}" y2="30.5" stroke="#30363d"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" class="bar" text-anchor="middle">neofetch --github</text>
<text x="24" y="60"><tspan class="h">{escape(s["login"])}</tspan><tspan class="k">@github</tspan></text>
<line x1="24" y1="70" x2="420" y2="70" stroke="#30363d" stroke-dasharray="3 3"/>
<g class="fade">{"".join(left)}</g>
<line x1="446" y1="48" x2="446" y2="208" stroke="#30363d"/>
<text x="{bx}" y="60" class="k">languages</text>
<g class="fade">{"".join(bar)}{"".join(legend)}</g>
<text x="{bx}" y="160" class="k">activity - 52 weeks</text>
<g class="fade">{"".join(spark)}</g>
<text x="{W - 24}" y="{H - 8}" class="bar" text-anchor="end" font-size="10">updated {date.today().isoformat()}</text>
</svg>
'''


def mock():
    import random
    random.seed(7)
    days = [(str(i), random.choice([0, 0, 0, 1, 2, 3, 5, 8])) for i in range(364)]
    return {
        "login": "Duarters07", "contributions": sum(n for _, n in days), "commits": 512,
        "prs": 14, "issues": 6, "repos": 9, "stars": 4, "days": days,
        "langs": {"Python": (420000, "#3572A5"), "C": (310000, "#555555"), "VHDL": (150000, "#adb2cb"),
                  "Shell": (90000, "#89e051"), "Lua": (60000, "#000080"), "HTML": (40000, "#e34c26")},
    }


if __name__ == "__main__":
    data = mock() if "--mock" in sys.argv else fetch(os.environ["USERNAME"], os.environ["GITHUB_TOKEN"])
    out = os.environ.get("OUT", "assets/stats.svg")
    with open(out, "w") as f:
        f.write(render(data))
    print("wrote", out)
