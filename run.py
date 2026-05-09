#!/usr/bin/env python3
"""
WebBuilder - Scraper de Google Maps.
Guarda incrementalmente para no perder datos.
Uso: python run.py [--location "Ciudad, Departamento"]
"""
import os, json, re, shutil, time, sys, functools, argparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

print = functools.partial(print, flush=True)

BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "negocios"
TEMPLATE_DIR = BASE_DIR / "exercise-gym"

C = {"cyan": "\033[96m", "green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m", "bold": "\033[1m", "end": "\033[0m"}
p = lambda c, t: f"{C.get(c,'')}{t}{C['end']}"

MAX_PER_QUERY = 12

def create_driver():
    opt = webdriver.ChromeOptions()
    opt.add_argument("--no-sandbox")
    opt.add_argument("--disable-dev-shm-usage")
    opt.add_argument("--window-size=1280,900")
    opt.add_argument("--lang=es-CO")
    d = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opt)
    d.set_page_load_timeout(12)
    return d

def safe_txt(el):
    try: return el.text.strip()
    except: return ""

def safe_attr(el, a):
    try: return el.get_attribute(a) or ""
    except: return ""

def safe_click(d, el):
    try:
        d.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.2)
        d.execute_script("arguments[0].click();", el)
        return True
    except:
        try: el.click(); return True
        except: return False

def extract_socials(url):
    if not url: return {}
    socials = {}
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200: return socials
        soup = BeautifulSoup(r.text, "html.parser")
        patterns = {
            "facebook": r"facebook\.com/[\w.]+",
            "instagram": r"instagram\.com/[\w.]+",
            "twitter": r"(?:twitter\.com|x\.com)/[\w.]+",
            "youtube": r"youtube\.com/@?[\w-]+",
            "tiktok": r"tiktok\.com/@?[\w.]+",
            "linkedin": r"linkedin\.com/(?:company|in)/[\w-]+",
            "whatsapp": r"(?:wa\.me|api\.whatsapp\.com/send)[^\s\"'>]+",
        }
        for tag in soup.find_all(["a", "link"], href=True):
            h = tag["href"]
            for plat, pat in patterns.items():
                m = re.search(pat, h, re.I)
                if m and plat not in socials:
                    socials[plat] = m.group(0) if "://" in m.group(0) else f"https://{m.group(0)}"
        text = soup.get_text()
        for plat, pat in patterns.items():
            if plat not in socials:
                m = re.search(pat, text, re.I)
                if m:
                    socials[plat] = m.group(0) if "://" in m.group(0) else f"https://{m.group(0)}"
    except: pass
    return socials

def get_links(d):
    links = set()
    for sel in ['[role="feed"]', '.m6QErb.DxyMkb', '.m6QErb']:
        panel = d.find_elements(By.CSS_SELECTOR, sel)
        if panel:
            for _ in range(25):
                prev = len(links)
                d.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", panel[0])
                time.sleep(1.2)
                for a in d.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]'):
                    h = safe_attr(a, "href")
                    if h: links.add(h)
                if len(links) == prev: break
            break
    if not links:
        for a in d.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]'):
            h = safe_attr(a, "href")
            if h: links.add(h)
    return list(links)

def scrape_business(d, url, short_loc=None):
    try:
        d.set_page_load_timeout(10)
        d.get(url)
    except:
        pass  # timeout ok, page may have partially loaded
    time.sleep(2.5)

    info = {"name":"","address":"","phone":"","website":"","rating":0,"rating_total":0,
            "reviews":[],"opening_hours":[],"types":[],"social_media":{},"photos":[],"google_maps_url":d.current_url}

    body = d.find_element(By.TAG_NAME, "body")
    page_text = body.text

    # Name
    for sel in ["h1", ".DUwDvf"]:
        els = d.find_elements(By.CSS_SELECTOR, sel)
        if els:
            n = safe_txt(els[0])
            if n and len(n) < 100:
                info["name"] = n; break

    # Rating
    for el in d.find_elements(By.CSS_SELECTOR, '[role="img"][aria-label*="estrella"]'):
        aria = safe_attr(el, "aria-label")
        m = re.search(r'([\d.]+)', aria)
        if m: info["rating"] = float(m.group(1)); break

    # Address
    for el in d.find_elements(By.CSS_SELECTOR, '[data-item-id="address"]'):
        t = safe_txt(el)
        t = re.sub(r'[\ue000-\uf8ff]', '', t).strip()
        t = re.sub(r'\s+', ' ', t)
        if t: info["address"] = t; break
    if not info["address"] and short_loc:
        loc_parts = short_loc.replace('\u00e1','a').replace('\u00e9','e').replace('\u00ed','i').replace('\u00f3','o').replace('\u00fa','u').replace('\u00f1','n')
        m = re.search(r'[A-Z0-9]{4}\+[A-Z0-9]{2,3}[^,]*' + re.escape(loc_parts[:15]), page_text, re.I)
        if m: info["address"] = m.group(0).strip()
        else:
            for line in page_text.split('\n'):
                if any(p in line.lower() for p in [short_loc.lower(), loc_parts[:10].lower()]) and len(line) < 120:
                    info["address"] = line.strip(); break

    # Phone
    for a in d.find_elements(By.CSS_SELECTOR, 'a[href^="tel:"]'):
        tel = safe_attr(a, "href").replace("tel:","")
        if tel: info["phone"] = tel; break

    # Website
    for a in d.find_elements(By.TAG_NAME, "a"):
        href = safe_attr(a, "href")
        if href and href.startswith("http") and "google" not in href and "facebook" not in href and "instagram" not in href:
            if not any(x in href for x in ["business.google", "support.google", "policies.google"]):
                info["website"] = href; break

    # Hours
    for el in d.find_elements(By.CSS_SELECTOR, '[data-item-id="oh"], [data-item-id*="hour"]'):
        t = re.sub(r'[\ue000-\uf8ff]', '', safe_txt(el)).strip()
        if t and any(k in t for k in ['Abierto','Cerrado','a.m.','p.m.']):
            info["opening_hours"] = [t]; break
    if not info["opening_hours"]:
        m = re.search(r'(Abierto[^。\n]{5,60})', page_text)
        if m: info["opening_hours"] = [m.group(1).strip()]

    # Rating total
    m = re.search(r'(\d[\d,]*)\s*reseñas?', page_text, re.I)
    if m: info["rating_total"] = int(m.group(1).replace(",",""))

    # Reviews
    for sel in ['button[aria-label*="reseña"]', '[jsaction*="review"]']:
        els = d.find_elements(By.CSS_SELECTOR, sel)
        if els:
            safe_click(d, els[0]); time.sleep(1); break
    body2 = d.find_element(By.TAG_NAME, "body").text
    for block in re.split(r'\n{2,}', body2):
        if any(s in block for s in ['★★★★★','★★★★☆','★★★☆☆','★★☆☆☆','★☆☆☆☆']):
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            txt = ' '.join(lines[1:3])
            if len(txt) > 15:
                info["reviews"].append({"author":lines[1] if len(lines)>1 else "","rating":0,"text":txt[:300]})
            if len(info["reviews"])>=3: break

    # Photos - click Fotos tab
    for sel in ['button[aria-label*="Fotos"]', '[jsaction*="photo"]']:
        els = d.find_elements(By.CSS_SELECTOR, sel)
        if els:
            safe_click(d, els[0]); time.sleep(1.5); break
    seen = set()
    for img in d.find_elements(By.TAG_NAME, "img"):
        src = safe_attr(img, "src")
        if not src or "branding/mapslogo" in src or "GoogleMaps_Logo" in src: continue
        if src in seen: continue
        if "lh3.google" in src or ("google" in src and "maps" in src):
            seen.add(src)
            info["photos"].append({"url":src,"width":0,"height":0})
        if len(info["photos"]) >= 12: break

    # Social media from website
    if info["website"]:
        print(f"      → Redes...")
        info["social_media"] = extract_socials(info["website"])

    return info

def save_business(b):
    safe = re.sub(r'[^\w\s-]', '', b["name"]).strip().replace(" ", "_")
    safe = re.sub(r'_+', '_', safe)[:60]
    biz_dir = DATA_DIR / safe
    if biz_dir.exists():
        return  # already saved
    biz_dir.mkdir(parents=True, exist_ok=True)
    # Save info
    with open(biz_dir / "info.json", "w", encoding="utf-8") as f:
        json.dump(b, f, ensure_ascii=False, indent=2)
    # Download photos
    pd = biz_dir / "fotos"
    for pi, photo in enumerate(b.get("photos", [])):
        url = photo.get("url","")
        if not url: continue
        try:
            r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
            if r.status_code == 200:
                ct = r.headers.get("content-type","")
                ext = ".webp" if "webp" in ct else ".png" if "png" in ct else ".jpg"
                (pd / f"foto_{pi+1}{ext}").parent.mkdir(parents=True, exist_ok=True)
                (pd / f"foto_{pi+1}{ext}").write_bytes(r.content)
        except: pass
    return biz_dir

def main():
    parser = argparse.ArgumentParser(description="Scrape Google Maps businesses")
    parser.add_argument("--location", default="Chinchin\u00e1, Caldas",
                        help="Ubicaci\u00f3n a scrapear (ej: 'Santa Rosa de Cabal, Caldas')")
    args = parser.parse_args()
    LOC = args.location
    SHORT_LOC = LOC.split(",")[0].strip()
    QUERIES = [
        f"negocios en {LOC}",
        f"restaurantes en {LOC}",
        f"tiendas en {LOC}",
    ]

    print(f"\n  {p('bold', '╔══════════════════════════════════════════╗')}")
    print(f"  {p('bold', f'║   WEBBUILDER - {SHORT_LOC.upper():<20} ║')}")
    print(f"  {p('bold', '║   Scrapeo incremental sin perder datos  ║')}")
    print(f"  {p('bold', '╚══════════════════════════════════════════╝')}\n")

    d = create_driver()
    seen_names = set()
    total_saved = 0
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load previously saved names to avoid duplicates
    for biz_dir in DATA_DIR.iterdir():
        if biz_dir.is_dir() and (biz_dir / "info.json").exists():
            try:
                with open(biz_dir / "info.json") as f:
                    data = json.load(f)
                if data.get("name"):
                    seen_names.add(data["name"].lower())
                    total_saved += 1
            except: pass

    if total_saved > 0:
        print(f"  {p('green', f'Ya hay {total_saved} negocios guardados. Continuando...')}\n")

    for qidx, query in enumerate(QUERIES):
        if total_saved >= MAX_PER_QUERY * len(QUERIES):
            break
        print(f"\n  {p('bold', f'[{qidx+1}/{len(QUERIES)}]')} Buscando: {p('cyan', query)}")
        d.get(f"https://www.google.com/maps/search/{query.replace(' ', '+')}/")
        time.sleep(4)

        links = get_links(d)
        print(f"  → {len(links)} enlaces")

        count = 0
        for url in links:
            if count >= MAX_PER_QUERY:
                break
            if total_saved >= MAX_PER_QUERY * len(QUERIES):
                break
            try:
                info = scrape_business(d, url, SHORT_LOC)
                name = info.get("name","")
                if not name:
                    print(f"    {p('yellow', 'Sin nombre')}")
                    continue
                if name.lower() in seen_names:
                    print(f"    {p('yellow', f'Duplicado: {name}')}")
                    continue
                seen_names.add(name.lower())
                count += 1
                total_saved += 1

                print(f"\n  [{total_saved}] {p('cyan', name)}")
                print(f"      Dir: {info.get('address','N/A')[:60]}")
                print(f"      Tel: {info.get('phone','N/A')}")
                print(f"      Web: {info.get('website','N/A')}")
                print(f"      Rating: {info.get('rating','N/A')} ({info.get('rating_total',0)})")
                print(f"      Fotos: {len(info.get('photos',[]))}")
                if info.get("social_media"):
                    for s, l in info["social_media"].items():
                        print(f"      {p('yellow', s.capitalize())}: {l}")

                save_business(info)
                print(f"      {p('green', '✓ Guardado')}")

            except Exception as e:
                print(f"    {p('red', f'Error: {e}')}")
                continue

    d.quit()

    # Final summary
    all_dirs = sorted([d for d in DATA_DIR.iterdir() if d.is_dir() and (d/"info.json").exists()])
    print(f"\n{'='*60}")
    print(f"  {p('bold', f'RECOLECCION COMPLETADA: {len(all_dirs)} negocios')}")
    print(f"{'='*60}")
    for i, d2 in enumerate(all_dirs, 1):
        with open(d2 / "info.json") as f:
            b = json.load(f)
        bn = b.get("name", "N/A")
        print(f"\n  {p('cyan', f'{i}. {bn}')}")
        print(f"     Direccion: {b.get('address','N/A')}")
        print(f"     Telefono:  {b.get('phone','N/A')}")
        print(f"     Web:       {b.get('website','N/A')}")
        soc = b.get("social_media", {})
        if soc:
            for s, l in soc.items():
                print(f"     {p('yellow', s.capitalize())}: {l}")
        print(f"     Fotos:     {len([x for x in (d2/'fotos').iterdir()]) if (d2/'fotos').exists() else 0}")

    print(f"\n  {p('green', 'Datos guardados en:')} {DATA_DIR}")
    print(f"\n  {p('bold', f'Listo! {len(all_dirs)} negocios de {SHORT_LOC} recolectados.')}")
    print(f"  {p('bold', 'Ahora dime que construya las paginas web.')}")

if __name__ == "__main__":
    main()
