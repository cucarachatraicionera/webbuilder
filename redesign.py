#!/usr/bin/env python3
"""
Rediseño completo: 5 temas distintos para 10 negocios.
Cada sitio tiene diseño único, profesional, con colores, tipografías y layouts diferenciados.
"""
import json, re, shutil, subprocess, functools
from pathlib import Path

print = functools.partial(print, flush=True)

BASE = Path(__file__).parent.resolve()
DATA_DIR = BASE / "negocios"
SITES = BASE / "sitios-web"
DEPLOY = BASE / "deploy"

C = {"cy":"\033[96m","gr":"\033[92m","ye":"\033[93m","re":"\033[91m","bo":"\033[1m","en":"\033[0m"}
p = lambda c,t: f"{C.get(c,'')}{t}{C['en']}"

BUSINESSES = [
    {"name": "Almacenes Oportunidades", "theme": 0,
     "colors": {"p":"#1a56db","s":"#7c3aed","a":"#f59e0b","bg":"#ffffff","tx":"#1f2937","tx2":"#6b7280","sf":"#f9fafb","sf2":"#f3f4f6"},
     "font": "'Inter', system-ui, sans-serif", "hero_layout": "left", "card_style": "shadow"},
    {"name": "Ranchero Rústico Paisa", "theme": 1,
     "colors": {"p":"#b91c1c","s":"#7f1d1d","a":"#fbbf24","bg":"#faf5f0","tx":"#292524","tx2":"#78716c","sf":"#f5f0ea","sf2":"#efe6d8"},
     "font": "'Playfair Display', Georgia, serif", "hero_layout": "full", "card_style": "bordered"},
    {"name": "La Postrera Campestre", "theme": 2,
     "colors": {"p":"#059669","s":"#065f46","a":"#f97316","bg":"#f0fdf4","tx":"#1c1917","tx2":"#78716c","sf":"#f0fdf4","sf2":"#dcfce7"},
     "font": "'DM Serif Display', serif", "hero_layout": "right", "card_style": "rounded"},
    {"name": "Compañía Cafetera La Meseta S.A.S", "theme": 3,
     "colors": {"p":"#7c3aed","s":"#4c1d95","a":"#d97706","bg":"#0c0a09","tx":"#fafaf9","tx2":"#a8a29e","sf":"#1c1917","sf2":"#292524"},
     "font": "'Space Grotesk', system-ui, sans-serif", "hero_layout": "center", "card_style": "glass"},
    {"name": "Zumo&Humo", "theme": 4,
     "colors": {"p":"#e11d48","s":"#be123c","a":"#facc15","bg":"#09090b","tx":"#fafafa","tx2":"#a1a1aa","sf":"#18181b","sf2":"#27272a"},
     "font": "'DM Sans', system-ui, sans-serif", "hero_layout": "split", "card_style": "border-accent"},
    {"name": "Parque Ecológico Fundación Salva el Amazonas", "theme": 2,
     "colors": {"p":"#16a34a","s":"#15803d","a":"#22d3ee","bg":"#f0fdf4","tx":"#1c1917","tx2":"#78716c","sf":"#f0fdf4","sf2":"#dcfce7"},
     "font": "'DM Serif Display', serif", "hero_layout": "center", "card_style": "rounded"},
    {"name": "La Tarima Cafe Cultural", "theme": 1,
     "colors": {"p":"#d97706","s":"#92400e","a":"#fcd34d","bg":"#fffbeb","tx":"#292524","tx2":"#78716c","sf":"#fef3c7","sf2":"#fde68a"},
     "font": "'Playfair Display', Georgia, serif", "hero_layout": "right", "card_style": "bordered"},
    {"name": "Diez de10 Coffee & Brunch", "theme": 0,
     "colors": {"p":"#0891b2","s":"#0e7490","a":"#fbbf24","bg":"#ffffff","tx":"#1f2937","tx2":"#6b7280","sf":"#f9fafb","sf2":"#f3f4f6"},
     "font": "'Inter', system-ui, sans-serif", "hero_layout": "right", "card_style": "shadow"},
    {"name": "Supermercado El Campesino", "theme": 3,
     "colors": {"p":"#4f46e5","s":"#3730a3","a":"#22c55e","bg":"#0c0a09","tx":"#fafaf9","tx2":"#a8a29e","sf":"#1c1917","sf2":"#292524"},
     "font": "'Space Grotesk', system-ui, sans-serif", "hero_layout": "left", "card_style": "glass"},
    {"name": "MonRut Café", "theme": 4,
     "colors": {"p":"#a21caf","s":"#701a75","a":"#e879f9","bg":"#09090b","tx":"#fafafa","tx2":"#a1a1aa","sf":"#18181b","sf2":"#27272a"},
     "font": "'DM Sans', system-ui, sans-serif", "hero_layout": "center", "card_style": "border-accent"},
]

# ─── HELPERS ─────────────────────────────────────────────────

def slugify(name):
    s = re.sub(r'[^\w\s-]', '', name).strip().lower().replace(" ", "-")
    return re.sub(r'-+', '-', s)[:40]

def ascii_slug(name):
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n')]:
        name = name.replace(a, b)
    return name

def load_data(name):
    safe = re.sub(r'[^\w\s-]', '', name).strip().replace(" ", "_")
    safe = re.sub(r'_+', '_', safe)[:60]
    biz_dir = DATA_DIR / safe
    if not (biz_dir / "info.json").exists():
        return None
    data = json.loads((biz_dir / "info.json").read_text(encoding="utf-8"))
    pd = biz_dir / "fotos"
    fotos = sorted(pd.iterdir()) if pd.exists() else []
    data["_photos"] = [f"/{f.name}" for f in fotos]
    return data

# ─── CSS GENERATION ───────────────────────────────────────────

def generate_css(b):
    c = b["colors"]
    t = b["theme"]
    f = b["font"]

    themes = [None] * 5

    themes[0] = """
:root {
  --p: PCOL; --s: SCOL; --a: ACOL;
  --bg: BGCOL; --tx: TXCOL; --tx2: TX2COL; --sf: SFCOL; --sf2: SF2COL;
  --font: FONT;
  --radius: 12px;
  --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-lg: 0 10px 25px rgba(0,0,0,0.06), 0 4px 10px rgba(0,0,0,0.04);
}
body { font-family: var(--font); background: var(--bg); color: var(--tx); }
.card { background: white; border-radius: var(--radius); box-shadow: var(--shadow); padding: 2rem; transition: box-shadow 0.3s, transform 0.3s; }
.card:hover { box-shadow: var(--shadow-lg); transform: translateY(-2px); }
"""

    themes[1] = """
:root {
  --p: PCOL; --s: SCOL; --a: ACOL;
  --bg: BGCOL; --tx: TXCOL; --tx2: TX2COL; --sf: SFCOL; --sf2: SF2COL;
  --font: FONT;
  --radius: 4px;
}
body { font-family: var(--font); background: var(--bg); color: var(--tx); }
.card { background: var(--sf); border: 1px solid var(--sf2); padding: 2rem; transition: all 0.3s; }
.card:hover { border-color: var(--p); }
"""

    themes[2] = """
:root {
  --p: PCOL; --s: SCOL; --a: ACOL;
  --bg: BGCOL; --tx: TXCOL; --tx2: TX2COL; --sf: SFCOL; --sf2: SF2COL;
  --font: FONT;
  --radius: 24px;
}
body { font-family: var(--font); background: var(--bg); color: var(--tx); }
.card { background: white; border-radius: var(--radius); padding: 2rem; transition: all 0.4s; box-shadow: 0 4px 20px rgba(0,0,0,0.04); }
.card:hover { transform: translateY(-4px) scale(1.01); box-shadow: 0 12px 40px rgba(5,150,105,0.1); }
"""

    themes[3] = """
:root {
  --p: PCOL; --s: SCOL; --a: ACOL;
  --bg: BGCOL; --tx: TXCOL; --tx2: TX2COL; --sf: SFCOL; --sf2: SF2COL;
  --font: FONT;
  --radius: 16px;
}
body { font-family: var(--font); background: var(--bg); color: var(--tx); }
.card { background: var(--sf); border: 1px solid var(--sf2); border-radius: var(--radius); padding: 2rem; backdrop-filter: blur(12px); transition: all 0.3s; }
.card:hover { border-color: var(--p); box-shadow: 0 0 30px rgba(124,58,237,0.1); }
"""

    themes[4] = """
:root {
  --p: PCOL; --s: SCOL; --a: ACOL;
  --bg: BGCOL; --tx: TXCOL; --tx2: TX2COL; --sf: SFCOL; --sf2: SF2COL;
  --font: FONT;
  --radius: 0px;
}
body { font-family: var(--font); background: var(--bg); color: var(--tx); }
.card { background: var(--sf); border-left: 3px solid var(--p); padding: 2rem; transition: all 0.3s; }
.card:hover { background: var(--sf2); transform: translateX(4px); }
"""

    css = themes[t]
    css = css.replace("PCOL", c['p']).replace("SCOL", c['s']).replace("ACOL", c['a'])
    css = css.replace("BGCOL", c['bg']).replace("TXCOL", c['tx']).replace("TX2COL", c['tx2'])
    css = css.replace("SFCOL", c['sf']).replace("SF2COL", c['sf2']).replace("FONT", f)

    extra = """
* { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
img { max-width: 100%; height: auto; }
a { text-decoration: none; color: inherit; }

.btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.75rem; border-radius: var(--radius); font-weight: 600; font-size: 0.9rem; transition: all 0.2s; cursor: pointer; border: none; text-decoration: none; }
.btn-primary { background: var(--p); color: white; }
.btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
.btn-outline { border: 2px solid var(--p); color: var(--p); background: transparent; }
.btn-outline:hover { background: var(--p); color: white; }
.section { padding: 5rem 0; }
.section-alt { background: var(--sf); }
.container { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; }
.tag { display: inline-block; padding: 0.3rem 0.9rem; border-radius: 100px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; background: color-mix(in srgb, var(--p) 12%, transparent); color: var(--p); margin-bottom: 1rem; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
@media (max-width: 768px) { .grid-2, .grid-3 { grid-template-columns: 1fr; } .section { padding: 3rem 0; } }
h2 { font-size: clamp(1.8rem, 4vw, 2.8rem); font-weight: 800; line-height: 1.15; }
h2 .hl { background: linear-gradient(135deg, var(--p), var(--a)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; padding: 0 1.5rem; transition: all 0.3s; }
nav.scrolled { background: var(--bg); box-shadow: 0 1px 10px rgba(0,0,0,0.05); }
nav .inner { max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; height: 4rem; }
nav .logo { font-weight: 800; font-size: 1.2rem; }
nav .links { display: flex; gap: 2rem; align-items: center; }
nav .links a { font-size: 0.85rem; color: var(--tx2); transition: color 0.2s; font-weight: 500; }
nav .links a:hover { color: var(--p); }
.mobile-toggle { display: none; background: none; border: none; color: var(--tx); cursor: pointer; padding: 0.5rem; }
@media (max-width: 768px) { .mobile-toggle { display: block; } nav .links { display: none; } nav .links.open { display: flex; flex-direction: column; position: absolute; top: 4rem; left: 0; right: 0; background: var(--bg); padding: 1.5rem; gap: 1rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); } }

.hero { min-height: 100vh; display: flex; align-items: center; position: relative; overflow: hidden; }
.hero-left { padding-top: 6rem; }
.hero-right { text-align: right; }
.hero-center { text-align: center; }
.hero-full { position: relative; }
.hero-full .content { position: relative; z-index: 2; }
.hero-split { display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh; }
.hero-split .text { display: flex; flex-direction: column; justify-content: center; padding: 6rem 2rem 2rem 4rem; }
.hero-split .visual { background: linear-gradient(135deg, var(--p), var(--s)); display: flex; align-items: center; justify-content: center; }
.hero h1 { font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 900; line-height: 1.05; margin-bottom: 1.5rem; }
.hero p { font-size: clamp(1rem, 2vw, 1.2rem); color: var(--tx2); max-width: 540px; line-height: 1.6; margin-bottom: 2rem; }
.hero-center p { margin-left: auto; margin-right: auto; }
.hero-right p { margin-left: auto; }
.hero .actions { display: flex; gap: 1rem; flex-wrap: wrap; }
.hero-center .actions { justify-content: center; }
.hero-right .actions { justify-content: flex-end; }
@media (max-width: 768px) { .hero-split { grid-template-columns: 1fr; } .hero-split .visual { min-height: 40vh; } .hero-split .text { padding: 6rem 1.5rem 2rem; } .hero { padding-top: 4rem; } }

.about-icon { width: 3rem; height: 3rem; display: flex; align-items: center; justify-content: center; border-radius: var(--radius); margin-bottom: 1rem; font-size: 1.3rem; }
.text-center { text-align: center; }
.mb-1 { margin-bottom: 1rem; } .mb-2 { margin-bottom: 2rem; } .mb-3 { margin-bottom: 3rem; }
.mt-2 { margin-top: 2rem; }
.gap-1 { gap: 1rem; } .gap-2 { gap: 2rem; }

.gallery-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.gallery-grid img { width: 100%; aspect-ratio: 4/3; object-fit: cover; border-radius: var(--radius); transition: transform 0.5s; }
.gallery-grid img:hover { transform: scale(1.03); }
@media (max-width: 768px) { .gallery-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .gallery-grid { grid-template-columns: 1fr; } }

.location-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-items: center; }
.info-item { display: flex; align-items: flex-start; gap: 1rem; padding: 1rem; border-radius: var(--radius); }
.info-icon { width: 2.5rem; height: 2.5rem; display: flex; align-items: center; justify-content: center; border-radius: var(--radius); flex-shrink: 0; }
.info-text h4 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--tx2); margin-bottom: 0.25rem; }
.info-text p, .info-text a { font-size: 0.95rem; color: var(--tx); }
.map-wrap { border-radius: var(--radius); overflow: hidden; height: 400px; }
.map-wrap iframe { width: 100%; height: 100%; border: 0; }
@media (max-width: 768px) { .location-grid { grid-template-columns: 1fr; } .map-wrap { height: 300px; } }

.stars { color: var(--a); display: flex; gap: 2px; margin-bottom: 0.75rem; }
.contact-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.social-links { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.social-link { width: 2.75rem; height: 2.75rem; display: flex; align-items: center; justify-content: center; border-radius: var(--radius); transition: all 0.2s; color: var(--tx2); background: var(--sf2); }
.social-link:hover { background: var(--p); color: white; }
@media (max-width: 768px) { .contact-grid { grid-template-columns: 1fr; } }

footer { padding: 3rem 0; border-top: 1px solid var(--sf2); }
footer .inner { max-width: 1200px; margin: 0 auto; padding: 0 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; }
footer .copy { font-size: 0.85rem; color: var(--tx2); }

.whatsapp-float { position: fixed; bottom: 1.5rem; right: 1.5rem; z-index: 99; width: 3.5rem; height: 3.5rem; border-radius: 50%; background: #25D366; color: white; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(37,211,102,0.3); transition: transform 0.2s; }
.whatsapp-float:hover { transform: scale(1.1); }
.scroll-top { position: fixed; bottom: 1.5rem; left: 1.5rem; z-index: 99; width: 2.75rem; height: 2.75rem; border-radius: 50%; background: var(--p); color: white; display: flex; align-items: center; justify-content: center; cursor: pointer; border: none; opacity: 0; transition: opacity 0.3s; }
.scroll-top.visible { opacity: 1; }
"""
    return css + extra

# ─── APP TSX GENERATION ───────────────────────────────────────

def generate_app(b, idx):
    name = b["name"]
    data = load_data(name)
    if not data:
        return None

    biz_safe = re.sub(r'[^\w\s-]', '', name).strip().replace(" ", "_")
    src_photos = DATA_DIR / biz_safe / "fotos"
    photos = [f"{f.name}" for f in sorted(src_photos.iterdir())] if src_photos.exists() else []

    embed = {
        "name": name, "address": data.get("address", ""), "phone": data.get("phone", ""),
        "website": data.get("website", ""), "rating": data.get("rating", 0),
        "rating_total": data.get("rating_total", 0), "reviews": data.get("reviews", [])[:3],
        "social": data.get("social_media", {}), "whatsapp": data.get("social_media", {}).get("whatsapp", ""),
        "hero_img": photos[0] if photos else "", "gallery_imgs": photos,
    }
    data_json = json.dumps(embed, ensure_ascii=False)

    REACT_SECTION_NAMES = """const SECTIONS = [
  { href: "#inicio", label: "Inicio" },
  { href: "#nosotros", label: "Nosotros" },
  { href: "#galeria", label: "Galer\u00eda" },
  { href: "#ubicacion", label: "Ubicaci\u00f3n" },
  { href: "#contacto", label: "Contacto" },
]"""

    SOCIAL_MAP = """const SOCIAL_ICONS: Record<string, any> = {
  facebook: Facebook, instagram: Instagram, youtube: Youtube,
  twitter: Twitter, linkedin: Linkedin, tiktok: Music2, whatsapp: MessageCircle,
}"""

    HEADER = 'import { useState, useEffect } from "react"\nimport { motion, AnimatePresence } from "framer-motion"\nimport { Menu, X, MapPin, Phone, Globe, Star, ArrowUp, ChevronRight, ExternalLink, Facebook, Instagram, Youtube, Twitter, Linkedin, Music2, MessageCircle, Award, Heart } from "lucide-react"'

    return HEADER + """

const DATA = """ + data_json + """;
""" + REACT_SECTION_NAMES + """
""" + SOCIAL_MAP + """

function Navbar() {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  useEffect(() => {
    const f = () => setScrolled(window.scrollY > 50)
    window.addEventListener("scroll", f)
    return () => window.removeEventListener("scroll", f)
  }, [])
  return (
    <nav className={scrolled ? "scrolled" : ""}>
      <div className="inner">
        <a href="#inicio" className="logo" style={{color: "var(--p)"}}>{DATA.name}</a>
        <div className={"links" + (open ? " open" : "")}>
          {SECTIONS.map(s => (
            <a key={s.href} href={s.href} onClick={() => setOpen(false)}>{s.label}</a>
          ))}
          <a href="#contacto" className="btn btn-primary" style={{padding: "0.5rem 1.25rem", fontSize: "0.8rem"}}>Contactar</a>
        </div>
        <button className="mobile-toggle" onClick={() => setOpen(!open)}>
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>
  )
}

function Hero() {
  const heroClass = "hero hero-""" + b['hero_layout'] + """"
  return (
    <section id="inicio" className={heroClass}>
      {DATA.hero_img ? (
        <div className="hero-bg" style={{position: "absolute", inset: 0}}>
          <img src={DATA.hero_img} alt="" style={{width: "100%", height: "100%", objectFit: "cover"}} />
          <div style={{position: "absolute", inset: 0, background: "linear-gradient(to right, var(--bg) 0%, color-mix(in srgb, var(--bg) 70%, transparent) 50%, transparent 100%)"}} />
        </div>
      ) : (
        <div className="hero-bg" style={{position: "absolute", inset: 0, background: "linear-gradient(135deg, color-mix(in srgb, var(--p) 8%, var(--bg)), var(--bg) 50%)"}} />
      )}
      <div className="container" style={{position: "relative", zIndex: 2}}>
        <motion.span
          initial={{opacity: 0, y: 20}}
          animate={{opacity: 1, y: 0}}
          transition={{delay: 0.1}}
          className="tag"
        >
          {DATA.rating ? "\u2605 " + DATA.rating + (DATA.rating_total ? " \u00b7 " + DATA.rating_total + " rese\u00f1as" : "") : "Chinchin\u00e1, Caldas"}
        </motion.span>
        <motion.h1
          initial={{opacity: 0, y: 30}}
          animate={{opacity: 1, y: 0}}
          transition={{delay: 0.2, duration: 0.6}}
        >
          <span className="hl">{DATA.name}</span>
        </motion.h1>
        <motion.p
          initial={{opacity: 0, y: 30}}
          animate={{opacity: 1, y: 0}}
          transition={{delay: 0.35, duration: 0.6}}
        >
          Descubre {DATA.name} en el coraz\u00f3n de Chinchin\u00e1, Caldas. Calidad, tradici\u00f3n y servicio excepcional.
        </motion.p>
        <motion.div
          initial={{opacity: 0, y: 30}}
          animate={{opacity: 1, y: 0}}
          transition={{delay: 0.5, duration: 0.6}}
          className="actions"
        >
          <a href="#contacto" className="btn btn-primary">Contactar <ChevronRight size={16} /></a>
          <a href="#galeria" className="btn btn-outline">Ver galer\u00eda</a>
        </motion.div>
      </div>
    </section>
  )
}

function About() {
  const items = [
    { icon: Award, title: "Trayectoria", desc: "A\u00f1os de experiencia sirviendo a la comunidad de Chinchin\u00e1 con dedicaci\u00f3n y calidad." },
    { icon: MapPin, title: "Ubicaci\u00f3n", desc: "Estrat\u00e9gicamente ubicados en Chinchin\u00e1, Caldas, con f\u00e1cil acceso y parqueadero." },
    { icon: Heart, title: "Atenci\u00f3n", desc: "Servicio personalizado y atenci\u00f3n al cliente que marca la diferencia." },
  ]
  return (
    <section id="nosotros" className="section section-alt">
      <div className="container">
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="text-center mb-3"
        >
          <span className="tag">Nosotros</span>
          <h2>Bienvenido a <span className="hl">{DATA.name}</span></h2>
        </motion.div>
        <div className="grid-3">
          {items.map((item, i) => (
            <motion.div
              key={i}
              initial={{opacity: 0, y: 30}}
              whileInView={{opacity: 1, y: 0}}
              viewport={{once: true}}
              transition={{delay: i * 0.15}}
              className="card text-center"
            >
              <div className="about-icon" style={{margin: "0 auto 1rem", background: "color-mix(in srgb, var(--p) 12%, transparent)", color: "var(--p)"}}>
                <item.icon size={24} />
              </div>
              <h3 style={{fontSize: "1.1rem", marginBottom: "0.5rem", fontWeight: 700}}>{item.title}</h3>
              <p style={{color: "var(--tx2)", fontSize: "0.9rem", lineHeight: 1.6}}>{item.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Gallery() {
  const imgs = DATA.gallery_imgs
  if (!imgs.length) return null
  return (
    <section id="galeria" className="section">
      <div className="container">
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="text-center mb-3"
        >
          <span className="tag">Galer\u00eda</span>
          <h2>Nuestras <span className="hl">Fotos</span></h2>
        </motion.div>
        <div className="gallery-grid">
          {imgs.slice(0, 9).map((img, i) => (
            <motion.div
              key={i}
              initial={{opacity: 0, y: 20}}
              whileInView={{opacity: 1, y: 0}}
              viewport={{once: true}}
              transition={{delay: i * 0.08}}
            >
              <img src={img} alt="" loading="lazy" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Location() {
  const addr = DATA.address
  const items = [
    addr && { icon: MapPin, title: "Direcci\u00f3n", value: addr },
    DATA.phone && { icon: Phone, title: "Tel\u00e9fono", value: DATA.phone, href: "tel:" + DATA.phone },
    DATA.website && {
      icon: Globe, title: "Sitio Web",
      value: DATA.website.replace("https://", "").replace("http://", "").split("/")[0],
      href: DATA.website, external: true,
    },
    DATA.rating > 0 && {
      icon: Star, title: "Calificaci\u00f3n",
      value: DATA.rating + " / 5.0" + (DATA.rating_total ? " (" + DATA.rating_total + " rese\u00f1as)" : ""),
    },
  ].filter(Boolean)
  return (
    <section id="ubicacion" className="section section-alt">
      <div className="container">
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="text-center mb-3"
        >
          <span className="tag">Ubicaci\u00f3n</span>
          <h2>Encu\u00e9ntranos en <span className="hl">Chinchin\u00e1</span></h2>
        </motion.div>
        <div className="location-grid">
          <motion.div
            initial={{opacity: 0, x: -20}}
            whileInView={{opacity: 1, x: 0}}
            viewport={{once: true}}
            style={{display: "flex", flexDirection: "column", gap: "0.75rem"}}
          >
            {items.map((item: any, i: number) => (
              <div key={i} className="info-item" style={{background: "var(--sf)"}}>
                <div className="info-icon" style={{background: "color-mix(in srgb, var(--p) 15%, transparent)", color: "var(--p)"}}>
                  <item.icon size={18} />
                </div>
                <div className="info-text">
                  <h4>{item.title}</h4>
                  {item.href ? (
                    <a href={item.href} target={item.external ? "_blank" : undefined} rel={item.external ? "noopener" : undefined} style={{color: "var(--p)"}}>
                      {item.value} {item.external && <ExternalLink size={12} style={{display: "inline"}} />}
                    </a>
                  ) : (
                    <p>{item.value}</p>
                  )}
                </div>
              </div>
            ))}
          </motion.div>
          <motion.div
            initial={{opacity: 0, x: 20}}
            whileInView={{opacity: 1, x: 0}}
            viewport={{once: true}}
            className="map-wrap"
            style={{boxShadow: "0 4px 20px rgba(0,0,0,0.08)"}}
          >
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3975.0!2d-75.6!3d4.98!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNMKwNTgnNTYuMCJOIDc1wrAzNScwMC4wIlc!5e0!3m2!1ses!2sco!4v1"
              loading="lazy"
              title="Mapa de Chinchin\u00e1, Caldas"
            />
          </motion.div>
        </div>
      </div>
    </section>
  )
}

function Reviews() {
  const revs = DATA.reviews
  if (!revs.length) return null
  return (
    <section className="section">
      <div className="container">
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="text-center mb-3"
        >
          <span className="tag">Rese\u00f1as</span>
          <h2>Lo que dicen <span className="hl">nuestros clientes</span></h2>
        </motion.div>
        <div className="grid-3">
          {revs.map((rv: any, i: number) => (
            <motion.div
              key={i}
              initial={{opacity: 0, y: 20}}
              whileInView={{opacity: 1, y: 0}}
              viewport={{once: true}}
              transition={{delay: i * 0.15}}
              className="card"
            >
              <div className="stars">
                {Array.from({length: Math.floor(rv.rating)}).map((_, si) => (
                  <Star key={si} size={14} fill="currentColor" />
                ))}
              </div>
              <p style={{color: "var(--tx2)", fontSize: "0.9rem", lineHeight: 1.6, fontStyle: "italic"}}>
                &ldquo;{rv.text?.slice(0, 150)}{rv.text?.length > 150 ? "..." : ""}&rdquo;
              </p>
              {rv.author && <p style={{marginTop: "0.75rem", fontWeight: 600, fontSize: "0.9rem"}}>&mdash; {rv.author}</p>}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Contact() {
  const soc = DATA.social
  return (
    <section id="contacto" className="section section-alt">
      <div className="container">
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="text-center mb-3"
        >
          <span className="tag">Contacto</span>
          <h2>Ponte en <span className="hl">contacto</span></h2>
        </motion.div>
        <motion.div
          initial={{opacity: 0, y: 30}}
          whileInView={{opacity: 1, y: 0}}
          viewport={{once: true}}
          className="card"
          style={{maxWidth: "900px", margin: "0 auto"}}
        >
          <div className="contact-grid">
            <div>
              <h3 style={{fontSize: "1.3rem", fontWeight: 700, marginBottom: "1rem"}}>Informaci\u00f3n de contacto</h3>
              <p style={{color: "var(--tx2)", marginBottom: "1.5rem", lineHeight: 1.6}}>Estamos para servirte. No dudes en contactarnos.</p>
              {DATA.phone && (
                <div className="info-item" style={{padding: "0.75rem 0"}}>
                  <Phone size={18} style={{color: "var(--p)"}} />
                  <span>{DATA.phone}</span>
                </div>
              )}
              {DATA.address && (
                <div className="info-item" style={{padding: "0.75rem 0"}}>
                  <MapPin size={18} style={{color: "var(--p)"}} />
                  <span>{DATA.address}</span>
                </div>
              )}
            </div>
            <div>
              <h3 style={{fontSize: "1.3rem", fontWeight: 700, marginBottom: "1rem"}}>Redes sociales</h3>
              <p style={{color: "var(--tx2)", marginBottom: "1.5rem"}}>S\u00edguenos en nuestras redes.</p>
              <div className="social-links">
                {Object.entries(soc).map(([plat, link]) => {
                  const Icon = SOCIAL_ICONS[plat] || Globe
                  return (
                    <motion.a
                      key={plat}
                      href={link as string}
                      target="_blank"
                      rel="noopener"
                      whileHover={{scale: 1.1}}
                      whileTap={{scale: 0.9}}
                      className="social-link"
                      aria-label={plat}
                    >
                      <Icon size={18} />
                    </motion.a>
                  )
                })}
              </div>
              {DATA.whatsapp && (
                <motion.a
                  href={DATA.whatsapp}
                  target="_blank"
                  rel="noopener"
                  whileHover={{scale: 1.02}}
                  whileTap={{scale: 0.98}}
                  style={{display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", width: "100%", padding: "0.85rem", borderRadius: "var(--radius)", background: "#25D366", color: "white", fontWeight: 600, marginTop: "1.5rem", textDecoration: "none"}}
                >
                  <MessageCircle size={18} /> Escribir por WhatsApp
                </motion.a>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer>
      <div className="inner">
        <span className="copy">&copy; {new Date().getFullYear()} {DATA.name}. Todos los derechos reservados.</span>
        <span style={{color: "var(--tx2)", fontSize: "0.85rem"}}>Chinchin\u00e1, Caldas, Colombia</span>
      </div>
    </footer>
  )
}

function WhatsApp() {
  if (!DATA.whatsapp) return null
  return (
    <motion.a
      href={DATA.whatsapp}
      target="_blank"
      rel="noopener"
      initial={{scale: 0}}
      animate={{scale: 1}}
      whileHover={{scale: 1.1}}
      whileTap={{scale: 0.9}}
      className="whatsapp-float"
      aria-label="WhatsApp"
    >
      <MessageCircle size={24} />
    </motion.a>
  )
}

function ScrollToTop() {
  const [visible, setVisible] = useState(false)
  useEffect(() => {
    const f = () => setVisible(window.scrollY > 500)
    window.addEventListener("scroll", f)
    return () => window.removeEventListener("scroll", f)
  }, [])
  return (
    <button
      className={"scroll-top" + (visible ? " visible" : "")}
      onClick={() => window.scrollTo({top: 0, behavior: "smooth"})}
      aria-label="Volver arriba"
    >
      <ArrowUp size={18} />
    </button>
  )
}

export default function App() {
  return (
    <main>
      <Navbar />
      <Hero />
      <About />
      <Gallery />
      <Location />
      <Reviews />
      <Contact />
      <Footer />
      <WhatsApp />
      <ScrollToTop />
    </main>
  )
}
"""

# ─── MAIN ─────────────────────────────────────────────────────

def main():
    print("\n  " + p("bo", "=" * 50))
    print("  " + p("bo", "REDISE\u00d1O COMPLETO \u2014 5 TEMAS \u00d7 10 NEGOCIOS"))
    print("  " + p("bo", "=" * 50) + "\n")

    tmpl_dir = BASE / ".template-vite"

    for i, b in enumerate(BUSINESSES, 1):
        name = b["name"]
        theme_names = ["Claro Moderno", "R\u00fasticico C\u00e1lido", "Naturaleza Org\u00e1nica", "Corporativo Oscuro", "Urbano Bold"]
        tn = theme_names[b["theme"]]

        print("  " + p("cy", f"[{i}/10] {name}") + " \u2014 " + p("gr", tn))

        data = load_data(name)
        if not data:
            print("    " + p("ye", "Sin datos, saltando"))
            continue

        slug = slugify(name)
        site_dir = SITES / f"{i:02d}-{slug}"

        if site_dir.exists():
            shutil.rmtree(site_dir)

        subprocess.run(["npx", "create-vite", site_dir.name, "--template", "react-ts"],
                       cwd=SITES, capture_output=True, timeout=30)

        if not site_dir.exists():
            print("    " + p("re", "Error creando proyecto"))
            continue

        for f in ["App.css", "index.css", "App.tsx"]:
            (site_dir / "src" / f).unlink(missing_ok=True)

        # Copy photos
        biz_safe = re.sub(r'[^\w\s-]', '', name).strip().replace(" ", "_")
        src_photos = DATA_DIR / biz_safe / "fotos"
        if src_photos.exists():
            for pf in sorted(src_photos.iterdir()):
                if pf.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                    shutil.copy2(pf, site_dir / "public" / pf.name)

        # Package.json
        pkg = json.loads((site_dir / "package.json").read_text())
        pkg["dependencies"]["framer-motion"] = "^12.0.0"
        pkg["dependencies"]["lucide-react"] = "^0.400.0"
        pkg["devDependencies"]["tailwindcss"] = "^4"
        pkg["devDependencies"]["@tailwindcss/vite"] = "^4"
        pkg["scripts"]["dev"] = "vite --host"
        (site_dir / "package.json").write_text(json.dumps(pkg, indent=2))

        (site_dir / "vite.config.ts").write_text('import { defineConfig } from "vite"\nimport react from "@vitejs/plugin-react"\nimport tailwindcss from "@tailwindcss/vite"\n\nexport default defineConfig({\n  plugins: [tailwindcss(), react()],\n})\n')

        # Install deps
        if not tmpl_dir.exists():
            print("    Instalando dependencias...")
            subprocess.run(["npm", "install"], cwd=site_dir, capture_output=True, timeout=180)
            shutil.copytree(site_dir, tmpl_dir, symlinks=True, ignore=shutil.ignore_patterns("node_modules/.cache"))
        else:
            shutil.rmtree(site_dir)
            shutil.copytree(tmpl_dir, site_dir, symlinks=True, ignore=shutil.ignore_patterns("node_modules/.cache"))

        # index.html
        addr = data.get("address", "Chinchin\u00e1, Caldas")
        (site_dir / "index.html").write_text(
            '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8" />\n'
            + '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
            + '<meta name="description" content="' + name + " - " + addr + '" />\n'
            + '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
            + '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
            + '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Serif+Display:ital@0;1&family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700;9..40,800&display=swap" rel="stylesheet" />\n'
            + '<title>' + name + " - Chinchin\u00e1, Caldas</title>\n</head>\n<body>\n<div id=\"root\"></div>\n<script type=\"module\" src=\"/src/main.tsx\"></script>\n</body>\n</html>",
            encoding="utf-8"
        )

        # styles.css
        css = generate_css(b)
        (site_dir / "src" / "styles.css").write_text(css, encoding="utf-8")

        # main.tsx
        (site_dir / "src" / "main.tsx").write_text(
            'import { StrictMode } from "react"\nimport { createRoot } from "react-dom/client"\n'
            + 'import "./styles.css"\nimport App from "./App"\n\n'
            + "createRoot(document.getElementById(\"root\")!).render(\n  <StrictMode>\n    <App />\n  </StrictMode>,\n)\n",
            encoding="utf-8"
        )

        # App.tsx
        app_tsx = generate_app(b, i)
        if app_tsx:
            (site_dir / "src" / "App.tsx").write_text(app_tsx, encoding="utf-8")

        print("    " + p("gr", "OK"))

    print("\n  " + p("bo", "=" * 50))
    print("  " + p("bo", "CONSTRUYENDO SITIOS..."))
    print("  " + p("bo", "=" * 50) + "\n")

    for i, b in enumerate(BUSINESSES, 1):
        slug = slugify(b["name"])
        site_dir = SITES / f"{i:02d}-{slug}"
        if site_dir.exists():
            result = subprocess.run(["npx", "vite", "build"], cwd=site_dir, capture_output=True, timeout=60)
            if result.returncode == 0:
                print("  " + p("gr", f"  [{i}/10] {b['name'][:30]}") + " construido")
            else:
                err = result.stderr.decode()[:200]
                print("  " + p("re", f"  [{i}/10] {b['name'][:30]} ERROR: {err}"))

    print("\n  " + p("bo", "Preparando deploy..."))

    if DEPLOY.exists():
        shutil.rmtree(DEPLOY)
    DEPLOY.mkdir(parents=True)

    for i, b in enumerate(BUSINESSES, 1):
        orig_slug = f"{i:02d}-{slugify(b['name'])}"
        safe_slug = ascii_slug(orig_slug)
        src = SITES / orig_slug / "dist"
        dst = DEPLOY / safe_slug

        if src.exists():
            subprocess.run(["npx", "vite", "build", "--base", f"/{safe_slug}/"],
                          cwd=SITES / orig_slug, capture_output=True, timeout=60)
            shutil.copytree(src, dst)

    # Hub and report
    for fname in ["index.html", "informe-comercial.html"]:
        src = SITES / fname
        if src.exists():
            html = src.read_text(encoding="utf-8")
            for i, b in enumerate(BUSINESSES, 1):
                orig = f"{i:02d}-{slugify(b['name'])}"
                safe = ascii_slug(orig)
                html = html.replace(f"./{orig}/dist/index.html", f"./{safe}/")
            (DEPLOY / fname).write_text(html, encoding="utf-8")

    (DEPLOY / "vercel.json").write_text('{"version":2,"cleanUrls":true}\n')

    print("\n  " + p("gr", "\u2713") + " Deploy listo en " + str(DEPLOY))
    print("  " + p("gr", "\u2713") + " Ejecuta: npx vercel deploy --prod --yes --cwd deploy\n")


if __name__ == "__main__":
    main()
