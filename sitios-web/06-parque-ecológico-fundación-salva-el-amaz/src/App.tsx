import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Menu, X, MapPin, Phone, Globe, Star, ArrowUp, ChevronRight, ExternalLink, Facebook, Instagram, Youtube, Twitter, Linkedin, Music2, MessageCircle, Award, Heart } from "lucide-react"

const DATA = {"name": "Parque Ecológico Fundación Salva el Amazonas", "address": "Via, Chinchiná, Manizales, Caldas", "phone": "3105991153", "website": "", "rating": 4.2, "rating_total": 0, "reviews": [], "social": {}, "whatsapp": "", "hero_img": "foto_1.jpg", "gallery_imgs": ["foto_1.jpg", "foto_10.jpg", "foto_11.jpg", "foto_12.jpg", "foto_13.jpg", "foto_14.jpg", "foto_15.jpg", "foto_16.jpg", "foto_17.jpg", "foto_18.jpg", "foto_19.jpg", "foto_2.jpg", "foto_20.jpg", "foto_21.jpg", "foto_22.jpg", "foto_23.jpg", "foto_3.jpg", "foto_4.jpg", "foto_5.jpg", "foto_6.jpg", "foto_7.jpg", "foto_8.jpg", "foto_9.jpg"]};
const SECTIONS = [
  { href: "#inicio", label: "Inicio" },
  { href: "#nosotros", label: "Nosotros" },
  { href: "#galeria", label: "Galería" },
  { href: "#ubicacion", label: "Ubicación" },
  { href: "#contacto", label: "Contacto" },
]
const SOCIAL_ICONS: Record<string, any> = {
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
  const heroClass = "hero hero-center"
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
          {DATA.rating ? "★ " + DATA.rating + (DATA.rating_total ? " · " + DATA.rating_total + " reseñas" : "") : "Chinchiná, Caldas"}
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
          Descubre {DATA.name} en el corazón de Chinchiná, Caldas. Calidad, tradición y servicio excepcional.
        </motion.p>
        <motion.div
          initial={{opacity: 0, y: 30}}
          animate={{opacity: 1, y: 0}}
          transition={{delay: 0.5, duration: 0.6}}
          className="actions"
        >
          <a href="#contacto" className="btn btn-primary">Contactar <ChevronRight size={16} /></a>
          <a href="#galeria" className="btn btn-outline">Ver galería</a>
        </motion.div>
      </div>
    </section>
  )
}

function About() {
  const items = [
    { icon: Award, title: "Trayectoria", desc: "Años de experiencia sirviendo a la comunidad de Chinchiná con dedicación y calidad." },
    { icon: MapPin, title: "Ubicación", desc: "Estratégicamente ubicados en Chinchiná, Caldas, con fácil acceso y parqueadero." },
    { icon: Heart, title: "Atención", desc: "Servicio personalizado y atención al cliente que marca la diferencia." },
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
          <span className="tag">Galería</span>
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
    addr && { icon: MapPin, title: "Dirección", value: addr },
    DATA.phone && { icon: Phone, title: "Teléfono", value: DATA.phone, href: "tel:" + DATA.phone },
    DATA.website && {
      icon: Globe, title: "Sitio Web",
      value: DATA.website.replace("https://", "").replace("http://", "").split("/")[0],
      href: DATA.website, external: true,
    },
    DATA.rating > 0 && {
      icon: Star, title: "Calificación",
      value: DATA.rating + " / 5.0" + (DATA.rating_total ? " (" + DATA.rating_total + " reseñas)" : ""),
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
          <span className="tag">Ubicación</span>
          <h2>Encuéntranos en <span className="hl">Chinchiná</span></h2>
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
              title="Mapa de Chinchiná, Caldas"
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
          <span className="tag">Reseñas</span>
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
              <h3 style={{fontSize: "1.3rem", fontWeight: 700, marginBottom: "1rem"}}>Información de contacto</h3>
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
              <p style={{color: "var(--tx2)", marginBottom: "1.5rem"}}>Síguenos en nuestras redes.</p>
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
        <span style={{color: "var(--tx2)", fontSize: "0.85rem"}}>Chinchiná, Caldas, Colombia</span>
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
