"""Genera las 3 propuestas de logo (perfil 1080x1080 y portada de Facebook 1640x624)."""
import os, subprocess

KIT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(KIT), "logo", "propuestas")
os.makedirs(OUT, exist_ok=True)
QX = 588
NAVY, GOLD, PAPER, MID = "#0F2340", "#D4A017", "#F5F2EB", "#2A3F63"

FONTS = f"""@font-face{{font-family:'SS4';src:url('file://{KIT}/fonts/SourceSerif4.ttf');font-weight:200 900}}
@font-face{{font-family:'Arch';src:url('file://{KIT}/fonts/Archivo.ttf');font-weight:100 900}}
html,body{{margin:0}}"""

# --- Íconos (SVG 1080x1080). Todo lo importante cabe en el círculo central (radio ~460). ---

# 1 · Globo: burbuja de diálogo con ¿? — evolución del logo actual, sin texto.
ICON_1 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
<rect width="1080" height="1080" fill="{NAVY}"/>
<path d="M300 300 h480 a90 90 0 0 1 90 90 v240 a90 90 0 0 1 -90 90 h-300 l-120 110 v-110 h-60 a90 90 0 0 1 -90 -90 v-240 a90 90 0 0 1 90 -90 z" fill="{PAPER}"/>
<text x="455" y="690" text-anchor="middle" font-family="SS4" font-weight="900" font-size="440" fill="{NAVY}">¿</text>
<text x="640" y="660" text-anchor="middle" font-family="SS4" font-weight="900" font-size="440" fill="{GOLD}">?</text>
</svg>"""

# 2 · Monograma ¿Y?: corto, se lee como "¿Y?" (¿y usted?).
ICON_2 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
<rect width="1080" height="1080" fill="{NAVY}"/>
<circle cx="540" cy="540" r="400" fill="none" stroke="{GOLD}" stroke-width="18"/>
<text x="540" y="705" text-anchor="middle" font-family="SS4" font-weight="900" font-size="460" letter-spacing="-20">
<tspan fill="{GOLD}">¿</tspan><tspan fill="{PAPER}">Y</tspan><tspan fill="{GOLD}">?</tspan></text>
</svg>"""

# 3 · Dos lados: círculo partido (debate) con un "?" que cruza ambos lados.
ICON_3 = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080">
<defs><clipPath id="left"><rect x="0" y="0" width="540" height="1080"/></clipPath>
<clipPath id="right"><rect x="540" y="0" width="540" height="1080"/></clipPath></defs>
<rect width="540" height="1080" fill="{NAVY}"/><rect x="540" width="540" height="1080" fill="{GOLD}"/>
<g font-family="SS4" font-weight="900" font-size="780" text-anchor="middle">
<text x="{QX}" y="820" fill="{PAPER}" clip-path="url(#left)">?</text>
<text x="{QX}" y="820" fill="{NAVY}" clip-path="url(#right)">?</text></g>
</svg>"""

ICONS = {"1_globo": ICON_1, "2_monograma": ICON_2, "3_dos_lados": ICON_3}

TAGLINE = "Noticias claras · Opinión marcada · Usted decide"


def cover(icon_svg, name):
    """Portada FB 1640x624. FB recorta los lados en móvil: lo importante va al centro (~1100 px)."""
    return f"""<div style="width:1640px;height:624px;background:{NAVY};display:flex;align-items:center;justify-content:center;gap:56px;font-family:'Arch',sans-serif;position:relative;overflow:hidden">
<div style="position:absolute;left:0;right:0;bottom:0;height:14px;background:{GOLD}"></div>
<div style="width:260px;height:260px;border-radius:50%;overflow:hidden;flex:none{'' if name.startswith('2') else ';box-shadow:0 0 0 6px ' + GOLD}">{icon_svg.replace('width="1080" height="1080"', 'width="260" height="260"')}</div>
<div style="color:{PAPER}">
<div style="font-family:'SS4',serif;font-weight:900;font-size:96px;line-height:1;letter-spacing:-2px">¿Y usted qué opina<span style="color:{GOLD}">?</span></div>
<div style="font-weight:600;font-size:30px;letter-spacing:3px;margin-top:22px;color:#C9CFDB">{TAGLINE.upper()}</div>
</div></div>"""


def render(html, path, w, h):
    tmp = path + ".html"
    open(tmp, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><style>{FONTS}</style></head><body>{html}</body></html>')
    subprocess.run(["python3", "-c", f"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={{'width':{w},'height':{h}}})
    pg.goto('file://{tmp}'); pg.wait_for_timeout(400)
    pg.screenshot(path='{path}', clip={{'x':0,'y':0,'width':{w},'height':{h}}}); b.close()"""], check=True)
    os.remove(tmp)


for name, svg in ICONS.items():
    render(svg, f"{OUT}/{name}_perfil.png", 1080, 1080)
    render(cover(svg, name), f"{OUT}/{name}_portada_fb.png", 1640, 624)
print("ok", OUT)
