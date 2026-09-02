"""Blocca finche' il giocatore non invia una mossa dalla plancia, poi la stampa ed esce.

  python attesa.py [minuti_max]

Serve al GM per essere svegliato dal browser: si mette in ascolto su
mosse.jsonl e termina appena compare una riga nuova rispetto a quando e'
partito.
"""

import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent
MOSSE = ROOT / "mosse.jsonl"
MAX_MIN = float(sys.argv[1]) if len(sys.argv) > 1 else 45.0


def righe():
    if not MOSSE.exists():
        return []
    return [r for r in MOSSE.read_text(encoding="utf-8").splitlines() if r.strip()]


base = len(righe())
scadenza = time.time() + MAX_MIN * 60
print("in ascolto - %d mosse gia' registrate" % base, flush=True)

while time.time() < scadenza:
    ora = righe()
    if len(ora) > base:
        for r in ora[base:]:
            try:
                m = json.loads(r)
                print("MOSSA %s :: %s" % (m.get("ora", "--:--:--"), m.get("testo", "")), flush=True)
            except Exception:
                print("MOSSA (illeggibile) :: " + r, flush=True)
        sys.exit(0)
    time.sleep(1.0)

print("nessuna mossa entro %g minuti" % MAX_MIN, flush=True)
sys.exit(0)
