# STILE VISIVO DELLA CAMPAGNA
*Da usare identico su ogni immagine generata, per coerenza tra le scene.*

> 🔁 **ORDINE PERMANENTE — non va ricordato dal giocatore.**
> **Un'immagine per ogni scelta del giocatore.** Ogni volta che arriva una mossa dalla plancia, il GM genera l'illustrazione di quel momento *prima* di pubblicare la scena, e la scena esce già completa. Una sola immagine per mossa: il flusso è un diario illustrato, non una galleria.
> Il giocatore aspetta 15–30 secondi in più a turno. È un prezzo accettabile e non va scaricato su di lui: mai pubblicare il testo e aggiungere l'immagine dopo, perché la pagina si ricarica e gli strappa la lettura di mano.
> Restano utili anche le immagini d'ambiente generate in anticipo per le zone non ancora visitate: quelle si preparano quando c'è tempo morto.

**Cartella immagini:** `C:\Users\ricca\RumoreDiFondo\immagini\`
**Come entrano in gioco:** una voce nel flusso di `partita.json`, poi `python build.py`.
```json
{ "t": "img",
  "file": "immagini/s03-corpi.jpg",
  "alt":  "Portello interno chiuso in un corridoio annerito dal fuoco, acqua bassa sul pavimento.",
  "dida": "Il portello interno del Ponte B. Tutti dalla stessa parte." }
```
Il server le serve da `/immagini/*`.

⚠️ **`alt` e `dida` non devono mai avere lo stesso testo.** L'`alt` descrive in piano quello che si vede, per chi non vede l'immagine e per chi copia la pagina; la `dida` è testo di gioco e si scrive con la voce di [STILE.md](STILE.md). Riempirli con la stessa frase la fa comparire due volte in ogni copia-incolla della partita.

---

## Suffisso di stile (da appendere SEMPRE, in inglese)

```
grainy underexposed documentary night photograph, 1990s reportage film stock, heavy film grain, one harsh work-light as the only source, deep petrol-green and black palette with a single rust-orange accent, wet steel, rust streaks, riveted industrial surfaces, cold and unromantic composition, no text, no lettering, no signage
```

---

## Regole

- Prompt **sempre in inglese**, molto specifici: soggetto, luce, materiale, composizione.
- **Fotografia, mai illustrazione.** Questo gioco non è dipinto: è documentato. Ogni prompt deve contenere *photograph* e un riferimento a pellicola/grana.
- ⚠️ **Mai chiedere scritte.** Il modello produce lettere finte e illeggibili: la prima versione del portello di Z1 è tornata con `PEICNB` stampigliato sopra. Scrivere sempre `completely blank paint, no writing, no letters, no numbers, no signage`. Le scritte del mondo (MAREA, i cartellini) **si dicono nel testo**, non si mostrano.
- ⚠️ **I corpi non si illustrano mai.** Vale la tecnica ⑦ di STILE.md: si illustra **l'oggetto accanto**. Un morto sulla passerella diventa la linguetta d'armamento mai tirata sul petto della tuta.
- **Le persone vive si possono mostrare, ma di spalle e senza volto.** Cappucci alzati, controluce, inquadratura da dietro o dal basso: `seen from behind, hoods up, faces not visible`. Un ritratto frontale rompe la serie e trasforma il diario in un fotoromanzo. Per le immagini di solo ambiente resta `no people`.
- **Ogni immagine illustra un momento, non una zona.** Se la mossa è un gesto — una mano su un quadro, una chiave che esce da un imbrago — l'inquadratura è stretta. Le vedute d'insieme si usano per le aperture di scena.
- **Ancorare i soggetti come oggetti e ambienti**, mai come «personaggio suggestivo»: il modello deriva verso il ritratto posato se gli si lascia spazio.
- **Arancio ossido** = l'unica luce accesa, il pericolo, la vita. Usarlo **una volta sola per immagine**. **Verde petrolio** = tutto il resto. Il bianco freddo è ammesso solo per le lampade da lavoro.
- ⚠️ **Mai cielo, mai alba, mai orizzonte illuminato.** È notte, c'è una tempesta, e la piattaforma è nera. Se serve profondità, usare pioggia e riflessi sul grigliato.
- Formato **scena: 1024×640**. Formato **ritratto: 640×800**.
- Un **HTTP 400 «Your output has been flagged»** non è un errore di rete: è il filtro. Succede su descrizioni di corpo e abbigliamento (`dry-suit unzipped` è bastato). Riformulare vestendo del tutto il soggetto o cambiando inquadratura; non insistere due volte con lo stesso testo.

---

## Generatore

Si usa la skill **`/flux-image`**, sempre tramite `scripts/cloudflare.py` (mai `generate.py` diretto).
Modello di default `flux2-klein-4b` a 1024px: ~95 immagini al giorno di quota gratuita. Non passare `--model` senza motivo: `phoenix` e `flux2-klein-9b` costano 10–20× e bruciano la giornata in 3–4 immagini.

```bash
python "C:/Users/ricca/.claude/skills/flux-image/scripts/cloudflare.py" "<prompt in inglese>" \
  --width 1024 --height 640 --out "C:/Users/ricca/RumoreDiFondo/immagini"
```

Lo script stampa una riga JSON con `path`: rinominare subito il file in `sNN-soggetto.jpg`, altrimenti la cartella diventa illeggibile.

Se compare la riga `"backend": "pollinations"`, le credenziali Cloudflare non sono state caricate e la qualità crolla. In questa sessione erano già nell'ambiente e non è servito caricarle.

---

## Flusso di lavoro

**Una mossa, un'immagine, in questo ordine:** arriva la mossa → si sceglie l'inquadratura → si genera → si scrive la scena in `partita.json` con la voce `img` al punto giusto → `python build.py`. La scena arriva al giocatore già illustrata, in un colpo solo.

**Niente batch di fine sessione.** Producono immagini che non c'entrano più con quello che è successo davvero. L'unica generazione anticipata ammessa è l'ambiente di una zona non ancora visitata, e si fa nei tempi morti.

**Sempre guardare il file prima di metterlo in gioco.** Le due cose che il modello sbaglia sistematicamente e che il giocatore nota subito: le scritte e il numero di oggetti.

---

## Inventario

| File | Soggetto | Uso |
|---|---|---|
| `profondo-7.jpg` | La piattaforma di notte, dal mare, con una sola finestra accesa | Copertina, `/` |
| `s01-portello.jpg` | Il portello rosso chiuso, lampada da lavoro, grigliato, pioggia | Scena 01 |
| `pg-tecnico.jpg` | Iolanda Cerf | Carta personaggio |
| `pg-cane.jpg` | Renzo Bosco | Carta personaggio |
| `pg-palombaro.jpg` | Tarik Muzaffer | Carta personaggio |
| `pg-fissatore.jpg` | Nadia Sartori | Carta personaggio |
| `pg-medico.jpg` | Ada Piras | Carta personaggio |
| `s01b-squadra.jpg` | I quattro sulla passerella, di spalle sotto la lampada | Scena 01 · «la squadra» |
| `s01c-trasmettitore.jpg` | Il petto della tuta arancione, linguetta d'armamento intatta | Scena 01 · «esamino il corpo» |
| `s02-alloggi.jpg` | Le quattro cuccette, la linea nel soffitto, il foglio dei turni | Z2, pronta in anticipo |

---

## PROMPT CANONICO — le zone di Profondo 7
*Ogni scena futura parte da questi blocchi: si cambia inquadratura e dettaglio, mai la luce e mai la palette.*

**Z1 · Ponte alto** — *approvato, in gioco*
> Night photograph of a heavy sealed steel bulkhead door on the exterior walkway of an offshore platform, painted deep red, **completely blank paint with absolutely no writing no letters no numbers no signage**, wet with rain, rust streaks bleeding down, a large mechanical deadbolt lever in the locked-down position, riveted frame, steel handrail and grating around it, harsh raking work-light from one side, deep petrol-green blackness beyond, heavy film grain, documentary night photography, no people

**Z2 · Alloggi** — *generata, in attesa*
> Cramped offshore platform bunk room at night, four narrow steel bunks, three unmade and one made with military precision, personal objects on a shelf, a shift rota sheet pinned to the bulkhead, one dim ceiling lamp, exposed ammonia pipework running along the ceiling, deep petrol-green shadows, one rust-orange indicator glow, heavy film grain, no people, no readable text

**Z3 · Ponte B** — *da generare*
> Burned-out lower deck of an offshore platform, blackened battery racks, melted cable insulation hanging in strands, ankle-deep black water reflecting a single torch beam, an internal bulkhead door shut tight, soot on every surface, absolute darkness beyond the beam, heavy film grain, no people, no text

**Z4 · Sala controllo** — *da generare*
> Small offshore platform control room at night, the only lit room in a dead structure, banks of old monitors with one screen still on, warm amber light, empty operator chair pushed back, four water bottles lined up on the desk, cold petrol-green darkness in the corridor beyond the doorway, heavy film grain, no people, no readable text

**Note apprese generando:**
- Chiedere esplicitamente `no writing / no letters / no numbers / no signage` è l'unico modo per non ricevere stencil finti. Dirlo una volta sola non basta: va ripetuto in tre forme.
- I ritratti reggono meglio con **una sola fonte di luce nominata** e un ambiente stretto. Senza ambiente, il modello produce fondi neutri da studio che rompono la serie.
- La palette regge da sola se si nominano *petrol-green* e *rust-orange* **insieme**: nominarne una sola porta a un'immagine monocroma.
