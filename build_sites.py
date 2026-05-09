#!/usr/bin/env python3
"""
Genera sitios web profesionales con Vite + React + TypeScript + Framer Motion.
Cada sitio inyecta los datos del negocio como JSON en un template base.
Usa un proyecto base con npm install pre-hecho para evitar 10 instalaciones.
"""
import json, os, re, shutil, subprocess, functools
from pathlib import Path

print = functools.partial(print, flush=True)

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "negocios"
SITES_DIR = BASE_DIR / "sitios-web"
TEMPLATE_DIR = BASE_DIR / ".template-vite"

C = {"cyan":"\033[96m","green":"\033[92m","yellow":"\033[93m","red":"\033[91m","bold":"\033[1m","end":"\033[0m"}
p = lambda c,t: f"{C.get(c,'')}{t}{C['end']}"

BUSINESSES = [
    ("Almacenes Oportunidades", "#2563eb", "#1e40af", "#f59e0b"),
    ("Ranchero Rústico Paisa", "#dc2626", "#991b1b", "#fbbf24"),
    ("La Postrera Campestre", "#059669", "#065f46", "#f97316"),
    ("Compañía Cafetera La Meseta S.A.S", "#7c3aed", "#5b21b6", "#d97706"),
    ("Zumo&Humo", "#e11d48", "#9f1239", "#facc15"),
    ("Parque Ecológico Fundación Salva el Amazonas", "#16a34a", "#15803d", "#22d3ee"),
    ("La Tarima Cafe Cultural", "#d97706", "#92400e", "#fcd34d"),
    ("Diez de10 Coffee & Brunch", "#0891b2", "#0e7490", "#fbbf24"),
    ("Supermercado El Campesino", "#4f46e5", "#3730a3", "#22c55e"),
    ("MonRut Café", "#a21caf", "#701a75", "#e879f9"),
]


def slugify(name):
    s = re.sub(r'[^\w\s-]', '', name).strip().lower().replace(" ", "-")
    return re.sub(r'-+', '-', s)[:40]


def load_business(name):
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


def create_base_template():
    """Create one base Vite project with all deps installed, then reuse."""
    if TEMPLATE_DIR.exists():
        print(f"  Template ya existe, saltando creaci\u00f3n")
        return

    print(f"  Creando proyecto Vite base...")
    subprocess.run(["npx", "create-vite", str(TEMPLATE_DIR.name), "--template", "react-ts"],
                   cwd=BASE_DIR, capture_output=True, timeout=30)

    pkg = json.loads((TEMPLATE_DIR / "package.json").read_text())
    pkg["dependencies"]["framer-motion"] = "^12.0.0"
    pkg["dependencies"]["lucide-react"] = "^0.400.0"
    pkg["devDependencies"]["tailwindcss"] = "^4"
    pkg["devDependencies"]["@tailwindcss/vite"] = "^4"
    pkg["scripts"]["dev"] = "vite --host"
    (TEMPLATE_DIR / "package.json").write_text(json.dumps(pkg, indent=2))

    (TEMPLATE_DIR / "vite.config.ts").write_text("""import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [tailwindcss(), react()],
})
""", encoding="utf-8")

    print(f"    Instalando dependencias (una sola vez)...")
    subprocess.run(["npm", "install"], cwd=TEMPLATE_DIR, capture_output=True, timeout=180)

    # Clean defaults from template
    for f in ["App.css", "index.css", "App.tsx"]:
        (TEMPLATE_DIR / "src" / f).unlink(missing_ok=True)

    print(f"  {p('green', 'OK')} Template base listo")


def generate_site(biz_data, primary_hex, secondary_hex, accent_hex, index):
    name = biz_data["name"]
    slug = slugify(name)
    site_dir = SITES_DIR / f"{index:02d}-{slug}"

    if site_dir.exists():
        shutil.rmtree(site_dir)

    print(f"\n  {p('cyan', f'[{index}/10] {name}')}")

    # Copy base template (fast, no npm install needed)
    shutil.copytree(TEMPLATE_DIR, site_dir, symlinks=True, ignore=shutil.ignore_patterns("node_modules/.cache"))

    # Copy photos
    biz_safe = re.sub(r'[^\w\s-]', '', name).strip().replace(" ", "_")
    src_photos = DATA_DIR / biz_safe / "fotos"
    if src_photos.exists():
        for pf in sorted(src_photos.iterdir()):
            if pf.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                shutil.copy2(pf, site_dir / "public" / pf.name)

    # Build embed data
    photos = [f"/{f.name}" for f in sorted(src_photos.iterdir())] if src_photos.exists() else []
    embed_data = {
        "name": name,
        "address": biz_data.get("address", ""),
        "phone": biz_data.get("phone", ""),
        "website": biz_data.get("website", ""),
        "rating": biz_data.get("rating", 0),
        "rating_total": biz_data.get("rating_total", 0),
        "reviews": biz_data.get("reviews", [])[:3],
        "social": biz_data.get("social_media", {}),
        "whatsapp": biz_data.get("social_media", {}).get("whatsapp", ""),
        "hero_img": photos[0] if photos else "",
        "gallery_imgs": photos,
    }
    data_json = json.dumps(embed_data, ensure_ascii=False)

    # ── index.html ──
    addr = embed_data["address"]
    (site_dir / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{name} - {addr}" />
    <title>{name} - Chinchiná, Caldas</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>""", encoding="utf-8")

    # ── styles.css ──
    r, g, b = tuple(int(primary_hex[i:i+2], 16) for i in (1, 3, 5))
    ra, ga, ba = tuple(int(accent_hex[i:i+2], 16) for i in (1, 3, 5))

    css = f"""@import "tailwindcss";

@theme inline {{
  --color-primary: {primary_hex};
  --color-primary-dark: {secondary_hex};
  --color-accent: {accent_hex};
  --color-primary-rgb: {r}, {g}, {b};
  --color-accent-rgb: {ra}, {ga}, {ba};
  --color-bg: #0a0a0f;
  --color-surface: #12121a;
  --color-surface-light: #1a1a2e;
  --color-text: #f1f1f1;
  --color-text-secondary: #a0a0b0;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
}}

.glass {{
  background: rgba({r},{g},{b},0.08);
  backdrop-filter: blur(12px);
  border: 1px solid rgba({r},{g},{b},0.15);
}}
.glass-light {{
  background: rgba(255,255,255,0.04);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.06);
}}
.gradient-text {{
  background: linear-gradient(135deg, {primary_hex}, {accent_hex});
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.glow {{
  box-shadow: 0 0 30px rgba({r},{g},{b},0.15), 0 0 60px rgba({r},{g},{b},0.05);
}}
"""
    (site_dir / "src" / "styles.css").write_text(css, encoding="utf-8")

    # ── main.tsx ──
    (site_dir / "src" / "main.tsx").write_text("""import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
""", encoding="utf-8")

    # ── App.tsx ──
    app_template = (BASE_DIR / "AppTemplate.tsx").read_text(encoding="utf-8")
    app_content = app_template.replace("/*BUSINESS_DATA*/", data_json)
    app_content = app_content.replace("/*PRIMARY_HEX*/", primary_hex)
    (site_dir / "src" / "App.tsx").write_text(app_content, encoding="utf-8")

    print(f"    {p('green', 'OK')} Sitio generado")
    return site_dir


def create_template_file():
    template = """import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Menu, X, MapPin, Phone, Globe, Star, ArrowUp, ChevronRight,
  ExternalLink, Facebook, Instagram, Youtube, Twitter, Linkedin,
  Music2, MessageCircle,
} from 'lucide-react'

const DATA = /*BUSINESS_DATA*/
const PRIMARY = "/*PRIMARY_HEX*/"

const sections = [
  { href: "#inicio", label: "Inicio" },
  { href: "#nosotros", label: "Nosotros" },
  { href: "#galeria", label: "Galer\u00eda" },
  { href: "#ubicacion", label: "Ubicaci\u00f3n" },
  { href: "#contacto", label: "Contacto" },
]

const socialIcons: Record<string, any> = {
  facebook: Facebook, instagram: Instagram, youtube: Youtube,
  twitter: Twitter, linkedin: Linkedin, tiktok: Music2, whatsapp: MessageCircle,
}

function Navbar() {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const f = () => setScrolled(window.scrollY > 50)
    window.addEventListener("scroll", f)
    return () => window.removeEventListener("scroll", f)
  }, [])

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100, damping: 20 }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "glass mt-4 mx-4 md:mx-8 rounded-2xl" : "bg-transparent mt-0 mx-0"
      }`}
    >
      <div className="max-w-7xl mx-auto px-6 h-16 md:h-20 flex items-center justify-between">
        <a href="#inicio" className="text-xl md:text-2xl font-bold gradient-text">
          {DATA.name}
        </a>
        <div className="hidden md:flex items-center gap-8">
          {sections.map((s) => (
            <a key={s.href} href={s.href} className="text-text-secondary hover:text-text transition-colors text-sm font-medium">
              {s.label}
            </a>
          ))}
          <a
            href="#contacto"
            className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white"
            style={{ backgroundColor: PRIMARY }}
          >
            Contactar
          </a>
        </div>
        <button className="md:hidden text-text" onClick={() => setOpen(!open)}>
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-white/5"
          >
            <div className="px-6 py-4 flex flex-col gap-3">
              {sections.map((s) => (
                <a key={s.href} href={s.href} onClick={() => setOpen(false)} className="text-text-secondary hover:text-text transition-colors py-2">
                  {s.label}
                </a>
              ))}
              <a
                href="#contacto"
                onClick={() => setOpen(false)}
                className="px-5 py-2.5 rounded-xl text-sm font-semibold text-white text-center mt-2"
                style={{ backgroundColor: PRIMARY }}
              >
                Contactar
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  )
}

function Hero() {
  return (
    <section id="inicio" className="relative min-h-screen flex items-center overflow-hidden">
      {DATA.hero_img ? (
        <div className="absolute inset-0">
          <img src={DATA.hero_img} alt="" className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-r from-bg via-bg/80 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-bg via-transparent to-bg/20" />
        </div>
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-bg to-surface" />
      )}
      <div className="relative z-10 max-w-7xl mx-auto px-6 w-full">
        <div className="max-w-3xl">
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            <motion.span
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="inline-block px-4 py-1.5 rounded-full glass text-sm font-medium text-accent mb-6"
            >
              {DATA.rating ? `\u2605 ${DATA.rating}${DATA.rating_total ? ` · ${DATA.rating_total} rese\u00f1as` : ""}` : "Chinchin\u00e1, Caldas"}
            </motion.span>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.8 }}
            className="text-5xl md:text-7xl lg:text-8xl font-bold leading-[1.05] tracking-tight mb-6"
          >
            <span className="gradient-text">{DATA.name}</span>
            <br />
            <span className="text-text">En Chinchin\u00e1</span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="text-lg md:text-xl text-text-secondary max-w-xl mb-8 leading-relaxed"
          >
            Descubre {DATA.name} en el coraz\u00f3n de Chinchin\u00e1, Caldas. Calidad, tradici\u00f3n y servicio excepcional.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.8 }}
            className="flex flex-wrap gap-4"
          >
            <a
              href="#contacto"
              className="px-8 py-3.5 rounded-xl font-semibold text-white text-sm inline-flex items-center gap-2 glow"
              style={{ backgroundColor: PRIMARY }}
            >
              Contactar <ChevronRight size={16} />
            </a>
            <a
              href="#galeria"
              className="px-8 py-3.5 rounded-xl font-semibold text-text border border-white/10 hover:bg-white/5 transition-all text-sm inline-flex items-center gap-2"
            >
              Ver galer\u00eda
            </a>
          </motion.div>
        </div>
      </div>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="w-6 h-10 rounded-full border-2 border-white/20 flex items-start justify-center pt-2"
        >
          <div className="w-1.5 h-1.5 rounded-full bg-white/40" />
        </motion.div>
      </motion.div>
    </section>
  )
}

function About() {
  return (
    <section id="nosotros" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <span className="text-accent text-sm font-semibold tracking-widest uppercase">Nosotros</span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">
            Bienvenido a <span className="gradient-text">{DATA.name}</span>
          </h2>
          <div className="w-16 h-1 rounded-full mx-auto mt-6" style={{ backgroundColor: PRIMARY }} />
        </motion.div>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: Star, title: "Trayectoria", desc: "A\u00f1os de experiencia sirviendo a la comunidad de Chinchin\u00e1 con dedicaci\u00f3n y calidad." },
            { icon: MapPin, title: "Ubicaci\u00f3n", desc: "Estrat\u00e9gicamente ubicados en Chinchin\u00e1, Caldas, con f\u00e1cil acceso." },
            { icon: Phone, title: "Atenci\u00f3n", desc: "Servicio personalizado y atenci\u00f3n al cliente que marca la diferencia." },
          ].map((item, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="glass-light rounded-2xl p-8 text-center hover:glow transition-all duration-500"
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-5"
                style={{ backgroundColor: PRIMARY + "20", color: PRIMARY }}
              >
                <item.icon size={24} />
              </div>
              <h3 className="text-lg font-semibold mb-3">{item.title}</h3>
              <p className="text-text-secondary text-sm leading-relaxed">{item.desc}</p>
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
    <section id="galeria" className="py-24 md:py-32 bg-surface relative">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <span className="text-accent text-sm font-semibold tracking-widest uppercase">Galer\u00eda</span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">Nuestras <span className="gradient-text">Fotos</span></h2>
          <div className="w-16 h-1 rounded-full mx-auto mt-6" style={{ backgroundColor: PRIMARY }} />
        </motion.div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {imgs.slice(0, 9).map((img, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="relative group overflow-hidden rounded-2xl aspect-[4/3]"
            >
              <img src={img} alt="" className="w-full h-full object-cover transition-all duration-700 group-hover:scale-110" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

function Location() {
  const addr = DATA.address
  return (
    <section id="ubicacion" className="py-24 md:py-32 relative">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <span className="text-accent text-sm font-semibold tracking-widest uppercase">Ubicaci\u00f3n</span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">
            Encu\u00e9ntranos en <span className="gradient-text">Chinchin\u00e1</span>
          </h2>
          <div className="w-16 h-1 rounded-full mx-auto mt-6" style={{ backgroundColor: PRIMARY }} />
        </motion.div>
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <motion.div initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} className="space-y-6">
            {[
              addr && { icon: MapPin, title: "Direcci\u00f3n", value: addr },
              DATA.phone && { icon: Phone, title: "Tel\u00e9fono", value: DATA.phone, href: "tel:" + DATA.phone },
              DATA.website && {
                icon: Globe, title: "Sitio Web",
                value: DATA.website.replace("https://", "").replace("http://", "").split("/")[0],
                href: DATA.website,
                external: true,
              },
              DATA.rating > 0 && {
                icon: Star, title: "Calificaci\u00f3n",
                value: `${DATA.rating} / 5.0${DATA.rating_total ? ` (${DATA.rating_total} rese\u00f1as)` : ""}`,
              },
            ]
              .filter(Boolean)
              .map((item: any, i: number) => (
                <div key={i} className="glass-light rounded-2xl p-6 flex items-start gap-4">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ backgroundColor: PRIMARY + "20", color: PRIMARY }}
                  >
                    <item.icon size={18} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-1">{item.title}</h4>
                    {item.href ? (
                      <a href={item.href} target={item.external ? "_blank" : undefined} rel={item.external ? "noopener noreferrer" : undefined} className="text-text hover:text-primary transition-colors inline-flex items-center gap-1">
                        {item.value}
                        {item.external && <ExternalLink size={12} />}
                      </a>
                    ) : (
                      <p className="text-text">{item.value}</p>
                    )}
                  </div>
                </div>
              ))}
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="rounded-2xl overflow-hidden h-[400px] glow"
          >
            <iframe
              src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3975.0!2d-75.6!3d4.98!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNMKwNTgnNTYuMCJOIDc1wrAzNScwMC4wIlc!5e0!3m2!1ses!2sco!4v1"
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen
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
    <section className="py-24 md:py-32 bg-surface relative">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <span className="text-accent text-sm font-semibold tracking-widest uppercase">Rese\u00f1as</span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">
            Lo que dicen <span className="gradient-text">nuestros clientes</span>
          </h2>
          <div className="w-16 h-1 rounded-full mx-auto mt-6" style={{ backgroundColor: PRIMARY }} />
        </motion.div>
        <div className="grid md:grid-cols-3 gap-6">
          {revs.map((rv: any, i: number) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="glass-light rounded-2xl p-6"
            >
              <div className="flex gap-1 text-accent mb-3">
                {Array.from({ length: Math.floor(rv.rating) }).map((_, si) => (
                  <Star key={si} size={14} fill="currentColor" />
                ))}
              </div>
              <p className="text-text-secondary text-sm leading-relaxed italic">
                &ldquo;{rv.text?.slice(0, 150)}{rv.text?.length > 150 ? "..." : ""}&rdquo;
              </p>
              {rv.author && <p className="text-text text-sm font-semibold mt-3">&mdash; {rv.author}</p>}
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
    <section id="contacto" className="py-24 md:py-32 relative">
      <div className="max-w-4xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-16">
          <span className="text-accent text-sm font-semibold tracking-widest uppercase">Contacto</span>
          <h2 className="text-4xl md:text-5xl font-bold mt-3">
            Ponte en <span className="gradient-text">contacto</span>
          </h2>
          <div className="w-16 h-1 rounded-full mx-auto mt-6" style={{ backgroundColor: PRIMARY }} />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="glass rounded-2xl p-8 md:p-12 glow"
        >
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-6">
              <h3 className="text-2xl font-bold">Informaci\u00f3n de contacto</h3>
              <p className="text-text-secondary">Estamos para servirte. No dudes en contactarnos.</p>
              {DATA.phone && (
                <a href={"tel:" + DATA.phone} className="flex items-center gap-3 text-text-secondary hover:text-primary transition-colors">
                  <Phone size={18} />
                  <span>{DATA.phone}</span>
                </a>
              )}
              {DATA.address && (
                <div className="flex items-start gap-3 text-text-secondary">
                  <MapPin size={18} className="mt-0.5" />
                  <span>{DATA.address}</span>
                </div>
              )}
            </div>
            <div className="space-y-4">
              <h3 className="text-2xl font-bold">Redes sociales</h3>
              <p className="text-text-secondary">S\u00edguenos en nuestras redes.</p>
              <div className="flex flex-wrap gap-3">
                {Object.entries(soc).map(([plat, link]) => {
                  const Icon = socialIcons[plat] || Globe
                  return (
                    <motion.a
                      key={plat}
                      href={link as string}
                      target="_blank"
                      rel="noopener noreferrer"
                      whileHover={{ scale: 1.1, rotate: 5 }}
                      whileTap={{ scale: 0.9 }}
                      className="w-11 h-11 rounded-xl glass flex items-center justify-center text-text-secondary hover:text-primary transition-all duration-300"
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
                  rel="noopener noreferrer"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center justify-center gap-2 w-full px-6 py-3.5 rounded-xl font-semibold text-white mt-4"
                  style={{ backgroundColor: "#25D366" }}
                >
                  <MessageCircle size={18} />
                  Escribir por WhatsApp
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
  const soc = DATA.social
  return (
    <footer className="border-t border-white/5 py-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-center md:text-left">
            <span className="text-xl font-bold gradient-text">{DATA.name}</span>
            <p className="text-text-secondary text-sm mt-1">Chinchin\u00e1, Caldas, Colombia</p>
          </div>
          <div className="flex gap-4">
            {Object.entries(soc).map(([plat, link]) => {
              const Icon = socialIcons[plat] || Globe
              return (
                <a
                  key={plat}
                  href={link as string}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-xl glass flex items-center justify-center text-text-secondary hover:text-primary transition-all duration-300"
                  aria-label={plat}
                >
                  <Icon size={16} />
                </a>
              )
            })}
          </div>
        </div>
        <div className="text-center text-text-secondary text-xs mt-8 pt-8 border-t border-white/5">
          &copy; {new Date().getFullYear()} {DATA.name}. Todos los derechos reservados.
        </div>
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
      rel="noopener noreferrer"
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.9 }}
      className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center shadow-lg"
      style={{ backgroundColor: "#25D366" }}
      aria-label="WhatsApp"
    >
      <MessageCircle size={24} className="text-white" />
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
    <AnimatePresence>
      {visible && (
        <motion.button
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0 }}
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          className="fixed bottom-6 left-6 z-50 w-12 h-12 rounded-xl glass flex items-center justify-center text-text-secondary hover:text-primary transition-all"
        >
          <ArrowUp size={18} />
        </motion.button>
      )}
    </AnimatePresence>
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
    (BASE_DIR / "AppTemplate.tsx").write_text(template, encoding="utf-8")
    print(f"  {p('green', 'OK')} Template creado")


def main():
    print(f"\n  {p('bold', '\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557')}")
    print(f"  {p('bold', '\u2551    GENERANDO 10 SITIOS WEB PROFESIONALES \u2551')}")
    print(f"  {p('bold', '\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d')}\n")

    SITES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"  Creando template base...")
    create_template_file()
    create_base_template()

    for i, (name, pr, sc, ac) in enumerate(BUSINESSES, 1):
        biz_data = load_business(name)
        if not biz_data:
            print(f"  {p('yellow', f'No hay datos para: {name}')}")
            continue
        generate_site(biz_data, pr, sc, ac, i)

    print(f"\n  {p('green', '\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557')}")
    print(f"  {p('green', '\u2551       10 SITIOS GENERADOS               \u2551')}")
    print(f"  {p('green', '\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d')}")
    print(f"\n  {p('bold', 'Para desarrollar cada sitio:')}")
    print(f"    cd sitios-web/01-...")
    print(f"    npm run dev")
    print(f"\n  O construir: npm run build")


if __name__ == "__main__":
    main()
