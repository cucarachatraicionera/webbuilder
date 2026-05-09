#!/usr/bin/env python3
"""
webuilder — CLI tool for scraping Google Maps businesses,
generating professional Vite+React+TypeScript websites, and deploying to Vercel.

Usage:
  python webuilder.py scrape --location "City, Dept"
  python webuilder.py build --dir negocios --prefix XX --start-idx N
  python webuilder.py hub
  python webuilder.py serve
  python webuilder.py deploy
  python webuilder.py all --location "City, Dept" --prefix XX
"""
import sys, subprocess, functools, json, pathlib, re, shutil

print = functools.partial(print, flush=True)
BASE = pathlib.Path(__file__).parent.resolve()

C = {"cy": "\033[96m", "gr": "\033[92m", "ye": "\033[93m", "re": "\033[91m", "bo": "\033[1m", "en": "\033[0m"}
p = lambda c, t: f"{C.get(c, '')}{t}{C['en']}"


def cmd_scrape(args):
    """Run the Google Maps scraper for a location."""
    location = args.get("location") or "Santa Rosa de Cabal, Risaralda"
    print(f"\n  {p('bo', 'Scraping:')} {p('cy', location)}\n")
    result = subprocess.run(
        [sys.executable, "run.py", "--location", location],
        cwd=BASE, capture_output=False, timeout=600
    )
    return result.returncode


def cmd_build(args):
    """Build sites from scraped data."""
    data_dir = args.get("dir", "negocios")
    prefix = args.get("prefix", "SR")
    start_idx = int(args.get("start_idx", 11))
    print(f"\n  {p('bo', 'Building sites from:')} {p('cy', data_dir)} prefix={prefix} start={start_idx}\n")
    result = subprocess.run(
        [sys.executable, "build_location.py", "--dir", data_dir, "--prefix", prefix, "--start-idx", str(start_idx)],
        cwd=BASE, capture_output=False, timeout=600
    )
    return result.returncode


def cmd_hub(args):
    """Generate hub page and sales report with CRM."""
    print(f"\n  {p('bo', 'Generating hub + report with CRM...')}\n")
    _generate_hub_and_report()
    print(f"\n  {p('gr', 'Hub and report generated')}")
    return 0


def cmd_serve(args):
    """Start the local dev server."""
    port = args.get("port", "4000")
    print(f"\n  {p('bo', f'Starting server on port {port}...')}\n")
    proc = subprocess.Popen(
        ["node", "server.js"],
        cwd=BASE / "sitios-web",
        env={**__import__('os').environ, "PORT": port}
    )
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
    return 0


def cmd_deploy(args):
    """Deploy to Vercel."""
    print(f"\n  {p('bo', 'Deploying to Vercel...')}\n")
    result = subprocess.run(
        ["npx", "vercel", "deploy", "--prod", "--yes", "--cwd", "."],
        cwd=BASE / "deploy", capture_output=False, timeout=300
    )
    return result.returncode


def cmd_all(args):
    """Full pipeline: scrape, build, hub, deploy."""
    location = args.get("location", "Santa Rosa de Cabal, Risaralda")
    prefix = args.get("prefix", "SR")
    data_dir = args.get("dir", "negocios")

    # 1. Scrape
    print(f"\n  {'='*50}")
    print(f"  {p('bo', 'STEP 1: Scrape Google Maps')}")
    print(f"  {'='*50}\n")
    code = cmd_scrape({"location": location})
    if code != 0:
        print(f"  {p('re', 'Scrape failed, aborting')}")
        return code

    # 2. Build
    print(f"\n  {'='*50}")
    print(f"  {p('bo', 'STEP 2: Build websites')}")
    print(f"  {'='*50}\n")
    code = cmd_build({"dir": data_dir, "prefix": prefix, "start_idx": str(cmd_all.next_idx)})
    if code != 0:
        print(f"  {p('re', 'Build failed, aborting')}")
        return code

    # 3. Hub
    print(f"\n  {'='*50}")
    print(f"  {p('bo', 'STEP 3: Generate hub + report')}")
    print(f"  {'='*50}\n")
    cmd_hub({})

    # 4. Deploy
    print(f"\n  {'='*50}")
    print(f"  {p('bo', 'STEP 4: Deploy to Vercel')}")
    print(f"  {'='*50}\n")
    cmd_deploy({})

    print(f"\n  {p('gr', 'Done! All steps completed.')}")
    return 0


cmd_all.next_idx = 1


def _get_theme_color(idx):
    colors = ["#2563eb", "#dc2626", "#059669", "#7c3aed", "#e11d48", "#16a34a", "#d97706", "#0891b2", "#4f46e5", "#a21caf"]
    return colors[(idx - 1) % 10]


def _safe_name(name):
    return name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _slugify(name):
    s = re.sub(r'[^\w\s-]', '', name).strip().lower().replace(" ", "-")
    s = re.sub(r'-+', '-', s)[:40]
    for a, b in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n')]:
        s = s.replace(a, b)
    return s


def _load_biz_data(data_dir):
    biz_data = {}
    for biz_dir in sorted(data_dir.iterdir()):
        if not biz_dir.is_dir():
            continue
        info_file = biz_dir / "info.json"
        if not info_file.exists():
            continue
        try:
            data = json.loads(info_file.read_text(encoding="utf-8"))
            if data.get("name"):
                biz_data[biz_dir.name] = data
        except Exception:
            pass
    return biz_data


def _find_matching_biz(deploy_name, biz_data):
    parts = deploy_name.split('-', 1)
    if len(parts) < 2:
        return None
    if parts[0].startswith('SR'):
        slug_part = '-'.join(parts[1].split('-', 1)[1:]) if '-' in parts[1] else ''
    else:
        slug_part = parts[1] if len(parts) > 1 else ''
    if not slug_part:
        return None
    for dirname, data in biz_data.items():
        if _slugify(data['name']) == slug_part:
            return data
    for dirname, data in biz_data.items():
        if slug_part in _slugify(data['name']) or _slugify(data['name']) in slug_part:
            return data
    return None


def _generate_hub_and_report():
    """Generate index.html (CRM hub) and informe-comercial.html for all deployed sites."""
    from pathlib import Path
    deploy_dir = BASE / "deploy"
    ch_data = _load_biz_data(BASE / "negocios_chinchina")
    sr_data = _load_biz_data(BASE / "negocios")

    dep_dirs = sorted([
        d.name for d in deploy_dir.iterdir()
        if d.is_dir() and (d.name[0].isdigit() or d.name.startswith('SR'))
    ])

    biz_list = []
    for dn in dep_dirs:
        if dn.startswith('SR'):
            match_data = _find_matching_biz(dn, sr_data)
            loc_short = "Santa Rosa"
        else:
            match_data = _find_matching_biz(dn, ch_data)
            loc_short = "Chinchiná"
        idx_match = re.search(r'(?:SR-)?(\d+)', dn)
        idx = int(idx_match.group(1)) if idx_match else 0
        biz_list.append({
            "idx": idx, "name": match_data.get("name", dn) if match_data else dn.split('-', 2)[-1].replace('-', ' ').title(),
            "slug": dn, "rating": match_data.get("rating", 0) if match_data else 0,
            "address": match_data.get("address", "") if match_data else "",
            "phone": match_data.get("phone", "") if match_data else "",
            "social": match_data.get("social_media", {}) if match_data else {},
            "location_short": loc_short,
        })
    biz_list.sort(key=lambda b: b['idx'])

    # External sites for Chinchiná
    EXTERNAL_SITES = [
        {"idx": 21, "name": "La Herencia Bar", "slug": "la-herencia-bar", "url": "https://laherencia.vercel.app/", "location": "chinchina", "location_short": "Chinchiná", "rating": 0, "address": "", "phone": "", "social": {}},
        {"idx": 22, "name": "Exercise Gym", "slug": "exercise-gym", "url": "https://exer-gym.vercel.app/", "location": "chinchina", "location_short": "Chinchiná", "rating": 0, "address": "", "phone": "", "social": {}},
        {"idx": 23, "name": "Casa Box", "slug": "casa-box", "url": "https://casabox.vercel.app/", "location": "chinchina", "location_short": "Chinchiná", "rating": 0, "address": "", "phone": "", "social": {}},
        {"idx": 24, "name": "Gym Body Building", "slug": "gym-body-building", "url": "https://gym-body-building.vercel.app/", "location": "chinchina", "location_short": "Chinchiná", "rating": 0, "address": "", "phone": "", "social": {}},
    ]
    for site in EXTERNAL_SITES:
        biz_list.append(site)

    biz_json = json.dumps([{
        "idx": b["idx"], "name": _safe_name(b["name"]), "slug": b["slug"],
        "loc": b["location_short"], "rating": b["rating"],
        "phone": b.get("phone", ""), "address": _safe_name(b.get("address", ""))
    } for b in biz_list], ensure_ascii=False)

    STATUSES = ["Pendiente", "Contactado", "1er Seguimiento", "2do Seguimiento", "Cerrado"]

    cards = []
    for b in biz_list:
        color = _get_theme_color(b['idx'])
        loc_class = b.get("location", "chinchina" if b['idx'] <= 10 else "santarosa")
        addr = _safe_name(b.get('address', ''))
        phone = b.get('phone', '')
        name = _safe_name(b['name'])
        phone_part = f' · 📞 {phone}' if phone else ''
        opts = ''.join(f'<option value="{s}">{s}</option>' for s in STATUSES)
        cards.append(
            f'  <div class="card" data-location="{loc_class}" data-idx="{b["idx"]}">'
            f'<div class="bar" style="background:{color}"></div>\n'
            f'    <h3>#{b["idx"]} {name}</h3>\n'
            f'    <div class="rating">★ {b["rating"]} · {b["location_short"]}</div>\n'
            f'    <div class="info">{addr}{phone_part}</div>\n'
            f'    <div class="actions">\n'
            f'      <a href="{b.get("url", f"./{b["slug"]}/")}" target="_blank" class="visit">👁 Ver sitio</a>\n'
            f'    </div>\n'
            f'    <div class="crm-row">\n'
            f'      <select class="crm-status" data-idx="{b["idx"]}" '
            f'onchange="updateCRM({b["idx"]}, this.value)">{opts}</select>\n'
            f'      <span class="crm-date" id="crm-date-{b["idx"]}"></span>\n'
            f'    </div></div>'
        )

    hub = (
        f'<!DOCTYPE html>\n<html lang="es"><head><meta charset="UTF-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
        f'<title>Sitios Web · Chinchiná + Santa Rosa de Cabal · CRM</title>\n'
        f'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">\n'
        f'<style>\n'
        f'*{{margin:0;padding:0;box-sizing:border-box}}'
        f'body{{font-family:\'Inter\',sans-serif;background:#07070d;color:#e8e8f0;'
        f'min-height:100vh;background-image:radial-gradient(ellipse at 20% 50%,'
        f'rgba(168,85,247,0.06) 0%,transparent 50%),radial-gradient(ellipse at 80% 50%,'
        f'rgba(59,130,246,0.06) 0%,transparent 50%)}}\n'
        f'.container{{max-width:1200px;margin:0 auto;padding:0 24px}}\n'
        f'header{{padding:40px 0 20px;text-align:center}}'
        f'header h1{{font-size:2.8rem;font-weight:900;'
        f'background:linear-gradient(135deg,#a855f7,#3b82f6);'
        f'-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}\n'
        f'header p{{color:#6666aa;margin-top:8px;font-size:1.05rem}}\n'
        f'.crm-summary{{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:16px auto;max-width:800px}}\n'
        f'.crm-stat{{padding:10px 20px;border-radius:12px;background:rgba(255,255,255,0.03);'
        f'border:1px solid rgba(255,255,255,0.06);text-align:center;min-width:100px}}\n'
        f'.crm-stat .num{{font-size:1.5rem;font-weight:800;color:white}}\n'
        f'.crm-stat .label{{font-size:0.7rem;color:#8888aa;text-transform:uppercase;letter-spacing:0.05em;margin-top:2px}}\n'
        f'.crm-stat.pendiente .num{{color:#f59e0b}}.crm-stat.contactado .num{{color:#3b82f6}}\n'
        f'.crm-stat.seguimiento1 .num{{color:#8b5cf6}}.crm-stat.seguimiento2 .num{{color:#ec4899}}\n'
        f'.crm-stat.cerrado .num{{color:#10b981}}\n'
        f'.loc-tabs{{display:flex;justify-content:center;gap:6px;margin:12px 0 20px;flex-wrap:wrap}}\n'
        f'.loc-tab{{padding:8px 18px;border-radius:100px;border:1px solid rgba(255,255,255,0.08);'
        f'background:rgba(255,255,255,0.03);color:#8888aa;font-size:0.8rem;font-weight:600;'
        f'cursor:pointer;transition:all 0.3s}}\n'
        f'.loc-tab:hover{{background:rgba(255,255,255,0.08);color:#ddd}}\n'
        f'.loc-tab.active{{background:rgba(168,85,247,0.2);border-color:#a855f7;color:#c084fc}}\n'
        f'.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;padding-bottom:60px}}\n'
        f'.card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);'
        f'border-radius:16px;padding:20px;transition:all 0.3s;position:relative;overflow:hidden}}\n'
        f'.card:hover{{transform:translateY(-4px);border-color:rgba(255,255,255,0.12);box-shadow:0 12px 40px rgba(0,0,0,0.3)}}\n'
        f'.card .bar{{position:absolute;top:0;left:0;right:0;height:4px}}\n'
        f'.card h3{{font-size:1rem;font-weight:700;margin-top:6px;color:white}}\n'
        f'.card .rating{{color:#fbbf24;font-size:0.85rem;font-weight:600;margin-top:4px}}\n'
        f'.card .info{{color:#6666aa;font-size:0.8rem;margin-top:6px;line-height:1.5}}\n'
        f'.card .actions{{margin-top:10px;display:flex;gap:6px;flex-wrap:wrap}}\n'
        f'.card .actions a{{padding:6px 14px;border-radius:100px;font-size:0.75rem;font-weight:600;'
        f'text-decoration:none;transition:all 0.2s;border:1px solid rgba(255,255,255,0.08);'
        f'color:#aaa;background:rgba(255,255,255,0.03)}}\n'
        f'.card .actions a:hover{{background:rgba(255,255,255,0.1);color:white}}\n'
        f'.card .actions .visit{{background:rgba(168,85,247,0.15);border-color:rgba(168,85,247,0.3);color:#c084fc}}\n'
        f'.card.hidden{{display:none}}\n'
        f'.crm-row{{display:flex;align-items:center;gap:8px;margin-top:10px;padding-top:10px;'
        f'border-top:1px solid rgba(255,255,255,0.04)}}\n'
        f'.crm-status{{flex:1;padding:6px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.1);'
        f'background:rgba(255,255,255,0.03);color:#ddd;font-size:0.75rem;font-weight:600;cursor:pointer;outline:none}}\n'
        f'.crm-status:focus{{border-color:#a855f7}}\n'
        f'.crm-status option{{background:#1a1a2e;color:#ddd}}\n'
        f'.crm-date{{font-size:0.65rem;color:#6666aa;white-space:nowrap}}\n'
        f'.crm-badge{{display:inline-block;font-size:0.6rem;padding:2px 8px;border-radius:100px;'
        f'font-weight:700;margin-left:6px;text-transform:uppercase;letter-spacing:0.03em}}\n'
        f'.informe-link{{display:block;text-align:center;padding:20px;margin:0 0 20px;'
        f'background:linear-gradient(135deg,rgba(168,85,247,0.08),rgba(59,130,246,0.08));'
        f'border:1px solid rgba(255,255,255,0.06);border-radius:16px;text-decoration:none;transition:all 0.3s}}\n'
        f'.informe-link:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,0,0,0.3)}}\n'
        f'.informe-link h2{{font-size:1.2rem;font-weight:700;color:white}}\n'
        f'.informe-link p{{color:#8888aa;font-size:0.85rem;margin-top:4px}}\n'
        f'.speech-modal{{display:none;position:fixed;z-index:1000;left:0;top:0;width:100%;height:100%;'
        f'background:rgba(0,0,0,0.7);align-items:center;justify-content:center}}\n'
        f'.speech-modal.open{{display:flex}}\n'
        f'.speech-content{{background:#0d0d18;border:1px solid rgba(255,255,255,0.1);'
        f'border-radius:16px;padding:30px;max-width:600px;width:90%;max-height:80vh;overflow-y:auto;position:relative}}\n'
        f'.speech-content h2{{font-size:1.3rem;font-weight:800;color:white;margin-bottom:8px}}\n'
        f'.speech-content .close-btn{{position:absolute;top:12px;right:16px;background:none;border:none;'
        f'color:#8888aa;font-size:1.5rem;cursor:pointer}}\n'
        f'.speech-content .close-btn:hover{{color:white}}\n'
        f'.speech-body{{font-size:0.9rem;line-height:1.7;color:#ccc;margin-top:16px}}\n'
        f'.speech-body p{{margin-bottom:10px}}\n'
        f'@media(max-width:768px){{header h1{{font-size:1.8rem}}.grid{{grid-template-columns:1fr}}'
        f'.crm-stat{{min-width:70px;padding:8px 12px}}.crm-stat .num{{font-size:1.2rem}}}}\n'
        f'</style></head><body>\n'
        f'<header><h1>🌐 CRM · Sitios Web</h1>'
        f'<p>{len(biz_list)} sitios · <strong>Chinchiná</strong> + <strong>Santa Rosa</strong> · Estado comercial en vivo</p></header>\n'
        f'<div class="container">\n'
        f'  <div class="crm-summary" id="crmSummary">\n'
        f'    <div class="crm-stat pendiente"><div class="num" id="stat-pendiente">0</div><div class="label">Pendiente</div></div>\n'
        f'    <div class="crm-stat contactado"><div class="num" id="stat-contactado">0</div><div class="label">Contactado</div></div>\n'
        f'    <div class="crm-stat seguimiento1"><div class="num" id="stat-seguimiento1">0</div><div class="label">1er Seg.</div></div>\n'
        f'    <div class="crm-stat seguimiento2"><div class="num" id="stat-seguimiento2">0</div><div class="label">2do Seg.</div></div>\n'
        f'    <div class="crm-stat cerrado"><div class="num" id="stat-cerrado">0</div><div class="label">Cerrado</div></div>\n'
        f'  </div>\n'
        f'  <a href="./informe-comercial.html" target="_blank" class="informe-link">'
        f'<h2>📊 Ver Informe Comercial</h2>'
        f'<p>Fichas técnicas, fortalezas y speech de venta para cada negocio</p></a>\n'
        f'  <div class="loc-tabs" id="locTabs">\n'
        f'    <button class="loc-tab" onclick="filterCRM(\'all\', this)">📍 Todos ({len(biz_list)})</button>\n'
        f'    <button class="loc-tab" onclick="filterCRM(\'chinchina\', this)">🏔 Chinchiná</button>\n'
        f'    <button class="loc-tab" onclick="filterCRM(\'santarosa\', this)">🌋 Santa Rosa</button>\n'
        f'    <button class="loc-tab" onclick="filterCRM(\'pendiente\', this)">⏳ Pendiente</button>\n'
        f'    <button class="loc-tab" onclick="filterCRM(\'cerrado\', this)">✅ Cerrados</button>\n'
        f'  </div>\n'
        f'  <div class="grid" id="bizGrid">\n'
        f'{chr(10).join(cards)}\n'
        f'  </div>\n'
        f'</div>\n\n'
        f'<div class="speech-modal" id="speechModal">\n'
        f'  <div class="speech-content">\n'
        f'    <button class="close-btn" onclick="closeSpeech()">✕</button>\n'
        f'    <h2 id="speechTitle"></h2>\n'
        f'    <div class="speech-body" id="speechBody"></div>\n'
        f'  </div>\n'
        f'</div>\n\n'
        f'<script>\n'
        f'const BIZ = {biz_json};\n'
        f'const STORAGE_KEY = \'webbuilder_crm\';\n'
        f'const STATUSES = {json.dumps(STATUSES, ensure_ascii=False)};\n\n'
        f'function loadCRM() {{'
        f'try {{ return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {{}}; }} catch(e) {{ return {{}}; }}}}\n'
        f'function saveCRM(data) {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }}\n'
        f'function getStatus(data, idx) {{ return data[idx] ? data[idx].s : \'Pendiente\'; }}\n\n'
        f'function updateCRM(idx, status) {{\n'
        f'  const data = loadCRM();\n'
        f'  const now = new Date();\n'
        f'  const dateStr = now.toLocaleDateString(\'es-CO\', {{day:\'2-digit\', month:\'2-digit\', year:\'numeric\'}});\n'
        f'  data[idx] = {{ s: status, d: dateStr }};\n'
        f'  saveCRM(data);\n'
        f'  document.getElementById(\'crm-date-\' + idx).textContent = dateStr;\n'
        f'  updateStats();\n'
        f'  updateFilterBadges();\n'
        f'}}\n\n'
        f'function updateStats() {{\n'
        f'  const data = loadCRM();\n'
        f'  const counts = {{}};\n'
        f'  STATUSES.forEach(s => counts[s] = 0);\n'
        f'  BIZ.forEach(b => {{ const s = getStatus(data, b.idx); counts[s] = (counts[s] || 0) + 1; }});\n'
        f'  STATUSES.forEach(s => {{\n'
        f'    let id = \'stat-pendiente\';\n'
        f'    if (s === \'Pendiente\') id = \'stat-pendiente\';\n'
        f'    else if (s === \'Contactado\') id = \'stat-contactado\';\n'
        f'    else if (s === \'1er Seguimiento\') id = \'stat-seguimiento1\';\n'
        f'    else if (s === \'2do Seguimiento\') id = \'stat-seguimiento2\';\n'
        f'    else if (s === \'Cerrado\') id = \'stat-cerrado\';\n'
        f'    document.getElementById(id).textContent = counts[s] || 0;\n'
        f'  }});\n'
        f'}}\n\n'
        f'const STATUS_COLORS = {{\n'
        f'  \'Pendiente\': \'rgba(245,158,11,0.15)\',\'Contactado\': \'rgba(59,130,246,0.15)\',\n'
        f'  \'1er Seguimiento\': \'rgba(139,92,246,0.15)\',\'2do Seguimiento\': \'rgba(236,72,153,0.15)\',\n'
        f'  \'Cerrado\': \'rgba(16,185,129,0.15)\',\n'
        f'}};\n'
        f'const STATUS_TEXT = {{\n'
        f'  \'Pendiente\': \'#f59e0b\',\'Contactado\': \'#3b82f6\',\n'
        f'  \'1er Seguimiento\': \'#8b5cf6\',\'2do Seguimiento\': \'#ec4899\',\'Cerrado\': \'#10b981\',\n'
        f'}};\n\n'
        f'function updateFilterBadges() {{\n'
        f'  const data = loadCRM();\n'
        f'  document.querySelectorAll(\'.card\').forEach(card => {{\n'
        f'    const idx = parseInt(card.dataset.idx);\n'
        f'    const s = getStatus(data, idx);\n'
        f'    let badge = card.querySelector(\'.crm-badge\');\n'
        f'    if (!badge) {{ badge = document.createElement(\'span\'); badge.className = \'crm-badge\'; card.querySelector(\'h3\').appendChild(badge); }}\n'
        f'    badge.textContent = s;\n'
        f'    badge.style.background = STATUS_COLORS[s] || \'rgba(255,255,255,0.08)\';\n'
        f'    badge.style.color = STATUS_TEXT[s] || \'#aaa\';\n'
        f'  }});\n'
        f'}}\n\n'
        f'function filterCRM(filter, btn) {{\n'
        f'  document.querySelectorAll(\'.loc-tab\').forEach(b => b.classList.remove(\'active\'));\n'
        f'  if (btn) btn.classList.add(\'active\');\n'
        f'  const data = loadCRM();\n'
        f'  document.querySelectorAll(\'.card\').forEach(card => {{\n'
        f'    const loc = card.dataset.location;\n'
        f'    const idx = parseInt(card.dataset.idx);\n'
        f'    const s = getStatus(data, idx);\n'
        f'    let visible = true;\n'
        f'    if (filter === \'chinchina\') visible = loc === \'chinchina\';\n'
        f'    else if (filter === \'santarosa\') visible = loc === \'santarosa\';\n'
        f'    else if (filter === \'pendiente\') visible = s === \'Pendiente\';\n'
        f'    else if (filter === \'cerrado\') visible = s === \'Cerrado\';\n'
        f'    card.classList.toggle(\'hidden\', !visible);\n'
        f'  }});\n'
        f'}}\n\n'
        f'async function mergeCallerCRM() {{\n'
        f'  try {{\n'
        f'    const resp = await fetch(\'./crm_state.json\');\n'
        f'    if (!resp.ok) return;\n'
        f'    const callerData = await resp.json();\n'
        f'    const local = loadCRM();\n'
        f'    for (const [idx, val] of Object.entries(callerData)) {{\n'
        f'      if (!local[idx] || new Date(val.d) >= new Date(local[idx].d)) {{\n'
        f'        local[idx] = val;\n'
        f'      }}\n'
        f'    }}\n'
        f'    saveCRM(local);\n'
        f'  }} catch(e) {{}}\n'
        f'}}\n\n'
        f'document.addEventListener(\'DOMContentLoaded\', async function() {{\n'
        f'  await mergeCallerCRM();\n'
        f'  const data = loadCRM();\n'
        f'  BIZ.forEach(b => {{\n'
        f'    const sel = document.querySelector(\'.crm-status[data-idx="\' + b.idx + \'"]\');\n'
        f'    if (sel) {{\n'
        f'      sel.value = getStatus(data, b.idx);\n'
        f'      const d = data[b.idx];\n'
        f'      if (d) document.getElementById(\'crm-date-\' + b.idx).textContent = d.d || \'\';\n'
        f'    }}\n'
        f'  }});\n'
        f'  updateStats();\n'
        f'  updateFilterBadges();\n'
        f'  const allBtn = document.querySelector(\'.loc-tab\');\n'
        f'  if (allBtn) allBtn.classList.add(\'active\');\n'
        f'}});\n'
        f'</script></body></html>'
    )

    # Simple text-based report (no CRM)
    tabs = ['    <button class="tab-btn active" onclick="showPage(\'all\')">📋 Ver Todos</button>']
    pages = []
    for b in biz_list:
        color = _get_theme_color(b['idx'])
        name = _safe_name(b['name'])
        addr = _safe_name(b.get('address', 'No disponible'))
        phone = b.get('phone', 'No disponible') or 'No disponible'
        rating = b.get('rating', 0) or 0
        tabs.append(f'    <button class="tab-btn" onclick="showPage(\'{b["slug"]}\')">#{b["idx"]} {name[:30]}</button>')
        fortalezas = []
        if phone and phone != 'No disponible':
            fortalezas.append('Teléfono disponible')
        if b.get('social'):
            fortalezas.append(f'Redes sociales activas ({", ".join(list(b["social"].keys())[:3])})')
        if rating >= 4.0:
            fortalezas.append(f'{rating} estrellas')
        ft = ', '.join(fortalezas) if fortalezas else 'Potencial digital por desarrollar'
        pages.append(
            f'<section class="business-page" data-slug="{b["slug"]}" style="border-color:{color}">\n'
            f'  <div class="page-header" style="background:linear-gradient(135deg,{color},#0a0a0f);">\n'
            f'    <span class="badge">#{b["idx"]} · {b["location_short"]}</span>\n'
            f'    <h2>{name}</h2>\n'
            f'    <div class="rating">★ {rating} / 5.0</div>\n'
            f'  </div>\n'
            f'  <div class="page-body">\n'
            f'    <div class="info-grid">\n'
            f'      <div class="info-card"><h4>📋 Información</h4><table>'
            f'<tr><td>Dirección</td><td>{addr}</td></tr>'
            f'<tr><td>Teléfono</td><td>{phone}</td></tr>'
            f'<tr><td>Calificación</td><td>★ {rating} / 5.0</td></tr></table></div>\n'
            f'      <div class="info-card"><h4>🌐 Incluye</h4><ul>'
            f'<li>✅ Diseño Framer Motion</li><li>✅ Hero + Galería</li>'
            f'<li>✅ Mapa + Contacto</li><li>✅ WhatsApp</li>'
            f'<li>✅ Responsive</li></ul></div>\n'
            f'      <div class="info-card full-width"><h4>💪 Fortalezas</h4><p>{ft}</p></div>\n'
            f'      <div class="info-card full-width"><h4>🎯 Speech</h4>'
            f'<div class="speech"><p><strong>Tú:</strong> "Don [nombre], le traigo la página web de '
            f'<strong>{name}</strong>, completamente terminada."</p>'
            f'<p><strong>Tú:</strong> "Tiene galería, mapa, WhatsApp, y se ve perfecta en celular y computador."</p>'
            f'<p><strong>Clave:</strong> "Usted ya tiene {rating} estrellas. Con esta página va a multiplicar sus clientes."</p>'
            f'</div></div>\n'
            f'    </div>\n'
            f'  </div>\n'
            f'</section>'
        )

    report = (
        f'<!DOCTYPE html>\n<html lang="es"><head><meta charset="UTF-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
        f'<title>Informe Comercial · {len(biz_list)} Sitios</title>\n'
        f'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">\n'
        f'<style>\n'
        f'*{{margin:0;padding:0;box-sizing:border-box}} body{{font-family:\'Inter\',sans-serif;background:#07070d;color:#e8e8f0}}\n'
        f'.container{{max-width:1200px;margin:0 auto;padding:0 20px}}\n'
        f'.main-header{{background:linear-gradient(135deg,#0a0a1a,#1a0a2e,#0a0a1a);padding:60px 0 40px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.05)}}\n'
        f'.main-header h1{{font-size:2.5rem;font-weight:900;background:linear-gradient(135deg,#a855f7,#3b82f6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}\n'
        f'.main-header p{{color:#8888aa;margin-top:12px;font-size:1.1rem;max-width:700px;margin:12px auto 0;line-height:1.6}}\n'
        f'.main-header .meta{{color:#6666aa;font-size:0.85rem;margin-top:16px}}\n'
        f'.main-header .meta span{{margin:0 12px}}\n'
        f'.tab-bar{{display:flex;overflow-x:auto;gap:6px;padding:20px 0;margin-bottom:10px;scrollbar-width:thin}}\n'
        f'.tab-btn{{flex-shrink:0;padding:8px 18px;border-radius:100px;border:1px solid rgba(255,255,255,0.08);background:rgba(255,255,255,0.03);color:#8888aa;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all 0.3s;white-space:nowrap}}\n'
        f'.tab-btn:hover{{background:rgba(255,255,255,0.08);color:#ddd}}\n'
        f'.tab-btn.active{{background:rgba(168,85,247,0.2);border-color:#a855f7;color:#c084fc}}\n'
        f'.business-page{{display:none;border-left:4px solid;border-radius:16px;background:#0d0d18;margin-bottom:30px;animation:fadeIn 0.4s ease}}\n'
        f'.business-page.active{{display:block}}\n'
        f'@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}\n'
        f'.page-header{{padding:40px 40px 30px}}\n'
        f'.page-header .badge{{display:inline-block;padding:4px 14px;border-radius:100px;background:rgba(255,255,255,0.08);font-size:0.75rem;font-weight:600;color:#aaa;margin-bottom:12px;text-transform:uppercase;letter-spacing:0.05em}}\n'
        f'.page-header h2{{font-size:2rem;font-weight:800;color:white}}\n'
        f'.page-header .rating{{margin-top:8px;font-size:1.1rem;font-weight:700;color:#fbbf24}}\n'
        f'.page-body{{padding:0 40px 40px}}\n'
        f'.info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}\n'
        f'.info-card{{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:12px;padding:24px}}\n'
        f'.info-card h4{{font-size:0.9rem;font-weight:700;color:#c084fc;margin-bottom:16px;text-transform:uppercase;letter-spacing:0.03em}}\n'
        f'.info-card.full-width{{grid-column:1/-1}}\n'
        f'.info-card table{{width:100%;border-collapse:collapse}}\n'
        f'.info-card td{{padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.9rem;word-break:break-word}}\n'
        f'.info-card td:first-child{{color:#8888aa;font-weight:600;width:120px}}\n'
        f'.info-card td:last-child{{color:#ddd}}\n'
        f'.info-card ul{{list-style:none}}\n'
        f'.info-card ul li{{padding:4px 0;font-size:0.9rem;color:#ccc}}\n'
        f'.speech{{font-size:0.95rem;line-height:1.7;color:#ddd}}\n'
        f'.speech p{{margin-bottom:10px}}\n'
        f'.cta-section{{background:linear-gradient(135deg,rgba(168,85,247,0.1),rgba(59,130,246,0.1));border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:40px;text-align:center;margin-top:40px}}\n'
        f'.cta-section h3{{font-size:1.5rem;font-weight:800;color:white;margin-bottom:12px}}\n'
        f'.cta-section p{{color:#8888aa;max-width:600px;margin:0 auto;line-height:1.6}}\n'
        f'.ver-pagina-btn{{display:inline-block;padding:10px 24px;border-radius:100px;background:rgba(255,255,255,0.06);color:#aaa;font-weight:600;font-size:0.85rem;text-decoration:none;margin-top:12px;transition:all 0.2s;border:1px solid rgba(255,255,255,0.08)}}\n'
        f'.ver-pagina-btn:hover{{background:rgba(255,255,255,0.1);color:white}}\n'
        f'@media(max-width:768px){{.info-grid{{grid-template-columns:1fr}}.page-header,.page-body{{padding-left:20px;padding-right:20px}}.page-header h2{{font-size:1.5rem}}.container{{padding:0 12px}}.main-header{{padding:40px 0 30px}}.main-header h1{{font-size:1.8rem}}.main-header .meta span{{display:block;margin:4px 0}}.cta-section{{padding:24px 16px;border-radius:12px}}.info-card{{padding:16px}}}}\n'
        f'@media print{{.tab-bar,.main-header .meta,.ver-pagina-btn{{display:none}}.business-page{{display:block!important;page-break-after:always}}body{{background:white;color:black}}.business-page{{background:white;border-color:#ddd!important}}.page-header{{background:#f5f5f5!important}}.page-header h2{{color:black!important}}.info-card{{background:#fafafa;border-color:#eee}}.info-card td:last-child,.info-card ul li,.speech{{color:#333}}.cta-section{{display:none}}}}\n'
        f'</style></head><body>\n'
        f'<div class="main-header"><div class="container">\n'
        f'  <h1>🚀 Informe Comercial</h1>\n'
        f'  <p>{len(biz_list)} sitios profesionales · <strong>Chinchiná</strong> + <strong>Santa Rosa</strong></p>\n'
        f'  <div class="meta"><span>📅 08/05/2026</span><span>📍 {len(biz_list)} sitios</span></div>\n'
        f'</div></div>\n'
        f'<div class="container">\n'
        f'  <div class="tab-bar" id="tabBar">\n'
        f'{chr(10).join(tabs)}\n'
        f'  </div>\n'
        f'  <div id="pagesContainer">\n'
        f'{chr(10).join(pages)}\n'
        f'  </div>\n'
        f'  <div class="cta-section">\n'
        f'    <h3>¿Listo para tener tu página web?</h3>\n'
        f'    <p>Estos sitios están 100% funcionales y listos para publicarse.</p>\n'
        f'    <div style="margin-top:20px;display:flex;gap:12px;justify-content:center;flex-wrap:wrap">\n'
    )
    for b in biz_list:
        report += f'<a href="{b.get("url", f"./{b["slug"]}/")}" target="_blank" class="ver-pagina-btn" style="border-color:{_get_theme_color(b["idx"])}">👁 {_safe_name(b["name"][:22])}</a>\n'
    report += (
        '    </div>\n'
        '  </div>\n'
        '</div>\n'
        '<script>\n'
        'function showPage(slug){\n'
        '  document.querySelectorAll(\'.tab-btn\').forEach(b=>b.classList.remove(\'active\'));\n'
        '  event.target.classList.add(\'active\');\n'
        '  document.querySelectorAll(\'.business-page\').forEach(p=>{\n'
        '    p.classList.toggle(\'active\',slug===\'all\'||p.dataset.slug===slug);\n'
        '  });\n'
        '}\n'
        '</script></body></html>'
    )

    for sub in ["sitios-web", "deploy"]:
        (BASE / sub / "index.html").write_text(hub, encoding="utf-8")
        (BASE / sub / "informe-comercial.html").write_text(report, encoding="utf-8")
        crm_src = BASE / "crm_state.json"
        if crm_src.exists():
            import shutil
            shutil.copy2(str(crm_src), str(BASE / sub / "crm_state.json"))


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="webuilder — Scrape, build, and deploy business websites.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python webuilder.py scrape --location \"Pereira, Risaralda\"\n"
            "  python webuilder.py build --dir negocios --prefix PE --start-idx 21\n"
            "  python webuilder.py hub\n"
            "  python webuilder.py serve --port 4000\n"
            "  python webuilder.py deploy\n"
            "  python webuilder.py all --location \"Pereira, Risaralda\" --prefix PE\n"
        )
    )
    sub = parser.add_subparsers(dest="command")

    p_scrape = sub.add_parser("scrape", help="Scrape Google Maps for businesses")
    p_scrape.add_argument("--location", default="Santa Rosa de Cabal, Risaralda",
                          help="City and department (e.g. \"Pereira, Risaralda\")")

    p_build = sub.add_parser("build", help="Build websites from scraped data")
    p_build.add_argument("--dir", default="negocios", help="Data directory")
    p_build.add_argument("--prefix", default="SR", help="Site prefix (e.g. SR, PE)")
    p_build.add_argument("--start-idx", type=int, default=11, help="Starting index")

    p_hub = sub.add_parser("hub", help="Generate hub page + sales report")

    p_serve = sub.add_parser("serve", help="Start local dev server")
    p_serve.add_argument("--port", default="4000", help="Port number")

    p_deploy = sub.add_parser("deploy", help="Deploy to Vercel")

    p_all = sub.add_parser("all", help="Full pipeline: scrape → build → hub → deploy")
    p_all.add_argument("--location", default="Santa Rosa de Cabal, Risaralda",
                       help="City and department")
    p_all.add_argument("--prefix", default="SR", help="Site prefix")
    p_all.add_argument("--dir", default="negocios", help="Data directory")

    args = parser.parse_args()
    cmds = {
        "scrape": lambda: cmd_scrape({"location": args.location}),
        "build": lambda: cmd_build({"dir": args.dir, "prefix": args.prefix, "start_idx": str(args.start_idx)}),
        "hub": lambda: cmd_hub({}),
        "serve": lambda: cmd_serve({"port": args.port}),
        "deploy": lambda: cmd_deploy({}),
        "all": lambda: cmd_all({"location": args.location, "prefix": args.prefix, "dir": args.dir}),
    }
    fn = cmds.get(args.command)
    if fn:
        sys.exit(fn())
    parser.print_help()


if __name__ == "__main__":
    main()
