# RUMORE DI FONDO

**Un gioco di ruolo di recupero industriale. 2039, Adriatico settentrionale.**

![Profondo 7 di notte durante la tempesta: la sagoma nera della piattaforma sulle gambe, mare grosso, e una sola finestra illuminata di arancione appena sopra la linea di galleggiamento.](immagini/profondo-7.jpg)

Nel 2039 non è finito niente. È stato costruito più di quanto si riesca a tenere acceso: piattaforme, depositi, data center sommersi, capannoni pieni di batterie — chiusi, sigillati, assicurati, dimenticati.

Tu sei un **Corvo**: uno che entra. Ti assumono assicuratori, tribunali e aziende che non vogliono comparire. Ti pagano alla consegna. Nessuno viene a prenderti se resti dentro.

La prima missione è **Profondo 7**: un caveau di dati raffreddato ad acqua di mare, quaranta miglia al largo di Ravenna, che ha smesso di rispondere trentuno ore fa. Quattro custodi a bordo. Il portello è chiuso dall'interno.

Niente di soprannaturale, mai. Ogni cosa strana ha una spiegazione tecnica o umana, e alla fine arriva.

---

## Il sistema, in trenta secondi

Si tira una manciata di **d6** e **si legge solo il dado più alto**.

| Dado più alto | Esito | |
|---|---|---|
| **6** | **Pulito** | Funziona come volevi. Nessun costo. |
| **4–5** | **Sporco** | Funziona, ma c'è un prezzo. |
| **1–3** | **Rumore** | Non funziona. Statica +1, e il posto reagisce. |
| **6 6** | **Limpido** | Funziona, e ti resta in mano un vantaggio. |

Base 1d6, più un dado per ognuna di queste cose: il tuo **Ruolo** c'entra, hai l'**Attrezzo** giusto, hai un **Vantaggio** concreto. Massimo quattro. Puoi **Forzare** per un quinto, e lo paga il gruppo.

Due tracce al centro del tavolo. La **Statica** (0–6) è il volume che stai facendo, e il GM la *spende* per farti male — spendendola la abbassa, quindi il ritmo pompa invece di stringere. L'**Allarme** (0–4) è l'ora: non scende mai, e ogni tacca cambia il posto in modo irreversibile.

Niente punti ferita: quattro **Condizioni**, e ogni volta che arriva addosso una conseguenza la stessa domanda — la paghi tu con il corpo, o la paga la squadra con un punto di Statica?

Il regolamento completo, che si legge in cinque minuti, sta in **[REGOLE.md](REGOLE.md)**.

---

## Due modi di usarlo

**Al tavolo, con delle persone.** Servono quattro o cinque d6, due file di caselle su un foglio e un timer da dieci minuti. Il regolamento e la missione bastano: `rumore-di-fondo.html` è il manuale in una pagina sola, apribile con un doppio clic.

**Da soli, con un GM che scrive.** L'applicazione in questa cartella regge una partita in solitaria in cui il game master è una sessione di Claude Code: il giocatore legge le scene sulla plancia nel browser e ci scrive dentro le proprie mosse.

---

## Setup

Serve **Python 3.8 o superiore**. Niente altro: il server usa solo la libreria standard, nessuna dipendenza da installare.

```bash
python server.py
```

Poi apri **http://127.0.0.1:7327**.

| Pagina | Cosa c'è |
|---|---|
| `/` | Copertina, e il tasto per riprendere la partita in corso |
| `/regole` | Il regolamento completo, da leggere |
| `/nuova` | Scelta fra i cinque Corvi, con i ritratti |
| `/plancia` | Il gioco |

Da `/nuova` scegli un personaggio e la partita comincia: il server prepara `partita.json`, costruisce la plancia e ti manda dentro.

---

## Come funziona una sessione in solitaria

Il giro è questo, e si ripete a ogni mossa:

1. Il giocatore legge la scena sulla plancia, scrive cosa fa nella casella in fondo e preme **Invia al GM** *(anche Ctrl+Invio)*.
2. La mossa finisce in `mosse.jsonl`. **`python attesa.py`** è in ascolto e si sblocca: è quello che sveglia il GM.
3. Il GM tira i dadi, aggiorna le tracce, genera l'illustrazione del momento e scrive la scena nel flusso di `partita.json`.
4. **`python build.py`** rigenera `plancia.html`.
5. La pagina aperta se ne accorge da sola — controlla `/versione` ogni secondo e mezzo — e si ricarica. Se stavi scrivendo, non ti strappa il testo di mano: aspetta e ti offre un tasto.

Due terminali, quindi: uno per `server.py`, uno per `attesa.py` fra una mossa e l'altra.

---

## Cosa c'è nella plancia

- **Il flusso** — narrazione, dialoghi dei PNG, le tue azioni, i tiri con i dadi disegnati, gli eventi delle tracce, gli indizi e le illustrazioni, tutto in ordine cronologico. È il diario della partita e resta leggibile fino in fondo.
- **Tocca a te** — in coda al flusso, sempre: la domanda aperta e le strade possibili, ognuna **con i dadi già dichiarati**. Prima di ogni tiro sai quanti dadi hai e perché, così Forzare è una scelta e non una sorpresa.
- **La barra** — Statica e Allarme a caselle, e la finestra meteo che si accorcia.
- **La scheda** — Ruolo, mossa, tratti, attrezzi (con quelli persi barrati), Condizioni, Legame.
- **La squadra** — i quattro PNG, dove sono e cosa hanno appena fatto.
- **La piattaforma** — le zone, che si scoprono man mano.
- **Gli indizi** — quello che hai scoperto, raccolto in un posto solo.
- **Dadi, timer della Chiusura e taccuino** — locali, restano su quel browser.

---

## I file

| File | Cosa |
|---|---|
| `REGOLE.md` | Il sistema completo |
| `TRAMA.md` | ⚠️ **Bibbia della missione: contiene tutte le risposte.** Non aprire se giochi |
| `STILE.md` | Voce, tono e lessico: si legge prima di scrivere narrazione |
| `STILE-IMMAGINI.md` | Stile visivo, prompt canonici, come entrano in gioco le illustrazioni |
| `PERSONAGGIO.md` | La scheda estesa del personaggio giocante |
| `CRONACA-esempio.md` | Modello della cronaca di campagna, da copiare in `CRONACA.md` |
| `server.py` | Il server locale: pagine, mosse, avvio partita |
| `build.py` | Inietta lo stato nel template e scrive `plancia.html` |
| `attesa.py` | Blocca finché non arriva una mossa, poi la stampa |
| `plancia.template.html` | Il modello della plancia, con `__STATO__` al posto dei dati |
| `apertura.json` | La scena 01, indipendente dal personaggio scelto |
| `personaggi.json` | I cinque Corvi, sia come giocanti sia come PNG |
| `tira.ps1` | Tiratore da riga di comando (PowerShell), tiene anche le tracce |
| `immagini/` | Ritratti, copertina, illustrazioni delle scene |

**Non versionati**, perché sono appunti di lavoro o lo stato di una partita e non il gioco: `CRONACA.md`, `PIANO-ONLINE.md`, `partita.json`, `mosse.jsonl`, `tracce.json`, e `plancia.html` che si rigenera.

---

## Il tiratore da riga di comando

Alternativa ai dadi della plancia, utile se giochi al tavolo. Applica le regole alla lettera e tiene Statica e Allarme in `tracce.json`.

```bash
./tira.ps1 -Ruolo -Attrezzo -Etichetta "Aprire il quadro del portello"
./tira.ps1 -Ruolo -Attrezzo -Vantaggio -Forza
./tira.ps1 -Spendi 2     # il GM spende Statica
./tira.ps1 -Statica      # mostra le tracce
./tira.ps1 -Azzera
```

⚠️ Le tracce del tiratore e quelle della plancia **sono due contatori distinti** e non si sincronizzano. Usa l'uno o l'altra, non entrambi nella stessa partita.

---

## Avvertenze sui contenuti

Morti sul lavoro, corpi, annegamento, spazi chiusi e sommersi, colpa e responsabilità. Nessuna violenza descritta esplicitamente — il gioco guarda sempre l'oggetto accanto — ma il tema è gente che muore perché qualcuno ha fatto la scelta più comoda.

---

## Licenza

Non ancora scelta.

Da chiarire prima di qualunque pubblicazione: i diritti sulle illustrazioni, che sono generate da un modello, dipendono dai termini del servizio usato per produrle.
