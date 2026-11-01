"""Generate terminal-window SVG cards for the GitHub profile README."""
import os
import sys
from html import escape

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"

CARDS = [
    {
        "file": "microrato24.svg",
        "path": "~/projects/MicroRato24",
        "accent": "#ff7b72",
        "cmd": "pcompile main.c map.c mr32.c",
        "headline": "A maze-solving robot that learns.",
        "desc": [
            "PIC32 line-follower for UA's MicroRato:",
            "maps the maze on the first run, prunes",
            "dead ends, then races the shortest path.",
        ],
        "status": "path LBR → B | shortest route locked",
        "tags": ["c", "pic32", "robotics"],
    },
    {
        "file": "minimalsiem.svg",
        "path": "~/projects/MinimalSIEM",
        "accent": "#58a6ff",
        "cmd": "docker compose up -d",
        "headline": "A SIEM small enough to run in class.",
        "desc": [
            "TLS-secured Elastic stack in one compose:",
            "Filebeat → Elasticsearch → Kibana.",
            "Plug SIEMgen in and start hunting.",
        ],
        "status": "es01 healthy | kibana healthy",
        "tags": ["elasticsearch", "kibana", "filebeat"],
    },
    {
        "file": "network-lab.svg",
        "path": "~/projects/enterprise-network-lab",
        "accent": "#f0883e",
        "cmd": "show ipv6 route",
        "headline": "A whole company network, emulated.",
        "desc": [
            "Multi-site GNS3 lab: VLSM, dual-stack",
            "IPv4/IPv6, NAT/PAT, DHCP, BIND9 DNS,",
            "Apache vhosts and a threaded TCP service.",
        ],
        "status": "198.155.198.0/24 | dual-stack up",
        "tags": ["gns3", "cisco-ios", "bind9", "python"],
    },
    {
        "file": "dotfiles.svg",
        "path": "~/.dotfiles",
        "accent": "#e3b341",
        "cmd": "nvim ~/.dotfiles",
        "headline": "Where I actually live: the terminal.",
        "desc": [
            "My Arch Linux setup, keyboard-driven:",
            "Neovim with LSP and Treesitter, Zsh,",
            "Tmux, Zellij and WezTerm.",
        ],
        "status": "zoxide | atuin | lsd | loaded",
        "tags": ["shell", "neovim", "arch"],
    },
]

W, H = 440, 220
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


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
        tags.append(
            f'<g class="r" style="animation-delay:{delay:.1f}s">'
            f'<rect x="{x}" y="190" width="{w:.0f}" height="18" rx="9" class="tag"/>'
            f'<text x="{x + w / 2:.1f}" y="203" class="tt" text-anchor="middle">{t}</text></g>'
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


os.makedirs(OUT, exist_ok=True)
for c in CARDS:
    with open(os.path.join(OUT, c["file"]), "w") as f:
        f.write(card(c))
    print("wrote", c["file"])
