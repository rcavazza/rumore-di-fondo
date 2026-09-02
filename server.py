"""Server locale di RUMORE DI FONDO — solo libreria standard.

  python server.py            → http://127.0.0.1:7327

Rotte
  GET  /            copertina
  GET  /regole      il regolamento completo
  GET  /nuova       scelta del personaggio
  GET  /plancia     la partita in corso
  GET  /immagini/*  illustrazioni
  GET  /versione    impronta della plancia (per l'aggiornamento automatico)
  POST /inizia      {"pg": "<id>"} → prepara partita.json e costruisce la plancia
  POST /mossa       {"testo": "..."} → accoda la mossa del giocatore su mosse.jsonl
"""

import http.server
import json
import pathlib
import socketserver
import subprocess
import sys
import time

try:  # la console di Windows non parla utf-8 di suo
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent
PORT = 7327
IMMAGINI = ROOT / "immagini"
PLANCIA = ROOT / "plancia.html"
PARTITA = ROOT / "partita.json"
MOSSE = ROOT / "mosse.jsonl"

TIPI = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
        ".webp": "image/webp", ".svg": "image/svg+xml", ".gif": "image/gif"}


def leggi(nome):
    return json.loads((ROOT / nome).read_text(encoding="utf-8"))


def annota(testo):
    riga = {"ora": time.strftime("%H:%M:%S"), "testo": testo}
    with MOSSE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(riga, ensure_ascii=False) + "\n")
    try:
        print("[%s] %s" % (riga["ora"], testo[:140]), flush=True)
    except Exception:
        pass


def stato_partita():
    """Riassunto della partita in corso, o None."""
    if not PARTITA.exists():
        return None
    try:
        p = json.loads(PARTITA.read_text(encoding="utf-8"))
    except Exception:
        return None
    scene = [e for e in p.get("flusso", []) if e.get("t") == "scena"]
    return {
        "pg": p["pg"]["nome"],
        "ruolo": p["pg"]["ruolo"],
        "scena": scene[-1]["n"] if scene else 1,
        "titolo": scene[-1]["titolo"] if scene else "",
        "statica": p.get("statica", 0),
        "allarme": p.get("allarme", 0),
    }


def prepara(pid):
    """Compone partita.json per il personaggio scelto e ricostruisce la plancia."""
    personaggi = leggi("personaggi.json")
    scelto = next((p for p in personaggi if p["id"] == pid), None)
    if scelto is None:
        raise ValueError("personaggio sconosciuto: %r" % pid)

    altri = [p for p in personaggi if p["id"] != pid]
    nomi = {p["nome"].split()[0]: p for p in altri}

    squadra = [{
        "nome": p["nome"],
        "ruolo": p["ruolo"],
        "stato": "ok",
        "dove": p["npc"]["dove"],
        "nota": p["npc"]["nota"],
    } for p in altri]

    apertura = leggi("apertura.json")
    flusso = []
    for e in apertura["flusso"]:
        e = dict(e)
        pref = e.pop("chi_pref", None)
        if e.get("t") == "png" and pref:
            scelta = next((n for n in pref if n in nomi), None)
            if scelta is None:
                scelta = altri[0]["nome"].split()[0]
            e["chi"] = scelta
        flusso.append(e)

    partita = {
        "missione": apertura["missione"],
        "sottotitolo": apertura["sottotitolo"],
        "finestra": apertura["finestra"],
        "finestra_nota": apertura["finestra_nota"],
        "statica": apertura["statica"],
        "allarme": apertura["allarme"],
        "pg": {
            "nome": scelto["nome"],
            "ruolo": scelto["ruolo"],
            "mossa_nome": scelto["mossa_nome"],
            "mossa_testo": scelto["mossa_testo"],
            "mossa_disponibile": True,
            "tratti": scelto["tratti"],
            "attrezzi": scelto["attrezzi"],
            "legame": scelto["legame"],
            "condizioni": [
                {"slot": "Scosso", "tag": None},
                {"slot": "Ferito", "tag": None},
                {"slot": "Compromesso", "tag": None},
                {"slot": "Spento", "tag": None},
            ],
        },
        "squadra": squadra,
        "zone": apertura["zone"],
        "flusso": flusso,
        "turno": apertura["turno"],
    }

    if PARTITA.exists():
        archivio = ROOT / ("partita-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
        archivio.write_text(PARTITA.read_text(encoding="utf-8"), encoding="utf-8")

    PARTITA.write_text(json.dumps(partita, ensure_ascii=False, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "build.py")], cwd=str(ROOT), check=True)
    annota(">> NUOVA PARTITA — il giocatore è %s (%s). Profondo 7, scena 01."
           % (scelto["nome"], scelto["ruolo"]))
    return scelto


class App(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "RumoreDiFondo/1.0"

    # ---------- utilità ----------
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, nome, sostituzioni=None):
        f = ROOT / nome
        if not f.exists():
            return self._send(503, "manca %s" % nome, "text/plain; charset=utf-8")
        testo = f.read_text(encoding="utf-8")
        for k, v in (sostituzioni or {}).items():
            testo = testo.replace(k, v)
        return self._send(200, testo, "text/html; charset=utf-8")

    # ---------- GET ----------
    def do_GET(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"

        if path == "/":
            return self._html("intro.html", {
                "__PARTITA__": json.dumps(stato_partita(), ensure_ascii=False)
            })

        if path == "/regole":
            return self._html("rumore-di-fondo.html")

        if path == "/nuova":
            return self._html("scelta.html", {
                "__PERSONAGGI__": json.dumps(leggi("personaggi.json"), ensure_ascii=False),
                "__PARTITA__": json.dumps(stato_partita(), ensure_ascii=False),
            })

        if path == "/plancia":
            if not PLANCIA.exists():
                self.send_response(302)
                self.send_header("Location", "/nuova")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            return self._send(200, PLANCIA.read_bytes(), "text/html; charset=utf-8")

        if path == "/comune.css":
            return self._send(200, (ROOT / "comune.css").read_bytes(), "text/css; charset=utf-8")

        if path == "/versione":
            v = PLANCIA.stat().st_mtime_ns if PLANCIA.exists() else 0
            return self._send(200, json.dumps({"v": v}))

        if path.startswith("/immagini/"):
            f = (ROOT / path.lstrip("/")).resolve()
            if IMMAGINI not in f.parents or not f.is_file():
                return self._send(404, "{}")
            return self._send(200, f.read_bytes(), TIPI.get(f.suffix.lower(), "application/octet-stream"))

        return self._send(404, "{}")

    # ---------- POST ----------
    def do_POST(self):
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        try:
            n = int(self.headers.get("Content-Length") or 0)
            dati = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._send(400, json.dumps({"ok": False, "err": "corpo illeggibile"}))

        if path == "/mossa":
            testo = (dati.get("testo") or "").strip()
            if not testo:
                return self._send(400, json.dumps({"ok": False, "err": "mossa vuota"}))
            annota(testo[:4000])
            return self._send(200, json.dumps({"ok": True}))

        if path == "/inizia":
            try:
                scelto = prepara(dati.get("pg"))
            except Exception as e:
                return self._send(400, json.dumps({"ok": False, "err": str(e)}))
            return self._send(200, json.dumps({"ok": True, "nome": scelto["nome"]}))

        return self._send(404, "{}")

    def log_message(self, *args):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    MOSSE.touch(exist_ok=True)
    IMMAGINI.mkdir(exist_ok=True)
    with Server(("127.0.0.1", PORT), App) as httpd:
        print("RUMORE DI FONDO — http://127.0.0.1:%d" % PORT, flush=True)
        httpd.serve_forever()
