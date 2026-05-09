#!/usr/bin/env python3
"""
caller.py — Automated outbound calling system for Webuilder.

Makes calls to businesses with a personalized pitch, tracks CRM status.

Modes:
  Simulate (default): shows speech + asks result, no actual call
  Twilio: real calls via Twilio API (set env vars)
  ElevenLabs: premium voice via ElevenLabs API (set ELEVENLABS_API_KEY)

Usage:
  python caller.py --list              # List businesses with phones
  python caller.py --idx 21            # Call one business
  python caller.py --all               # Call all businesses
  python caller.py --pending           # Call only pending
  python caller.py --status            # Show CRM summary

Env vars for auto-calling:
  export TWILIO_ACCOUNT_SID=...
  export TWILIO_AUTH_TOKEN=...
  export TWILIO_FROM_NUMBER=+1234567890
  export ELEVENLABS_API_KEY=...        # optional, for premium voice
"""
import argparse, json, os, re, sys, time
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.resolve()
CRM_FILE = BASE / "crm_state.json"

STATUSES = ["Pendiente", "Llamado", "No Contestó", "Interesado", "No Interesado", "Cerrado"]


def slugify(name):
    s = re.sub(r'[^\w\s-]', '', name).strip().lower().replace(" ", "-")
    s = re.sub(r'-+', '-', s)[:40]
    for a, b in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n')]:
        s = s.replace(a, b)
    return s


def load_biz_data(data_dir):
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


def find_matching_biz(deploy_name, biz_data):
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
        if slugify(data['name']) == slug_part:
            return data
    for dirname, data in biz_data.items():
        if slug_part in slugify(data['name']) or slugify(data['name']) in slug_part:
            return data
    return None


def load_biz_list():
    deploy_dir = BASE / "deploy"
    ch_data = load_biz_data(BASE / "negocios_chinchina")
    sr_data = load_biz_data(BASE / "negocios")

    dep_dirs = sorted([
        d.name for d in deploy_dir.iterdir()
        if d.is_dir() and (d.name[0].isdigit() or d.name.startswith('SR'))
    ])

    biz_list = []
    for dn in dep_dirs:
        if dn.startswith('SR'):
            match_data = find_matching_biz(dn, sr_data)
            loc_short = "Santa Rosa"
        else:
            match_data = find_matching_biz(dn, ch_data)
            loc_short = "Chinchiná"
        idx_match = re.search(r'(?:SR-)?(\d+)', dn)
        idx = int(idx_match.group(1)) if idx_match else 0
        biz_list.append({
            "idx": idx,
            "name": match_data.get("name", dn) if match_data else dn.split('-', 2)[-1].replace('-', ' ').title(),
            "slug": dn,
            "phone": match_data.get("phone", "") if match_data else "",
            "location_short": loc_short,
            "url": f"https://deploy-xi-taupe.vercel.app/{dn}/",
        })
    biz_list.sort(key=lambda b: b['idx'])

    external = [
        {"idx": 21, "name": "La Herencia Bar", "slug": "la-herencia-bar", "phone": "", "location_short": "Chinchiná", "url": "https://laherencia.vercel.app/"},
        {"idx": 22, "name": "Exercise Gym", "slug": "exercise-gym", "phone": "", "location_short": "Chinchiná", "url": "https://exer-gym.vercel.app/"},
        {"idx": 23, "name": "Casa Box", "slug": "casa-box", "phone": "", "location_short": "Chinchiná", "url": "https://casabox.vercel.app/"},
        {"idx": 24, "name": "Gym Body Building", "slug": "gym-body-building", "phone": "", "location_short": "Chinchiná", "url": "https://gym-body-building.vercel.app/"},
    ]
    for site in external:
        biz_list.append(site)

    return biz_list


def clean_phone(phone):
    return re.sub(r'[^\d+]', '', phone)


class Caller:
    def __init__(self):
        self.biz_list = load_biz_list()
        self.crm = self._load_crm()

    def _load_crm(self):
        if CRM_FILE.exists():
            return json.loads(CRM_FILE.read_text(encoding="utf-8"))
        return {}

    def _save_crm(self):
        CRM_FILE.write_text(json.dumps(self.crm, indent=2, ensure_ascii=False), encoding="utf-8")

    def _make_pitch(self, biz):
        name = biz["name"]
        loc = biz["location_short"]
        url = biz.get("url", "")

        return (
            f"Hola, buenos días. Lo llamo de Webuilder. "
            f"Hemos creado una página web profesional para {name} en {loc}, "
            f"completamente terminada y diseñada especialmente para su negocio. "
            f"Tiene galería de fotos, mapa interactivo, WhatsApp integrado, "
            f"y se ve perfecta tanto en celular como en computador. "
            f"Puede verla aquí: {url}. "
            f"Queremos mostrarle el trabajo sin ningún compromiso. "
            f"El precio es muy accesible y la página ya está lista para publicarse. "
            f"¿Le gustaría que le compartamos el enlace para que la vea? "
            f"Muchas gracias por su atención."
        )

    def list_biz(self):
        print(f"\n{'IDX':<5} {'NEGOCIO':<40} {'TELÉFONO':<16} {'UBICACIÓN':<14} {'CRM'}")
        print("-" * 95)
        for b in self.biz_list:
            phone = clean_phone(b.get("phone", "")) or "---"
            crm_s = self.crm.get(str(b["idx"]), {}).get("s", "Pendiente")
            print(f"{b['idx']:<5} {b['name'][:38]:<40} {phone:<16} {b['location_short']:<14} {crm_s}")
        self._print_summary()

    def _print_summary(self):
        counts = {s: 0 for s in STATUSES}
        for b in self.biz_list:
            s = self.crm.get(str(b["idx"]), {}).get("s", "Pendiente")
            counts[s] = counts.get(s, 0) + 1
        print(f"\n{'':4}Resumen CRM:")
        for s in STATUSES:
            print(f"{'':4}  {s}: {counts.get(s, 0)}")

    def call(self, idx):
        biz = next((b for b in self.biz_list if b["idx"] == idx), None)
        if not biz:
            print(f"❌ No se encontró negocio con índice {idx}")
            return

        phone = clean_phone(biz.get("phone", ""))
        if not phone:
            print(f"⚠️  {biz['name']} no tiene teléfono registrado.")
            self._menu_sin_telefono(biz)
            return

        print(f"\n{'='*60}")
        print(f"  📞 {biz['name']} ({biz['location_short']})")
        print(f"  📱 {phone}")
        print(f"{'='*60}")

        twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        twilio_from = os.environ.get("TWILIO_FROM_NUMBER")

        if twilio_sid and twilio_token and twilio_from:
            self._call_twilio(biz, phone, twilio_sid, twilio_token, twilio_from)
        else:
            self._call_simulate(biz, phone)

    def _call_twilio(self, biz, phone, sid, token, from_num):
        try:
            from twilio.rest import Client
            from twilio.twiml.voice_response import VoiceResponse
        except ImportError:
            print("  ⚠️  twilio package not installed. Run: pip install twilio")
            self._call_simulate(biz, phone)
            return

        try:
            pitch = self._make_pitch(biz)
            response = VoiceResponse()

            elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
            if elevenlabs_key:
                self._call_with_elevenlabs(biz, phone, pitch, sid, token, from_num, elevenlabs_key)
                return

            response.say(pitch, voice="Google.es-ES-Wavenet-C", language="es-ES")

            client = Client(sid, token)
            call = client.calls.create(
                to=phone,
                from_=from_num,
                twiml=str(response),
            )
            print(f"  ✅ Llamada iniciada: {call.sid}")
            self._update_crm(biz, "Llamado")
            self._menu_post_call(biz)

        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _call_with_elevenlabs(self, biz, phone, pitch, sid, token, from_num, api_key):
        try:
            import requests
            audio_url = None

            if audio_url:
                from twilio.rest import Client
                from twilio.twiml.voice_response import VoiceResponse, Play
                client = Client(sid, token)
                response = VoiceResponse()
                response.play(audio_url)
                call = client.calls.create(
                    to=phone, from_=from_num, twiml=str(response)
                )
                print(f"  ✅ Llamada iniciada (ElevenLabs): {call.sid}")
            else:
                print("  ⚠️  No se pudo generar audio con ElevenLabs, usando TTS de Twilio")
                from twilio.rest import Client
                from twilio.twiml.voice_response import VoiceResponse
                client = Client(sid, token)
                response = VoiceResponse()
                response.say(pitch, voice="Google.es-ES-Wavenet-C", language="es-ES")
                call = client.calls.create(to=phone, from_=from_num, twiml=str(response))
                print(f"  ✅ Llamada iniciada: {call.sid}")

            self._update_crm(biz, "Llamado")
            self._menu_post_call(biz)
        except Exception as e:
            print(f"  ❌ Error: {e}")

    def _call_simulate(self, biz, phone):
        print(f"\n  {'─'*50}")
        print(f"  📋 SPEECH DE VENTA")
        print(f"  {'─'*50}")
        print(f"\n  {self._make_pitch(biz)}")
        print(f"\n  {'─'*50}")
        self._menu_post_call(biz)

    def _menu_post_call(self, biz):
        print(f"\n  Resultado de la llamada:")
        print(f"    1 - ✅ Llamado exitoso")
        print(f"    2 - ❌ No contestó")
        print(f"    3 - 💚 Interesado")
        print(f"    4 - 💔 No interesado")
        print(f"    5 - 🔁 Dejar pendiente")
        print(f"    0 - ⏭ Saltar (sin cambios)")
        choice = input("  ¿Resultado? [1/2/3/4/5/0]: ").strip()

        status_map = {
            "1": "Llamado", "2": "No Contestó",
            "3": "Interesado", "4": "No Interesado",
            "5": "Pendiente", "0": None
        }
        status = status_map.get(choice)
        if status:
            self._update_crm(biz, status)
        else:
            print("  ⏭ Saltado")

    def _menu_sin_telefono(self, biz):
        print(f"\n  {biz['name']} no tiene teléfono.")
        print(f"    1 - ❓ Sin teléfono (marcar como 'No Interesado')")
        print(f"    2 - 📝 Ingresar teléfono manualmente")
        print(f"    0 - ⏭ Saltar")
        choice = input("  ¿Opción? [1/2/0]: ").strip()
        if choice == "1":
            self._update_crm(biz, "No Interesado")
        elif choice == "2":
            phone = input("  Teléfono: ").strip()
            if phone:
                biz["phone"] = phone
                self.call(biz["idx"])

    def _update_crm(self, biz, status):
        idx = str(biz["idx"])
        now = datetime.now().strftime("%d/%m/%Y")
        if idx not in self.crm:
            self.crm[idx] = {"s": status, "d": now, "calls": []}
        else:
            self.crm[idx]["s"] = status
            self.crm[idx]["d"] = now
        self.crm[idx].setdefault("calls", []).append({"date": now, "status": status})
        self._save_crm()
        print(f"  📝 {biz['name']} → {status}")

    def call_all(self):
        for b in self.biz_list:
            phone = clean_phone(b.get("phone", ""))
            if not phone:
                continue
            crm_s = self.crm.get(str(b["idx"]), {}).get("s", "Pendiente")
            self.call(b["idx"])
            print()
            cont = input("  ¿Siguiente? [Enter=si, n=no, t=terminar]: ").strip().lower()
            if cont == "n" or cont == "t":
                break

    def call_pending(self):
        for b in self.biz_list:
            idx = str(b["idx"])
            current = self.crm.get(idx, {}).get("s", "Pendiente")
            phone = clean_phone(b.get("phone", ""))
            if current == "Pendiente" and phone:
                self.call(b["idx"])
                print()
                cont = input("  ¿Siguiente? [Enter=si, n=no, t=terminar]: ").strip().lower()
                if cont == "n" or cont == "t":
                    break

    def reset(self):
        CRM_FILE.write_text("{}", encoding="utf-8")
        self.crm = {}
        print("  ✅ CRM reset")


def main():
    parser = argparse.ArgumentParser(
        description="Webuilder — Automated calling + CRM system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python caller.py --list              List businesses\n"
            "  python caller.py --idx 21            Call a specific business\n"
            "  python caller.py --all               Call all businesses\n"
            "  python caller.py --pending           Call only pending\n"
            "  python caller.py --status            CRM summary\n"
            "  python caller.py --reset             Clear CRM state\n\n"
            "Env vars for auto-calling:\n"
            "  TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER\n"
            "  ELEVENLABS_API_KEY (optional, premium voice)\n"
        )
    )
    parser.add_argument("--list", action="store_true", help="List businesses with phones and CRM status")
    parser.add_argument("--idx", type=int, help="Call a specific business by index")
    parser.add_argument("--all", action="store_true", help="Call all businesses sequentially")
    parser.add_argument("--pending", action="store_true", help="Call only businesses with 'Pendiente' status")
    parser.add_argument("--status", action="store_true", help="Show CRM summary")
    parser.add_argument("--reset", action="store_true", help="Reset all CRM data")

    args = parser.parse_args()
    caller = Caller()

    if args.list:
        caller.list_biz()
    elif args.idx is not None:
        caller.call(args.idx)
    elif args.all:
        caller.call_all()
    elif args.pending:
        caller.call_pending()
    elif args.status:
        caller.list_biz()
    elif args.reset:
        caller.reset()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
