"""Generador de diapositivas de @yusted.queopina (Instagram, 1080x1350).

Uso:  python3 kit/generar.py lotes/2026-10-11/peso.json
Sale: los PNG junto al JSON (peso_1.png, peso_2.png, ...).

Formato del JSON (ver kit/ejemplo.json):
{"post": "peso", "seccion": "economia", "slides": [ {"tipo": "...", ...}, ... ]}
seccion: politica (azul) | economia (crema) | debate (dorado) | analisis (negro). Define el color de portada y cierre.

Tipos de diapositiva:
  portada  tag, titulo, cifra? (número gigante, ej. "70%"), subtitulo?, icono? (nombre lucide) o mapa? {"estados":[ids], "etiqueta":?}
  dato     tag, cifra, texto, puntos?
  lista    tag, titulo, puntos
  grafica  tag, titulo, barras [[etiqueta, valor], ...], unidad, decimales?, nota?
  linea    tag, titulo, puntos_serie [[etiqueta, valor], ...], unidad, decimales?, nota?
  mapa     tag, titulo, estados [ids], texto?, leyenda?
  cita     texto, autor, contexto?
  versus   tag, titulo, a_favor [..], en_contra [..], lado_a?, lado_b?  (para posts de DEBATE)
  foto     foto (ruta relativa al JSON), estilo? (duotono|poster|grabado), credito, tag?, titulo, texto?, swipe? (true si es portada)
  cierre   titulo, texto, fuentes, tag? (por defecto "SU TURNO")
Todas aceptan "tema": "dark" | "light" | "gold" | "black" (cada tipo tiene su valor por defecto).
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
SECCIONES = {"politica": "dark", "economia": "light", "debate": "gold", "analisis": "black"}
ART = {  # (color de ícono/realce, base del mapa, trazo del mapa)
    "dark": (GOLD, LINE, NAVY), "light": (GOLD, "#D9DEE7", PAPER),
    "gold": (NAVY, "#E3B83F", GOLD), "black": (GOLD, "#2E2E2E", INK)}
MAP = json.load(open(os.path.join(KIT, "mexico_map.json")))

CSS = f"""
@font-face{{font-family:'SS4';src:url('file://{KIT}/fonts/SourceSerif4.ttf');font-weight:200 900}}
@font-face{{font-family:'Arch';src:url('file://{KIT}/fonts/Archivo.ttf');font-weight:100 900}}
html,body{{margin:0}}
.s{{width:1080px;height:1350px;box-sizing:border-box;padding:96px 88px 0;position:relative;overflow:hidden;font-family:'Arch',sans-serif;display:flex;flex-direction:column}}
.dark{{background:{NAVY};color:{PAPER}}} .light{{background:{PAPER};color:{NAVY}}}
.gold{{background:{GOLD};color:{NAVY}}} .black{{background:{INK};color:{PAPER}}}
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


def bars(data, unit, dec, theme):
    fg = NAVY if theme == "light" else PAPER
    vmax = max(v for _, v in data)
    vmin = min(v for _, v in data)
    floor = 0 if vmin < vmax * 0.5 else vmin * 0.9   # recorta el eje si las barras son parecidas
    W, H, gap = 900, 560, 40
    bw = (W - gap * (len(data) - 1)) / len(data)
    out = []
    for i, (lab, v) in enumerate(data):
        h = max(8, (v - floor) / (vmax - floor) * (H - 90))
        x = i * (bw + gap)
        col = GOLD if i == len(data) - 1 else (LINE if theme == "dark" else "#B9C2D3")
        out.append(f'<rect x="{x}" y="{H - h}" width="{bw}" height="{h}" fill="{col}"/>'
                   f'<text x="{x + bw/2}" y="{H - h - 20}" text-anchor="middle" font-family="SS4" font-weight="900" font-size="54" fill="{fg}">{v:.{dec}f}</text>'
                   f'<text x="{x + bw/2}" y="{H + 48}" text-anchor="middle" font-family="Arch" font-weight="600" font-size="30" fill="{fg}">{html.escape(lab)}</text>')
    axis = "" if floor == 0 else f'<text x="0" y="{H + 92}" font-family="Arch" font-size="22" fill="{fg}" opacity=".6">Eje recortado: empieza en {floor:.{dec}f}</text>'
    return (f'<svg width="{W}" height="{H + 100}" style="margin-top:56px;overflow:visible">{"".join(out)}'
            f'<line x1="0" y1="{H}" x2="{W}" y2="{H}" stroke="{fg}" stroke-width="2"/>{axis}</svg>'
            f'<div class="note">{html.escape(unit)}</div>')


def line(data, unit, dec, theme):
    fg = NAVY if theme == "light" else PAPER
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


def ul(items):
    return "<ul>" + "".join(f"<li>{fmt(p)}</li>" for p in items) + "</ul>" if items else ""


def slide(s, base_dir, seccion=None):
    t = s["tipo"]
    cover_theme = SECCIONES.get(seccion, "dark")
    theme = s.get("tema") or (cover_theme if t in ("portada", "cierre") else "dark" if t == "cita" else "light")
    tag = f'<div class="tag">{fmt(s.get("tag", ""))}</div>' if s.get("tag") else ""
    if t == "portada":
        art = ""
        if s.get("mapa"):
            m = s["mapa"]
            hi, base, stroke = ART[theme]
            art = f'<div class="art" style="right:-30px;bottom:120px;opacity:.95">{mexico(820, m.get("estados", []), base, hi, stroke)}</div>'
            if m.get("etiqueta"):
                art += f'<div class="art" style="right:88px;bottom:90px;font-weight:800;font-size:28px;letter-spacing:3px;color:{hi};z-index:2">{fmt(m["etiqueta"])}</div>'
        elif s.get("icono"):
            art = f'<div class="art" style="right:50px;bottom:110px;opacity:.95">{icon(s["icono"], 440, ART[theme][0], 1.3)}</div>'
        hero = f'<div class="hero">{fmt(s["cifra"])}</div>' if s.get("cifra") else ""
        body = (f'{tag}{hero}<div class="h1">{fmt(s["titulo"])}</div>'
                + (f'<div class="lead">{fmt(s["subtitulo"])}</div>' if s.get("subtitulo") else "")
                + art + '<div class="swipe" style="margin-bottom:96px">DESLICE →</div>')
    elif t == "dato":
        body = f'{tag}<div class="big">{fmt(s["cifra"])}</div><div class="lead" style="margin-top:16px">{fmt(s["texto"])}</div>{ul(s.get("puntos"))}'
    elif t == "lista":
        ic = f'<div style="margin-top:8px">{icon(s["icono"], 120, GOLD, 1.6)}</div>' if s.get("icono") else ""
        body = f'{tag}<div class="h2">{fmt(s["titulo"])}</div>{ul(s["puntos"])}{ic}'
    elif t in ("grafica", "linea"):
        fn = bars if t == "grafica" else line
        chart = fn(s["barras"] if t == "grafica" else s["puntos_serie"], s.get("unidad", ""), s.get("decimales", 1), theme)
        body = f'{tag}<div class="h2">{fmt(s["titulo"])}</div>{chart}' + (f'<div class="note">{fmt(s["nota"])}</div>' if s.get("nota") else "")
    elif t == "mapa":
        base = "#D9DEE7" if theme == "light" else LINE
        body = (f'{tag}<div class="h2">{fmt(s["titulo"])}</div>'
                f'<div style="margin-top:40px">{mexico(904, s.get("estados", []), base, GOLD, PAPER if theme == "light" else NAVY)}</div>'
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
        dark_bg = NAVY if theme == "light" else LINE
        body = (f'{tag}<div class="h2">{fmt(s["titulo"])}</div>'
                f'<div style="display:flex;gap:24px;margin-top:44px">'
                f'{col(s.get("lado_a", "A FAVOR"), s["a_favor"], dark_bg, PAPER)}'
                f'{col(s.get("lado_b", "EN CONTRA"), s["en_contra"], GOLD, NAVY)}</div>')
    elif t == "foto":
        theme = s.get("tema") or "dark"
        src = os.path.join(base_dir, s["foto"])
        tmp = os.path.join(base_dir, f".foto_{abs(hash(src))}.png")
        estilizar(src, tmp, s.get("estilo", "duotono"), 1080, 760)
        cred = f'<div style="position:absolute;right:20px;top:728px;font-size:18px;color:{PAPER};background:rgba(15,35,64,.75);padding:4px 10px;z-index:3">{fmt(s["credito"])}</div>'
        body = (f'<img src="file://{tmp}" style="position:absolute;left:0;top:0;width:1080px;height:760px">{cred}'
                f'<div style="margin-top:700px;position:relative;z-index:2;display:flex">{tag}</div>'
                f'<div class="h2" style="margin-top:28px;font-size:64px">{fmt(s["titulo"])}</div>'
                + (f'<div class="lead" style="font-size:34px;margin-top:20px">{fmt(s["texto"])}</div>' if s.get("texto") else "")
                + ('<div class="swipe" style="margin-bottom:150px">DESLICE →</div>' if s.get("swipe") else ""))
    elif t == "cierre":
        body = (f'<div class="tag">{fmt(s.get("tag", "SU TURNO"))}</div><div class="h1">{fmt(s["titulo"])}</div>'
                f'<div class="lead">{fmt(s["texto"])}</div><div class="src">Fuentes: {fmt(s["fuentes"])}</div>')
    else:
        raise ValueError(f"tipo desconocido: {t}")
    return theme, body


def main(spec_path):
    spec = json.load(open(spec_path))
    out_dir = os.path.dirname(os.path.abspath(spec_path))
    slides = spec["slides"]
    files = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            theme, body = slide(s, out_dir, spec.get("seccion"))
            cover = i == 1 and s["tipo"] in ("portada", "foto")
            doc = (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
                   f'<body><div class="s {theme}{" cover" if cover else ""}">{body}{"" if cover else foot(theme, i, len(slides))}</div></body></html>')
            tmp = os.path.join(out_dir, f".{spec['post']}_{i}.html")
            open(tmp, "w").write(doc)
            pg.goto("file://" + tmp)
            pg.wait_for_timeout(300)
            png = os.path.join(out_dir, f"{spec['post']}_{i}.png")
            pg.screenshot(path=png, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            os.remove(tmp)
            files.append(png)
        b.close()
    for f in os.listdir(out_dir):
        if f.startswith(".foto_"):
            os.remove(os.path.join(out_dir, f))
    print("\n".join(files))


if __name__ == "__main__":
    main(sys.argv[1])
