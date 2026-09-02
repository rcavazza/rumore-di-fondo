import json, pathlib
p = pathlib.Path(__file__).parent
s = json.loads((p/"partita.json").read_text(encoding="utf-8"))
tpl = (p/"plancia.template.html").read_text(encoding="utf-8")
assert "__STATO__" in tpl, "manca il segnaposto __STATO__"
out = tpl.replace("__STATO__", json.dumps(s, ensure_ascii=False))
(p/"plancia.html").write_text(out, encoding="utf-8")
scene = [e for e in s["flusso"] if e["t"] == "scena"]
ind   = [e for e in s["flusso"] if e["t"] == "indizio"]
print("plancia.html %d byte | scena %s | statica %d/6 | allarme %d/4 | %d voci nel flusso | %d indizi"
      % (len(out), scene[-1]["n"] if scene else "-", s["statica"], s["allarme"], len(s["flusso"]), len(ind)))
