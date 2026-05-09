# Webuilder

**Scrape Google Maps → Generate Vite+React+TypeScript websites → Deploy to Vercel**

A complete pipeline for creating professional business websites from Google Maps data. Scrapes businesses by location, generates 10 Vite+React+TypeScript sites with premium design (5 theme variants, Framer Motion animations), and deploys to Vercel with a CRM-enabled hub page and printable sales report.

---

## Requirements

| Tool    | Version     | Notes                        |
| ------- | ----------- | ---------------------------- |
| Python  | ≥ 3.10      | Core pipeline                |
| Node.js | ≥ 18        | Vite + React build           |
| Chrome  | latest      | Required for Selenium scraper |

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node dependencies (used by Vite builds)
npm install -g npx

# 3. Scrape businesses from Google Maps
python webuilder.py scrape --location "Pereira, Risaralda"

# 4. Build 10 websites from scraped data
python webuilder.py build --dir negocios --prefix PE --start-idx 21

# 5. Generate hub page + CRM + sales report
python webuilder.py hub

# 6. Deploy to Vercel
python webuilder.py deploy

# Or run the full pipeline in one command:
python webuilder.py all --location "Pereira, Risaralda" --prefix PE
```

---

## Usage

### 1. Scrape (`webuilder.py scrape`)

Opens a visible Chrome window, searches Google Maps for businesses by category, and saves data incrementally to `negocios/`.

```bash
python webuilder.py scrape --location "Manizales, Caldas"
```

**Data saved per business:**
```
negocios/Nombre_Del_Negocio/
├── info.json       # name, address, phone, website, rating, social media, etc.
└── fotos/          # downloaded photos (foto_1.jpg, foto_2.jpg, ...)
```

**Scraped data fields:** name, address, phone, website, rating, reviews, social media links, photos.

### 2. Build (`webuilder.py build`)

Scores all scraped businesses by data completeness, picks the top 10, assigns a theme (5 variants based on category), and generates a Vite+React+TypeScript site for each.

```bash
python webuilder.py build --dir negocios --prefix PE --start-idx 21
```

**Scoring system:**
| Feature          | Points |
| ---------------- | ------ |
| Phone            | 3      |
| Website          | 3      |
| Address          | 2      |
| Rating ≥ 4.0     | 2      |
| Social networks  | 2      |
| ≥ 5 photos       | 3      |
| ≥ 2 photos       | 1      |

**5 Theme Variants:**
| ID | Theme              | For                          |
| -- | ------------------ | ---------------------------- |
| 0  | Claro Moderno      | Tiendas, almacenes           |
| 1  | Rústico Cálido     | Restaurantes, cafeterías     |
| 2  | Naturaleza Orgánica| Parques, ecoturismo          |
| 3  | Corporativo Oscuro | Compañías, oficinas          |
| 4  | Urbano Bold        | Bares, discotecas            |

**Output:** `sitios-web/PE-21-slug/` (Vite project per site), `deploy/PE-21-slug/` (built static files).

### 3. Hub + Report (`webuilder.py hub`)

Generates two files from all deployed sites:

- **`index.html`** — Hub page with CRM: per-business status tracking (Pendiente → Contactado → 1er Seguimiento → 2do Seguimiento → Cerrado) with localStorage persistence, summary stats, and filter by location/status.
- **`informe-comercial.html`** — Printable sales report with tab-navigation per business, info cards, and sales speech.

```bash
python webuilder.py hub
```

### 4. Serve Locally (`webuilder.py serve`)

Starts a Node.js HTTP server for local preview. Serves the hub at `/`, report at `/informe-comercial.html`, and each site at `/{slug}/`.

```bash
python webuilder.py serve --port 4000
# → http://localhost:4000
```

### 5. Deploy (`webuilder.py deploy`)

Deploys the `deploy/` directory to Vercel. Requires `vercel` CLI logged in.

```bash
python webuilder.py deploy
```

### 6. Full Pipeline (`webuilder.py all`)

Runs scrape → build → hub → deploy sequentially.

```bash
python webuilder.py all --location "Pereira, Risaralda" --prefix PE
```

---

## Project Structure

```
webbuilder/
├── webuilder.py                 # CLI entry point (this tool)
├── run.py                       # Google Maps scraper (Selenium + BS4)
├── build_location.py             # Site generator (5 themes, scoring)
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
│
├── negocios/                     # Scraped business data (current location)
│   └── Nombre_Negocio/
│       ├── info.json
│       └── fotos/
│
├── negocios_chinchina/           # Backup: Chinchiná scraped data
│
├── sitios-web/                   # Generated Vite projects + hub + report
│   ├── index.html                # CRM hub page
│   ├── informe-comercial.html    # Sales report
│   ├── server.js                 # Local dev server
│   ├── 01-slug/                  # Chinchiná site 1
│   ├── SR-11-slug/               # Santa Rosa site 11
│   └── ...
│
├── deploy/                       # Vercel deployment directory
│   ├── index.html                # Hub page (copy)
│   ├── informe-comercial.html    # Report (copy)
│   ├── vercel.json               # Vercel config
│   ├── 01-slug/                  # Built Chinchiná site 1
│   └── SR-11-slug/               # Built Santa Rosa site 11
│
└── .template-vite/               # Cached Vite template (speeds builds)
```

## Site Features

Each generated site includes:

- **Responsive design** (mobile-first, CSS Grid/Flexbox, clamp() typography)
- **Framer Motion animations** (scroll-reveal, hover effects, page transitions)
- **5 theme variants** with distinct colors, fonts, radius, and card styles
- **Hero section** with photo background (5 layout options: left, right, center, full, split)
- **About section** with business values
- **Photo gallery** with hover zoom
- **Google Maps embed** for location
- **Reviews section** (shows Google reviews if available)
- **Contact section** with phone, address, social links
- **WhatsApp floating button**
- **Scroll-to-top button**
- **Fixed navbar** with scroll detection
- **Lucide React icons** throughout

## Hub CRM Features

- **Per-business status tracking** via dropdown (Pendiente / Contactado / 1er Seguimiento / 2do Seguimiento / Cerrado)
- **Summary stats bar** showing counts per status
- **Filter buttons** by location (Chinchiná / Santa Rosa) and by status (Pendiente / Cerrados)
- **Status badges** on each card (color-coded)
- **localStorage persistence** — status survives page reloads
- **Sales speech modal** — one-click access to persuasive pitch

## Deployed Sites

- **Production URL:** https://deploy-xi-taupe.vercel.app
- **Hub with CRM:** https://deploy-xi-taupe.vercel.app/
- **Sales Report:** https://deploy-xi-taupe.vercel.app/informe-comercial.html
- **Example site:** https://deploy-xi-taupe.vercel.app/01-almacenes-oportunidades/

## License

MIT
