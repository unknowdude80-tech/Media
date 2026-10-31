"""Generador de diapositivas de @yusted.queopina (Instagram, 1080x1350).

Uso:  python3 kit/generar.py lotes/2026-10-11/peso.json
Sale: los JPEG junto al JSON (peso_1.jpg, peso_2.jpg, ...). Instagram vía TARDIS no acepta PNG.

Formato del JSON (ver kit/ejemplo.json):
{"post": "peso", "seccion": "economia", "slides": [ {"tipo": "...", ...}, ... ]}
estilo: atardecer | noche | barda (opcional, recomendado). Ambiente de barrio regio con el Cerro de la Silla; se elige por el TONO de la nota, no por la sección:
  barda     = día a día, bolsillo, trámites, tecnología útil, notas ligeras o positivas (rótulo pintado en barda de block)
  atardecer = notas grandes del día, debates, cambios que afectan a todos (cielo morado a dorado sobre el cerro)
  noche     = notas serias o pesadas: seguridad, crisis, conflictos, análisis (noche en la colonia con foquitos)
  Si hay estilo, manda sobre los colores de sección. Sin estilo se usa el diseño anterior por sección.
temporada: navidad (opcional). Adorno de temporada solo en la portada y solo en barda o atardecer: en noche, en el
  resumen matutino y en notas delicadas no va (ver GUIA.md, "Temporadas"). Sin el campo, la portada sale normal.
seccion: politica (azul, país) | economia (crema) | tecnologia (verde azulado) | mundo (negro) | analisis (negro) | debate (dorado) | resumen (blanco). Define el color de portada y cierre.

Tipos de diapositiva:
  portada  tag, titulo, personaje? ("picos:<expresion>" = El Picos de cuerpo, o "rober"/"brayan"; expresiones: principal, explicando, sorprendido, esceptico, riendose, molesto, pensativo), cifra? (número gigante, ej. "70%"), subtitulo?, icono? (nombre lucide) o mapa? {"estados":[ids], "etiqueta":?}
  dato     tag, cifra, texto, puntos?
  lista    tag, titulo, puntos
  grafica  tag, titulo, barras [[etiqueta, valor], ...], unidad, decimales?, nota?, eje_cero? (true = no recortar el eje; úsalo si comparar tamaños importa)
  linea    tag, titulo, puntos_serie [[etiqueta, valor], ...], unidad, decimales?, nota?
  mapa     tag, titulo, estados [ids], texto?, leyenda?
  cita     texto, autor, contexto?
  versus   tag, titulo, a_favor [..], en_contra [..], lado_a?, lado_b?  (para posts de DEBATE)
  foto     foto (ruta relativa al JSON), estilo? (duotono|poster|grabado), credito, tag?, titulo, texto?, swipe? (true si es portada)
  resumen  fecha (ej. "Lunes 26 de octubre"), titulares [5 frases cortas], titulo? (por defecto "LAS 5 DE HOY")  — portada del resumen matutino
  personaje quien (picos:<expresion> | rober | brayan), texto (en su voz), firma?, tag?, tema?  — globo de diálogo con su avatar (alias: tipo "rober")
  nota     numero, tag (tema), titular, texto (2-3 líneas), fuente  — una noticia del resumen matutino
  cierre   titulo, texto, fuentes, tag? (por defecto "LES TOCA")
  vineta   imagen (ruta relativa al JSON, 4:5, sin texto), globos [{texto, x, y, w, cola:[x,y]}] (cola = punto al que apunta, la boca de quien habla),
           neta? {texto, fuente?} (recuadro LA NETA abajo), tag? y titulo? (solo portada), fuentes? (texto chico, para la última)  — historieta "Plática en el taller"
Todas aceptan "tema": "dark" | "light" | "gold" | "black" | "teal" | "brief" (cada tipo tiene su valor por defecto).
En titulos y textos: *palabra* = dorado, **palabra** = negritas.
Ids de estados: ver kit/mexico_map.json (agu, bcn, bcs, cam, chp, chh, coa, col, dur,
gua, gro, hid, jal, cmx, mex, mic, mor, nay, nle, oax, pue, que, roo, slp, sin, son,
tab, tam, tla, ver, yuc, zac).
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from estilizar import estilizar
from playwright.sync_api import sync_playwright

KIT = os.path.dirname(os.path.abspath(__file__))
NAVY, GOLD, PAPER, MUTED, LINE = "#0F2340", "#D4A017", "#F5F2EB", "#C9CFDB", "#2A3F63"
INK = "#161616"
# Cada sección tiene su color de portada y cierre, para que la cuadrícula del perfil no se vea repetida.
# Se evitan a propósito los colores de partidos (guinda, rojo, verde, naranja, azul PAN).
ESTILOS = ("atardecer", "noche", "barda")
CLAROS = ("light", "brief", "barda")  # fondos claros: texto azul
TEAL = "#0F5257"
SECCIONES = {"politica": "dark", "economia": "light", "debate": "gold", "analisis": "black", "mundo": "black", "tecnologia": "teal", "resumen": "brief"}
ART = {  # (color de ícono/realce, base del mapa, trazo del mapa)
    "dark": (GOLD, LINE, NAVY), "light": (GOLD, "#D9DEE7", PAPER),
    "gold": (NAVY, "#E3B83F", GOLD), "black": (GOLD, "#2E2E2E", INK), "brief": (GOLD, "#D9DEE7", "#FFFFFF"), "teal": (GOLD, "#1D6B70", "#0F5257"),
    "atardecer": (GOLD, "#6A3A7E", "#2A1A45"), "noche": (GOLD, "#2A3F6E", "#0F1B33"), "barda": (TEAL, "#CFC4AE", PAPER)}
MAP = json.load(open(os.path.join(KIT, "mexico_map.json")))
PERSONAJES = {"picos": "El Picos", "tio": "El Picos", "rober": "Don Rober", "brayan": "El Brayan"}
FIRMAS = {"picos": "Brayan para su jefa, El Picos para la colonia", "tio": "Brayan para su jefa, El Picos para la colonia", "rober": "Taxista y lector de tres periódicos", "brayan": "Técnico en celulares y programador de noche"}
EXPRESIONES = ["principal", "explicando", "sorprendido", "esceptico", "riendose", "molesto", "pensativo"]  # avatares en kit/<clave>.svg


def tio_png(quien, circ=True):
    expr = quien.split(":", 1)[1] if ":" in quien else "principal"
    if expr not in EXPRESIONES:
        raise ValueError(f"expresión desconocida: {expr} (usa {EXPRESIONES})")
    return os.path.join(KIT, "picos", ("circ_" if circ else "") + expr + ".png")


def rober(size, ring=None, quien="rober"):
    if quien.startswith(("picos", "tio")):
        ring = f";box-shadow:0 0 0 8px {ring}" if ring else ""
        return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;overflow:hidden;flex:none;background:{NAVY}{ring}">'
                f'<img src="file://{tio_png(quien)}" style="width:100%;height:100%;display:block"></div>')
    svg = open(os.path.join(KIT, f"{quien}.svg")).read().replace('width="400" height="400"', f'width="{size}" height="{size}"')
    ring = f";box-shadow:0 0 0 8px {ring}" if ring else ""
    return f'<div style="width:{size}px;height:{size}px;border-radius:50%;overflow:hidden;flex:none{ring}">{svg}</div>'

CSS = f"""
@font-face{{font-family:'SS4';src:url('file://{KIT}/fonts/SourceSerif4.ttf');font-weight:200 900}}
@font-face{{font-family:'Arch';src:url('file://{KIT}/fonts/Archivo.ttf');font-weight:100 900}}
@font-face{{font-family:'Bebas';src:url('file://{KIT}/fonts/BebasNeue-Regular.ttf')}}
@font-face{{font-family:'Pirata';src:url('file://{KIT}/fonts/PirataOne-Regular.ttf')}}
@font-face{{font-family:'Bungee';src:url('file://{KIT}/fonts/Bungee-Regular.ttf')}}
@font-face{{font-family:'Marker';src:url('file://{KIT}/fonts/PermanentMarker-Regular.ttf')}}
html,body{{margin:0}}
.s{{isolation:isolate;width:1080px;height:1350px;box-sizing:border-box;padding:96px 88px 0;position:relative;overflow:hidden;font-family:'Arch',sans-serif;display:flex;flex-direction:column}}
.dark{{background:{NAVY};color:{PAPER}}} .light{{background:{PAPER};color:{NAVY}}}
.gold{{background:{GOLD};color:{NAVY}}} .black{{background:{INK};color:{PAPER}}}
.brief{{background:#FFFFFF;color:{NAVY}}}
.teal{{background:#0F5257;color:{PAPER}}}
.rband{{position:absolute;left:0;right:0;top:0;height:300px;background:{NAVY};z-index:0}}
.rtitle{{position:relative;z-index:2;color:{PAPER};font-weight:800;font-size:38px;letter-spacing:6px}}
.rdate{{position:relative;z-index:2;font-family:'SS4',serif;font-weight:900;font-size:92px;line-height:1;color:{GOLD};margin-top:18px}}
.rlist{{margin-top:110px;display:flex;flex-direction:column;gap:30px}}
.ritem{{display:flex;gap:28px;align-items:baseline}}
.rnum{{font-family:'SS4',serif;font-weight:900;font-size:76px;color:{GOLD};width:56px;flex:none;line-height:1}}
.rtxt{{font-family:'SS4',serif;font-weight:700;font-size:50px;line-height:1.12}}
.nnum{{font-family:'SS4',serif;font-weight:900;font-size:240px;line-height:.85;color:{GOLD};margin-top:30px}}
.nsrc{{font-size:26px;opacity:.7;margin-top:auto;margin-bottom:150px}}
.gold .tag{{background:{NAVY};color:{GOLD}}} .gold .g{{background:linear-gradient(transparent 18%,{NAVY} 18%,{NAVY} 94%,transparent 94%);color:{GOLD};padding:0 .1em;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.gold li:before{{background:{NAVY}}} .gold .swipe{{color:{NAVY}}}
.cover .tag{{font-size:34px;padding:14px 26px}}
.cover .h1{{font-size:118px;line-height:1}}
.hero{{font-family:'SS4',serif;font-weight:900;font-size:330px;line-height:.9;letter-spacing:-10px;margin-top:56px;position:relative;z-index:2}}
.tag{{align-self:flex-start;font-weight:800;font-size:28px;letter-spacing:4px;padding:12px 22px;background:{GOLD};color:{NAVY};position:relative;z-index:2}}
.h1{{font-family:'SS4',serif;font-weight:900;font-size:100px;line-height:1.02;letter-spacing:-2px;margin:44px 0 0;position:relative;z-index:2}}
.h2{{font-family:'SS4',serif;font-weight:900;font-size:68px;line-height:1.08;letter-spacing:-1px;margin:40px 0 0}}
.lead{{font-size:40px;line-height:1.4;font-weight:500;margin-top:36px;position:relative;z-index:2}}
.g{{color:{GOLD}}}
ul{{margin:44px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:32px}}
li{{font-size:38px;line-height:1.38;padding-left:44px;position:relative}}
li:before{{content:'';position:absolute;left:0;top:18px;width:18px;height:18px;background:{GOLD}}}
.vb li:before{{background:{NAVY}}}
.big{{font-family:'SS4',serif;font-weight:900;font-size:220px;line-height:1;letter-spacing:-6px;margin-top:40px}}
.foot{{position:absolute;left:88px;right:88px;bottom:64px;display:flex;align-items:center;justify-content:space-between;font-weight:700;font-size:26px;letter-spacing:2px;z-index:3}}
.mark{{display:flex;align-items:center;gap:16px}}
.bub{{width:60px;height:60px;border-radius:50%;background:{NAVY};box-shadow:inset 0 0 0 3px {GOLD};display:flex;align-items:center;justify-content:center;font-family:'SS4',serif;font-weight:900;font-size:27px;letter-spacing:-1px;padding-top:2px;box-sizing:border-box}}
.src{{font-size:26px;line-height:1.5;margin-top:auto;margin-bottom:150px;opacity:.85}}
.swipe{{font-weight:800;font-size:30px;letter-spacing:3px;margin-top:auto;margin-bottom:160px;color:{GOLD};position:relative;z-index:2}}
.note{{font-size:24px;opacity:.75;margin-top:24px}}
.art{{position:absolute;z-index:1}}
.quote{{font-family:'SS4',serif;font-weight:700;font-style:italic;font-size:84px;line-height:1.2;margin-top:40px}}
.qmark{{font-family:'SS4',serif;font-weight:900;font-size:260px;line-height:.8;color:{GOLD};margin-top:30px;height:140px}}
/* ---- Estilos de barrio ---- */
.atardecer{{background:linear-gradient(180deg,#24183F 0%,#4A2563 45%,#7E3470 80%,#A84470 100%);color:{PAPER}}}
.atardecer.cover{{background:linear-gradient(180deg,#24183F 0%,#5B2A6E 30%,#B8477A 55%,#F2B33D 82%)}}
.noche{{background:radial-gradient(ellipse at 70% 0%,#25386A 0%,#0F1B33 55%,#0A1222 100%);color:{PAPER}}}
.barda{{background-color:#CFC4AE;background-image:linear-gradient(#A89C84 4px,transparent 4px),linear-gradient(90deg,#A89C84 4px,transparent 4px);background-size:270px 135px;color:{NAVY}}}
.atardecer .h1,.atardecer .h2,.atardecer .hero,.atardecer .big,.atardecer .nnum,.atardecer .rdate{{font-family:'Bebas',sans-serif;font-weight:400;letter-spacing:1px}}
.atardecer .h1{{font-size:150px;line-height:.9}} .atardecer.cover .h1{{font-size:170px}} .atardecer .h2{{font-size:96px;line-height:.95}}
.atardecer .hero{{font-size:380px;line-height:.85}} .atardecer .big{{font-size:300px}}
.atardecer .tag{{background:none;color:{GOLD};font-family:'Pirata',serif;font-weight:400;font-size:60px;letter-spacing:1px;padding:0}}
.noche .h1,.noche .h2,.noche .hero,.noche .big,.noche .nnum,.noche .rdate{{font-family:'Pirata',serif;font-weight:400;letter-spacing:0;color:{GOLD};text-shadow:0 5px 0 #6B4E0A}}
.noche .h1{{font-size:130px;line-height:.98}} .noche .h2{{font-size:88px;line-height:1}} .noche .hero{{font-size:330px}} .noche .big{{font-size:260px}}
.noche .h1 .g,.noche .h2 .g{{color:{PAPER}}}
.noche .tag{{background:none;color:{PAPER};font-family:'Bebas',sans-serif;font-weight:400;font-size:52px;letter-spacing:6px;padding:0}}
.barda .h1,.barda .h2,.barda .hero,.barda .big,.barda .nnum,.barda .rdate{{font-family:'Bungee',sans-serif;font-weight:400;letter-spacing:0;color:{NAVY};text-shadow:6px 6px 0 {GOLD}}}
.barda .h1{{font-size:92px;line-height:1.04}} .barda .h2{{font-size:62px;line-height:1.1}} .barda .hero{{font-size:250px;line-height:1}} .barda .big{{font-size:200px}}
.barda .h1 .g,.barda .h2 .g,.barda .hero .g{{color:{TEAL}}}
.barda .g{{color:{NAVY};background:linear-gradient(transparent 30%,rgba(212,160,23,.75) 30%,rgba(212,160,23,.75) 96%,transparent 96%);padding:0 4px;-webkit-box-decoration-break:clone;box-decoration-break:clone}}
.barda .tag{{background:none;color:{TEAL};font-family:'Marker',cursive;font-weight:400;font-size:46px;letter-spacing:0;padding:0}}
.barda li:before{{background:{TEAL}}} .barda .swipe{{font-family:'Marker',cursive;font-weight:400;letter-spacing:0;color:{NAVY}}}
.atardecer .swipe,.noche .swipe{{text-shadow:0 2px 8px #000;font-family:'Bebas',sans-serif;font-weight:400;font-size:44px;letter-spacing:4px}}
.atardecer .rtitle,.noche .rtitle{{font-family:'Bebas',sans-serif;font-weight:400;font-size:64px}} .barda .rtitle{{color:{TEAL};font-family:'Marker',cursive;font-weight:400;font-size:56px;letter-spacing:0}}
.atardecer .rnum,.noche .rnum{{font-family:'Bebas',sans-serif;font-weight:400}} .barda .rnum{{font-family:'Bungee',sans-serif;color:{TEAL}}}
.atardecer .rtxt,.noche .rtxt,.barda .rtxt{{font-family:'Arch',sans-serif;font-weight:700;font-size:44px}}
.rotulo{{position:relative;z-index:2;background:{PAPER};border:14px solid {TEAL};box-shadow:10px 12px 0 rgba(0,0,0,.18);transform:rotate(-1.2deg);padding:36px 40px 44px;margin:-26px -32px 0;display:flex;flex-direction:column}}
.globo{{position:absolute;z-index:5;background:#fff;color:#111;border:5px solid #111;border-radius:44px;padding:22px 30px;font-family:'Arch',sans-serif;font-weight:800;font-size:40px;line-height:1.18;box-shadow:6px 7px 0 rgba(0,0,0,.25)}}
.globo .g{{color:#B8860B}}
.vtit{{font-family:'Bebas',sans-serif;font-size:130px;line-height:.9;color:#fff;text-shadow:0 4px 14px rgba(0,0,0,.55)}} .vtit .g{{color:{GOLD}}}
.neta{{position:absolute;left:50px;right:50px;bottom:130px;z-index:6;background:{NAVY};color:{PAPER};border-left:12px solid {GOLD};padding:22px 30px;font-size:30px;line-height:1.35;font-weight:600;box-shadow:0 6px 20px rgba(0,0,0,.35)}}
.netat{{font-family:'Bebas',sans-serif;font-size:40px;letter-spacing:4px;color:{GOLD};font-weight:400;line-height:1}}
.netaf{{font-size:22px;opacity:.75;margin-top:8px}}
.who{{font-weight:800;font-size:34px;letter-spacing:1px;margin-top:48px}}
.ctx{{font-size:28px;opacity:.8;margin-top:10px}}
"""


def fmt(t):
    t = html.escape(t or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*(.+?)\*", r'<span class="g">\1</span>', t)


def icon(name, size, color, stroke=1.5):
    svg = open(os.path.join(KIT, "icons", f"{name}.svg")).read()
    svg = re.sub(r'width="\d+"', f'width="{size}"', svg, count=1)
    svg = re.sub(r'height="\d+"', f'height="{size}"', svg, count=1)
    svg = svg.replace('stroke="currentColor"', f'stroke="{color}"')
    return re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{stroke}"', svg)


def mexico(width, highlight, base, hi, stroke):
    paths = "".join(
        f'<path d="{l["path"]}" fill="{hi if l["id"] in highlight else base}" stroke="{stroke}" stroke-width="1.2"/>'
        for l in MAP["locations"])
    return f'<svg viewBox="{MAP["viewBox"]}" width="{width}" xmlns="http://www.w3.org/2000/svg">{paths}</svg>'


def bars(data, unit, dec, theme, eje_cero=False):
    fg = NAVY if theme in CLAROS else PAPER
    vmax = max(v for _, v in data)
    vmin = min(v for _, v in data)
    floor = 0 if (eje_cero or vmin < vmax * 0.5) else vmin * 0.9   # recorta el eje si las barras son parecidas
    W, H, gap = 900, 560, 40
    bw = (W - gap * (len(data) - 1)) / len(data)
    out = []
    for i, (lab, v) in enumerate(data):
        h = max(8, (v - floor) / (vmax - floor) * (H - 90))
        x = i * (bw + gap)
        col = GOLD if i == len(data) - 1 else (LINE if theme in ("dark", "noche") else "#9A8F79" if theme == "barda" else "#B9C2D3")
        out.append(f'<rect x="{x}" y="{H - h}" width="{bw}" height="{h}" fill="{col}"/>'
                   f'<text x="{x + bw/2}" y="{H - h - 20}" text-anchor="middle" font-family="SS4" font-weight="900" font-size="54" fill="{fg}">{v:.{dec}f}</text>'
                   f'<text x="{x + bw/2}" y="{H + 48}" text-anchor="middle" font-family="Arch" font-weight="600" font-size="30" fill="{fg}">{html.escape(lab)}</text>')
    axis = "" if floor == 0 else f'<text x="0" y="{H + 92}" font-family="Arch" font-size="22" fill="{fg}" opacity=".6">Eje recortado: empieza en {floor:.{dec}f}</text>'
    return (f'<svg width="{W}" height="{H + 100}" style="margin-top:56px;overflow:visible">{"".join(out)}'
            f'<line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="{fg}" stroke-width="2"/>{axis}</svg>'
            f'<div class="note">{html.escape(unit)}</div>')


def line(data, unit, dec, theme):
    fg = NAVY if theme in CLAROS else PAPER
    vals = [v for _, v in data]
    lo, hi = min(vals), max(vals)
    pad = (hi - lo) * 0.15 or 1
    lo, hi = lo - pad, hi + pad
    W, H = 900, 520
    pts = [(i * W / (len(data) - 1), H - (v - lo) / (hi - lo) * H) for i, (_, v) in enumerate(data)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    marks = "".join(
        f'<circle cx="{x}" cy="{y}" r="{12 if i in (0, len(pts)-1) else 7}" fill="{GOLD if i == len(pts)-1 else fg}"/>'
        + (f'<text x="{x}" y="{y - 30}" text-anchor="{"start" if i == 0 else "end"}" font-family="SS4" font-weight="900" font-size="50" fill="{fg}">{data[i][1]:.{dec}f}</text>'
           if i in (0, len(pts) - 1) else "")
        for i, (x, y) in enumerate(pts))
    labs = (f'<text x="0" y="{H + 56}" font-family="Arch" font-weight="600" font-size="28" fill="{fg}">{html.escape(data[0][0])}</text>'
            f'<text x="{W}" y="{H + 56}" text-anchor="end" font-family="Arch" font-weight="600" font-size="28" fill="{fg}">{html.escape(data[-1][0])}</text>')
    return (f'<svg width="{W}" height="{H + 80}" style="margin-top:72px;overflow:visible">'
            f'<polyline points="{poly}" fill="none" stroke="{GOLD}" stroke-width="8" stroke-linejoin="round"/>{marks}{labs}</svg>'
            f'<div class="note">{html.escape(unit)}</div>')


def foot(theme, n, total):
    return (f'<div class="foot"><div class="mark"><div class="bub"><span style="color:{GOLD}">¿</span>'
            f'<span style="color:{PAPER}">Y</span><span style="color:{GOLD}">?</span></div><span>@yusted.queopina</span></div><span>{n}/{total}</span></div>')


def cerro(fill, w=1080, h=420):
    path = open(os.path.join(KIT, "cerro_silla.path")).read()
    return f'<svg viewBox="0 0 1080 420" width="{w}" height="{h}" style="display:block"><path d="{path}" fill="{fill}"/></svg>'


def colonia(fill, win=None):
    casas = [(0, 120, 90), (80, 150, 110), (180, 110, 80), (250, 170, 120), (360, 130, 95), (450, 160, 105), (545, 120, 85),
             (620, 175, 125), (735, 140, 100), (825, 160, 110), (925, 125, 90), (1005, 150, 90)]
    parts = []
    for x, bw, hh in casas:
        y = 260 - hh
        parts.append(f'<rect x="{x}" y="{y}" width="{bw}" height="{hh + 40}" fill="{fill}"/>'
                     f'<rect x="{x + bw * .62}" y="{y - 26}" width="26" height="26" rx="5" fill="{fill}"/>'  # tinaco
                     f'<rect x="{x + 10}" y="{y - 14}" width="4" height="14" fill="{fill}"/><rect x="{x + 24}" y="{y - 10}" width="4" height="10" fill="{fill}"/>')
        if win:
            parts.append(f'<rect x="{x + bw * .2}" y="{y + hh * .35}" width="18" height="22" fill="{win}"/>')
            if bw > 110:
                parts.append(f'<rect x="{x + bw * .5}" y="{y + hh * .35}" width="18" height="22" fill="{win}" opacity=".7"/>')
    cables = (f'<path d="M0 70 Q270 120 540 80 T1080 90" stroke="{fill}" stroke-width="3" fill="none"/>'
              f'<path d="M0 95 Q300 140 600 105 T1080 115" stroke="{fill}" stroke-width="2" fill="none"/>')
    return f'<svg viewBox="0 0 1080 300" width="1080" height="300" style="display:block">{cables}{"".join(parts)}</svg>'


TEMPORADAS = ("navidad",)  # adornos de portada; la rutina elige cuál según la fecha de publicación (GUIA.md)
CON_TEMPORADA = ("barda", "atardecer")  # noche es para notas serias: nunca lleva adorno
# Foquitos navideños sin rojo, verde ni naranja: esos colores se asocian con partidos.
FOCOS = (GOLD, PAPER, "#5FC2C9", "#7FA7E8", "#B8A2E3")


def guirnalda(top, sag, n, cable, borde=None, w=1080):
    """Cable con foquitos de colores de orilla a orilla: cuelga `sag` px en el centro."""
    y = lambda x: top + 4 * sag * (x / w) * (1 - x / w)
    out = [f'<path d="M0 {top} Q{w / 2} {top + 2 * sag} {w} {top}" stroke="{cable}" stroke-width="3" fill="none"/>']
    for i in range(n):
        x = (i + 0.5) * w / n
        cy = y(x) + 17
        color = FOCOS[i % len(FOCOS)]
        stroke = f' stroke="{borde}" stroke-width="2"' if borde else ""
        out.append(f'<circle cx="{x:.0f}" cy="{cy:.0f}" r="17" fill="{color}" opacity=".28"/>'
                   f'<rect x="{x - 4:.0f}" y="{y(x) - 1:.0f}" width="8" height="8" fill="{cable}"/>'
                   f'<ellipse cx="{x:.0f}" cy="{cy:.0f}" rx="7" ry="10" fill="{color}"{stroke}/>')
    return f'<svg width="{w}" height="{top + sag + 40}" style="display:block">{"".join(out)}</svg>'


def estrella(size, color=GOLD):
    """Estrella de cuatro picos con su brillo (la punta del pino)."""
    c, r, k = size / 2, size / 2, size * 0.09
    pts = f"{c},0 {c + k},{c - k} {size},{c} {c + k},{c + k} {c},{size} {c - k},{c + k} 0,{c} {c - k},{c - k}"
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" style="display:block;overflow:visible">'
            f'<circle cx="{c}" cy="{c}" r="{r * 0.55:.0f}" fill="{color}" opacity=".25"/><polygon points="{pts}" fill="{color}"/></svg>')


def pino(color, adornos, w=300, h=380):
    """Pino pintado con esténcil en la barda, con esferas y su estrella."""
    capas = [(60, 150, 20), (130, 230, 50), (210, 300, 85)]  # (y arriba, y abajo, media base): tres triángulos
    tri = "".join(f'<polygon points="{w / 2},{y0 - 50} {w / 2 + b + 40},{y1} {w / 2 - b - 40},{y1}" fill="{color}"/>'
                  for y0, y1, b in capas)
    tronco = f'<rect x="{w / 2 - 18}" y="300" width="36" height="52" fill="{color}"/>'
    esferas = "".join(f'<circle cx="{x}" cy="{y}" r="11" fill="{adornos[i % len(adornos)]}"/>'
                      for i, (x, y) in enumerate([(130, 120), (175, 140), (105, 205), (150, 225), (200, 200),
                                                  (85, 285), (135, 275), (185, 290), (225, 270)]))
    punta = estrella(48).replace("<svg ", f'<svg x="{w / 2 - 24:.0f}" y="-14" ', 1)  # svg anidado: x, y relativos
    return (f'<svg width="{w}" height="{h + 20}" viewBox="0 -20 {w} {h + 20}" style="display:block;overflow:visible">'
            f'{tri}{tronco}{esferas}{punta}</svg>')


def adorno(temporada, estilo, L):
    """Capa de temporada de la portada (detrás del texto). Solo barda y atardecer."""
    if temporada != "navidad" or estilo not in CON_TEMPORADA:
        return ""
    if estilo == "atardecer":
        # Arriba, foquitos de orilla a orilla; abajo, otra guirnalda sobre las azoteas de la colonia (más
        # arriba que "DESLIZA"). Nada a media altura: ahí cae el título, que puede ser de cuatro renglones.
        return (L("left:0;top:0", guirnalda(12, 44, 15, "#140C24"))
                + L("left:0;bottom:200px", guirnalda(8, 30, 11, NAVY)))
    return (L("left:0;top:0", guirnalda(10, 40, 15, NAVY, NAVY))
            + L("left:70px;top:760px;opacity:.42", pino(TEAL, (GOLD, NAVY))))


def escena(estilo, tipo, temporada=None):
    """Fondo de barrio detrás del contenido (z-index -1). tipo: cover | resumen | interior.
    temporada: adorno de la portada (solo tipo cover, ver TEMPORADAS)."""
    L = lambda css, inner="": f'<div style="position:absolute;z-index:-1;{css}">{inner}</div>'
    extra = adorno(temporada, estilo, L) if tipo == "cover" else ""
    if estilo == "atardecer":
        if tipo == "cover":
            return (L("left:-300px;bottom:250px;opacity:.95", cerro("#3A1F4D", 1300, 505))
                    + L("left:0;bottom:30px", colonia(NAVY)) + L(f"left:0;right:0;bottom:0;height:40px;background:{NAVY}") + extra)
        if tipo == "resumen":
            return L("left:0;bottom:-40px;opacity:.85", cerro("#2A1A45")) + L("left:0;bottom:-120px", colonia("#1A1030"))
        return L("left:0;bottom:-120px;opacity:.55", cerro("#2A1A45"))
    if estilo == "noche":
        stars = "".join(L(f"left:{(i * 97) % 1080}px;top:{(i * 53) % 520}px;width:{3 if i % 3 else 5}px;height:{3 if i % 3 else 5}px;border-radius:50%;background:#FFF;opacity:{0.4 + 0.15 * (i % 4)}")
                        for i in range(46))
        if tipo == "cover":
            focos = "".join(L(f"left:{40 + i * 95}px;top:{48 + int(((i - 5.5) ** 2))}px;width:22px;height:30px;border-radius:50% 50% 45% 45%;background:{GOLD};box-shadow:0 0 22px 8px rgba(212,160,23,.55)")
                            for i in range(12))
            cable = L("left:0;top:0", '<svg width="1080" height="140"><path d="M0 40 Q540 130 1080 40" stroke="#05080F" stroke-width="4" fill="none"/></svg>')
            return (stars + cable + focos + L("left:-300px;bottom:200px", cerro("#22386B", 1300, 505))
                    + L("left:0;bottom:30px", colonia("#05080F", GOLD)) + L("left:0;right:0;bottom:0;height:40px;background:#05080F"))
        if tipo == "resumen":
            return stars + L("left:0;bottom:-40px", cerro("#1A2A52")) + L("left:0;bottom:-120px", colonia("#05080F", GOLD))
        return stars + L("left:0;bottom:-120px;opacity:.8", cerro("#1A2A52"))
    if estilo == "barda":
        if tipo == "cover":  # mural del cerro pintado en la barda
            return L("left:-200px;bottom:-40px;opacity:.28", cerro(TEAL, 1300, 505)) + extra
        return L(f"left:56px;right:56px;top:56px;bottom:136px;background:{PAPER};border:14px solid {NAVY};box-shadow:10px 12px 0 rgba(0,0,0,.18)")
    return ""


COLAS_JS = """<script>
document.querySelectorAll('.globo').forEach(function(g){
  var svg=document.querySelector('svg.colas'), r=g.getBoundingClientRect();
  var cx=+g.dataset.cx, cy=+g.dataset.cy;
  var bx=Math.min(Math.max(cx, r.left+70), r.right-70), by=(cy>r.bottom)? r.bottom-8 : r.top+8;
  var dx=cx-bx, dy=cy-by, d=Math.sqrt(dx*dx+dy*dy), L=Math.min(d*0.8, 120); cx=bx+dx*L/d; cy=by+dy*L/d;
  var w=24, p=bx-w+','+by+' '+(bx+w)+','+by+' '+cx+','+cy;
  svg.insertAdjacentHTML('beforeend','<polygon points="'+p+'" fill="#fff" stroke="#111" stroke-width="5" stroke-linejoin="round"/>'
    +'<polygon points="'+(bx-w+6)+','+by+' '+(bx+w-6)+','+by+' '+((bx+cx)/2)+','+((by+cy)/2)+'" fill="#fff"/>');
});
</script>"""


def ul(items):
    return "<ul>" + "".join(f"<li>{fmt(p)}</li>" for p in items) + "</ul>" if items else ""


def slide(s, base_dir, seccion=None, estilo=None):
    t = s["tipo"]
    cover_theme = estilo or SECCIONES.get(seccion, "dark")
    theme = s.get("tema") or estilo or (cover_theme if t in ("portada", "cierre") else "dark" if t == "cita" else "light")
    tag = f'<div class="tag">{fmt(s.get("tag", ""))}</div>' if s.get("tag") else ""
    if t == "portada":
        art = ""
        if s.get("mapa"):
            m = s["mapa"]
            hi, base, stroke = ART[theme]
            art = f'<div class="art" style="right:-30px;bottom:120px;opacity:.95">{mexico(820, m.get("estados", []), base, hi, stroke)}</div>'
            if m.get("etiqueta"):
                art += f'<div class="art" style="right:88px;bottom:90px;font-weight:800;font-size:28px;letter-spacing:3px;color:{hi};z-index:2">{fmt(m["etiqueta"])}</div>'
        elif str(s.get("personaje", "")).startswith(("picos", "tio")):
            art = f'<div class="art" style="right:-30px;bottom:0;z-index:1"><img src="file://{tio_png(s["personaje"], circ=False)}" style="width:660px;display:block"></div>'
        elif s.get("rober") or s.get("personaje"):
            art = f'<div class="art" style="right:70px;bottom:120px">{rober(380, ART[theme][0], s.get("personaje", "rober"))}</div>'
        elif s.get("icono"):
            art = f'<div class="art" style="right:50px;bottom:110px;opacity:.95">{icon(s["icono"], 440, ART[theme][0], 1.3)}</div>'
        hero = f'<div class="hero">{fmt(s["cifra"])}</div>' if s.get("cifra") else ""
        head = (f'{tag}{hero}<div class="h1">{fmt(s["titulo"])}</div>'
                + (f'<div class="lead">{fmt(s["subtitulo"])}</div>' if s.get("subtitulo") else ""))
        if theme == "barda":
            head = f'<div class="rotulo">{head}</div>'
        body = (head + art + '<div class="swipe" style="margin-bottom:96px">DESLIZA →</div>')
    elif t == "dato":
        body = f'{tag}<div class="big">{fmt(s["cifra"])}</div><div class="lead" style="margin-top:16px">{fmt(s["texto"])}</div>{ul(s.get("puntos"))}'
    elif t == "lista":
        ic = f'<div style="margin-top:8px">{icon(s["icono"], 120, GOLD, 1.6)}</div>' if s.get("icono") else ""
        body = f'{tag}<div class="h2">{fmt(s["titulo"])}</div>{ul(s["puntos"])}{ic}'
    elif t in ("grafica", "linea"):
        fn = bars if t == "grafica" else line
        chart = (bars(s["barras"], s.get("unidad", ""), s.get("decimales", 1), theme, s.get("eje_cero", False)) if t == "grafica"
                 else line(s["puntos_serie"], s.get("unidad", ""), s.get("decimales", 1), theme))
        body = f'{tag}<div class="h2">{fmt(s["titulo"])}</div>{chart}' + (f'<div class="note">{fmt(s["nota"])}</div>' if s.get("nota") else "")
    elif t == "mapa":
        base = ART[theme][1] if theme in ESTILOS else "#D9DEE7" if theme == "light" else LINE
        body = (f'{tag}<div class="h2">{fmt(s["titulo"])}</div>'
                f'<div style="margin-top:40px">{mexico(904, s.get("estados", []), base, GOLD, ART[theme][2] if theme in ESTILOS else PAPER if theme == "light" else NAVY)}</div>'
                + (f'<div class="note" style="display:flex;align-items:center;gap:14px"><span style="width:26px;height:26px;background:{GOLD};display:inline-block"></span>{fmt(s["leyenda"])}</div>' if s.get("leyenda") else "")
                + (f'<div class="lead">{fmt(s["texto"])}</div>' if s.get("texto") else ""))
    elif t == "cita":
        body = (f'{tag}<div class="qmark">“</div><div class="quote">{fmt(s["texto"])}</div>'
                f'<div class="who">— {fmt(s["autor"])}</div>' + (f'<div class="ctx">{fmt(s["contexto"])}</div>' if s.get("contexto") else ""))
    elif t == "versus":
        def col(title, items, bg, fg):
            lis = "".join(f'<li style="font-size:32px">{fmt(p)}</li>' for p in items)
            cls = "vb" if bg == GOLD else ""
            return (f'<div class="{cls}" style="flex:1;background:{bg};color:{fg};padding:36px 32px">'
                    f'<div style="font-weight:800;font-size:30px;letter-spacing:3px">{fmt(title)}</div>'
                    f'<ul style="margin-top:28px;gap:26px">{lis}</ul></div>')
        dark_bg = NAVY if theme in CLAROS else LINE
        body = (f'{tag}<div class="h2">{fmt(s["titulo"])}</div>'
                f'<div style="display:flex;gap:24px;margin-top:44px">'
                f'{col(s.get("lado_a", "A FAVOR"), s["a_favor"], dark_bg, PAPER)}'
                f'{col(s.get("lado_b", "EN CONTRA"), s["en_contra"], GOLD, NAVY)}</div>')
    elif t == "foto":
        theme = s.get("tema") or estilo or "dark"
        src = os.path.join(base_dir, s["foto"])
        tmp = os.path.join(base_dir, f".foto_{abs(hash(src))}.png")
        estilizar(src, tmp, s.get("estilo", "duotono"), 1080, 760)
        cred = f'<div style="position:absolute;right:20px;top:728px;font-size:18px;color:{PAPER};background:rgba(15,35,64,.75);padding:4px 10px;z-index:3">{fmt(s["credito"])}</div>'
        body = (f'<img src="file://{tmp}" style="position:absolute;left:0;top:0;width:1080px;height:760px">{cred}'
                f'<div style="margin-top:700px;position:relative;z-index:2;display:flex">{tag}</div>'
                f'<div class="h2" style="margin-top:28px;font-size:64px">{fmt(s["titulo"])}</div>'
                + (f'<div class="lead" style="font-size:34px;margin-top:20px">{fmt(s["texto"])}</div>' if s.get("texto") else "")
                + ('<div class="swipe" style="margin-bottom:150px">DESLIZA →</div>' if s.get("swipe") else ""))
    elif t == "resumen":
        theme = s.get("tema") or estilo or "brief"
        avatar = f'<div style="position:absolute;right:88px;bottom:120px;z-index:3">{rober(240, GOLD, s.get("personaje", "rober"))}</div>' if (s.get("rober") or s.get("personaje")) else ""
        items = "".join(f'<div class="ritem"><div class="rnum">{i}</div><div class="rtxt">{fmt(h)}</div></div>'
                        for i, h in enumerate(s["titulares"], 1))
        body = (('<div class="rband"></div>' if theme == "brief" else "") + f'<div class="rtitle">{fmt(s.get("titulo", "LAS 5 DE HOY"))}</div>'
                f'<div class="rdate">{fmt(s["fecha"])}</div>{avatar}<div class="rlist">{items}</div>'
                '<div class="swipe" style="margin-bottom:96px">DESLIZA →</div>')
    elif t in ("rober", "personaje"):
        quien = s.get("quien", "rober")
        theme = s.get("tema") or estilo or "dark"
        bubble_bg, bubble_fg = (NAVY, PAPER) if theme in CLAROS or theme == "gold" else (PAPER, NAVY)
        body = (f'{tag}<div style="margin-top:56px;position:relative;background:{bubble_bg};color:{bubble_fg};border-radius:36px;padding:48px 52px">'
                f'<div style="font-family:SS4,serif;font-weight:700;font-size:58px;line-height:1.22">{fmt(s["texto"])}</div>'
                f'<div style="position:absolute;left:120px;bottom:-44px;border-left:30px solid transparent;border-right:30px solid transparent;border-top:46px solid {bubble_bg}"></div></div>'
                f'<div style="display:flex;align-items:center;gap:30px;margin-top:80px">{rober(200, GOLD, quien)}'
                f'<div><div style="font-weight:800;font-size:38px;letter-spacing:1px">{PERSONAJES.get(quien.split(":")[0], quien)}</div>'
                f'<div style="font-size:28px;opacity:.75;margin-top:6px">{fmt(s.get("firma", FIRMAS.get(quien.split(":")[0], "")))}</div></div></div>')
    elif t == "nota":
        theme = s.get("tema") or estilo or "brief"
        body = (f'{tag}<div class="nnum">{s["numero"]}</div><div class="h2" style="margin-top:20px">{fmt(s["titular"])}</div>'
                f'<div class="lead">{fmt(s["texto"])}</div><div class="nsrc">Fuente: {fmt(s["fuente"])}</div>')
    elif t == "vineta":
        src = os.path.join(base_dir, s["imagen"])
        globos = "".join(
            f'<div class="globo" data-cx="{g["cola"][0]}" data-cy="{g["cola"][1]}" style="left:{g["x"]}px;top:{g["y"]}px;width:{g["w"]}px">{fmt(g["texto"])}</div>'
            for g in s.get("globos", []))
        head = ""
        if s.get("titulo"):
            head = (f'<div style="position:absolute;left:60px;top:56px;right:60px;z-index:6">'
                    + (f'<div style="font-family:Pirata,serif;font-size:60px;color:{GOLD};text-shadow:0 3px 10px rgba(0,0,0,.6)">{fmt(s["tag"])}</div>' if s.get("tag") else "")
                    + f'<div class="vtit">{fmt(s["titulo"])}</div></div>')
        neta = ""
        if s.get("neta"):
            n = s["neta"]
            neta = (f'<div class="neta"><div class="netat">LA NETA</div><div>{fmt(n["texto"])}</div>'
                    + (f'<div class="netaf">Fuente: {fmt(n["fuente"])}</div>' if n.get("fuente") else "") + '</div>')
        fuentes = f'<div class="neta" style="font-size:22px;padding:16px 24px">Fuentes: {fmt(s["fuentes"])}</div>' if s.get("fuentes") else ""
        body = (f'<img src="file://{src}" style="position:absolute;left:0;top:0;width:1080px;height:1350px;z-index:-2">'
                '<div style="position:absolute;left:0;right:0;bottom:0;height:200px;background:linear-gradient(transparent,rgba(10,10,25,.85));z-index:-1"></div>'
                f'<svg class="colas" width="1080" height="1350" style="position:absolute;left:0;top:0;z-index:4;overflow:visible"></svg>{head}{globos}{neta}{fuentes}'
                + ('<div class="swipe" style="position:absolute;left:60px;bottom:60px;margin:0;font-family:Bebas,sans-serif;font-weight:400;font-size:44px;letter-spacing:4px;color:#fff;text-shadow:0 2px 8px #000;z-index:6">DESLIZA →</div>' if s.get("titulo") else "")
                + COLAS_JS)
        theme = "noche"
    elif t == "cierre":
        body = (f'<div class="tag">{fmt(s.get("tag", "LES TOCA"))}</div><div class="h1">{fmt(s["titulo"])}</div>'
                f'<div class="lead">{fmt(s["texto"])}</div><div class="src">Fuentes: {fmt(s["fuentes"])}</div>')
    else:
        raise ValueError(f"tipo desconocido: {t}")
    return theme, body


def main(spec_path):
    spec = json.load(open(spec_path))
    out_dir = os.path.dirname(os.path.abspath(spec_path))
    slides = spec["slides"]
    temporada = spec.get("temporada")
    if temporada and temporada not in TEMPORADAS:
        raise ValueError(f"temporada desconocida: {temporada} (usa {TEMPORADAS})")
    if temporada and spec.get("estilo") not in CON_TEMPORADA:
        print(f"aviso: la temporada {temporada} no se dibuja en estilo {spec.get('estilo')} (solo {CON_TEMPORADA})", file=sys.stderr)
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            estilo = spec.get("estilo")
            if estilo and estilo not in ESTILOS:
                raise ValueError(f"estilo desconocido: {estilo} (usa {ESTILOS})")
            theme, body = slide(s, out_dir, spec.get("seccion"), estilo)
            cover = i == 1 and s["tipo"] in ("portada", "foto", "resumen", "vineta")
            if theme in ESTILOS and s["tipo"] not in ("foto", "vineta"):
                tipo = "resumen" if s["tipo"] == "resumen" else "cover" if s["tipo"] == "portada" else "interior"
                body = escena(theme, tipo, temporada) + body
            doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
                   f'<body><div class="s {theme}{" cover" if cover else ""}">{body}{"" if cover else foot(theme, i, len(slides))}</div></body></html>')
            tmp = os.path.join(out_dir, f".{spec['post']}_{i}.html")
            open(tmp, "w").write(doc)
            pg.goto("file://" + tmp)
            pg.wait_for_timeout(300)
            png = os.path.join(out_dir, f"{spec['post']}_{i}.jpg")  # Instagram vía TARDIS solo acepta JPEG
            pg.screenshot(path=png, type="jpeg", quality=92, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            os.remove(tmp)
            files.append(png)
        b.close()
    for f in os.listdir(out_dir):
        if f.startswith(".foto_"):
            os.remove(os.path.join(out_dir, f))
    print("\n".join(files))


if __name__ == "__main__":
    main(sys.argv[1])
