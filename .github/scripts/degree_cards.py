"""Generate the BSc / MSc cards for the profile README (assets/bsc.svg, assets/msc.svg)."""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"

W, H = 440, 250
FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def window(title, accent, body, extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<style>
  text {{ font-family: {FONT}; font-size: 12.5px; fill: #c9d1d9; }}
  .h {{ fill: #f0f6fc; font-weight: 700; font-size: 13.5px; }}
  .d {{ fill: #8b949e; }}
  .p {{ fill: {accent}; font-weight: 700; }}
  .bar {{ fill: #8b949e; font-size: 11.5px; }}
  .tag {{ fill: {accent}; fill-opacity: .14; stroke: {accent}; stroke-opacity: .5; }}
  .tt {{ fill: {accent}; font-size: 11px; }}
  .cur {{ fill: {accent}; animation: blink 1s step-end infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  {extra_css}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0d1117" stroke="#30363d"/>
<path d="M0.5 10.5a10 10 0 0 1 10-10h{W - 21}a10 10 0 0 1 10 10v20h-{W - 1}z" fill="#161b22"/>
<line x1="0.5" y1="30.5" x2="{W - 0.5}" y2="30.5" stroke="#30363d"/>
<circle cx="18" cy="15.5" r="5.5" fill="#ff5f57"/><circle cx="36" cy="15.5" r="5.5" fill="#febc2e"/><circle cx="54" cy="15.5" r="5.5" fill="#28c840"/>
<text x="{W / 2}" y="19.5" class="bar" text-anchor="middle">{title}</text>
{body}
</svg>
'''


def tags(names, y):
    out, x = [], 20
    for t in names:
        w = len(t) * 6.7 + 16
        out.append(
            f'<rect x="{x}" y="{y}" width="{w:.0f}" height="18" rx="9" class="tag"/>'
            f'<text x="{x + w / 2:.1f}" y="{y + 13}" class="tt" text-anchor="middle">{t}</text>'
        )
        x += w + 8
    return "".join(out)


def bsc():
    a = "#39d353"
    # one line per second, 5..1; the first one is the static fallback
    countdown = "".join(
        f'<text x="20" y="156" class="d n" font-size="11" style="animation-delay:{i}s{";opacity:1" if i == 0 else ""}">'
        f'Booting PIE automatically in <tspan class="p">{5 - i}</tspan>s</text>'
        for i in range(5)
    )
    body = f'''
<text x="{W / 2}" y="52" class="d" text-anchor="middle" font-size="11">GNU GRUB  version 2.12  |  /dev/sdb1</text>
<rect x="20.5" y="62.5" width="{W - 41}" height="74" fill="none" stroke="#30363d"/>
<rect x="24" y="68" width="{W - 48}" height="20" fill="{a}"/>
<text x="32" y="82" fill="#0d1117" font-weight="700" style="fill:#0d1117">*PIE Live - exam mode</text>
<text x="32" y="106" class="d">Safe Exam Browser</text>
<text x="{W - 32}" y="106" class="d" text-anchor="end" font-size="11">known vulns</text>
<text x="32" y="127" class="d" text-decoration="line-through">Windows 11 - cheatsheet.pdf</text>
<text x="{W - 32}" y="127" text-anchor="end" font-size="11" style="fill:#ff7b72">[blocked]</text>
{countdown}
<text x="20" y="180" class="h">Portable Isolated Environment</text>
<text x="20" y="198" class="d">Plug-and-play USB that turns any laptop into</text>
<text x="20" y="214" class="d">a locked-down exam machine. BSc final project.</text>
{tags(["debian-live", "mitmproxy", "python", "flutter"], 224)}
'''
    css = '''.n { opacity: 0; animation: cd 5s steps(1) infinite; }
  @keyframes cd { 0% { opacity: 1; } 20%, 100% { opacity: 0; } }'''
    return window("BSc LECI | final project | 2025", a, body, css)


def msc():
    a = "#e3b341"
    body = f'''
<text x="20" y="62"><tspan class="p">duarte@santos</tspan><tspan class="d">:~$</tspan> git checkout -b msc/thesis</text>
<text x="20" y="88" class="h">Master's thesis: in progress...</text>
<text x="20" y="114"><tspan class="d">degree</tspan><tspan x="100">MSc Informatics Engineering</tspan></text>
<text x="20" y="133"><tspan class="d">focus </tspan><tspan x="100">cybersecurity</tspan></text>
<text x="20" y="152"><tspan class="d">topic </tspan></text>
<rect x="100" y="141" width="150" height="14" rx="2" class="redact"/>
<text x="258" y="152" class="d" font-size="11">[classified]</text>
<text x="20" y="171"><tspan class="d">eta   </tspan><tspan x="100">2027</tspan></text>
<text x="20" y="198" class="d" font-size="11">pdflatex thesis.tex</text>
<rect x="180" y="189" width="{W - 200}" height="10" rx="5" fill="#21262d"/>
<clipPath id="pb"><rect x="180" y="189" width="{W - 200}" height="10" rx="5"/></clipPath>
<g clip-path="url(#pb)"><rect x="180" y="189" width="80" height="10" rx="5" fill="{a}" class="scan"/></g>
<text x="20" y="226"><tspan class="p">[ BUSY ]</tspan> writing chapter 1 of ? <tspan class="cur">█</tspan></text>
'''
    css = f'''.redact {{ fill: #c9d1d9; animation: glitch 3s steps(1) infinite; }}
  @keyframes glitch {{ 0%, 92% {{ fill: #c9d1d9; }} 94% {{ fill: {a}; }} 96% {{ fill: #c9d1d9; }} }}
  .scan {{ animation: scan 2.4s ease-in-out infinite alternate; }}
  @keyframes scan {{ from {{ transform: translateX(0); }} to {{ transform: translateX({W - 280}px); }} }}'''
    return window("MSc MEI | thesis.tex", a, body, css)


os.makedirs(OUT, exist_ok=True)
for name, svg in (("bsc.svg", bsc()), ("msc.svg", msc())):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(svg)
    print("wrote", name)
