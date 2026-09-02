# CRONACA DELLA CAMPAGNA — modello

> 📋 **Questo è il modello, non una campagna.**
> Copialo in `CRONACA.md` e riempilo mentre giochi. La `CRONACA.md` vera non è versionata: è lo stato di una partita, cambia a ogni scena, e appartiene al tuo disco e non alla storia del progetto.
>
> ```bash
> cp CRONACA-esempio.md CRONACA.md
> ```
>
> Le righe fra parentesi quadre sono istruzioni: cancellale man mano.

**Gioco:** *Rumore di Fondo* — recupero industriale a contratto
**Ambientazione:** 2039, Adriatico settentrionale. Un mondo con più rovine che manutentori, e un'industria di gente che ci rientra a pagamento.
**Formato:** un giocatore, GM al tavolo, una missione per sessione.

---

## STATO ATTUALE — *[missione, scena]*

*[Il blocco che il GM rilegge per primo a ogni ripresa. Va tenuto aggiornato a ogni scena chiusa, non a fine sessione: è l'unica parte del documento che deve essere vera adesso.]*

- ➡️ Regole di conduzione in **[TRAMA.md §8](TRAMA.md)**. Sistema in **[REGOLE.md](REGOLE.md)**. Voce in **[STILE.md](STILE.md)** — leggere §1bis e §5 prima di scrivere. Illustrazioni in **[STILE-IMMAGINI.md](STILE-IMMAGINI.md)**.
- **Personaggio:** *[nome, Ruolo]* — scheda in **[PERSONAGGIO.md](PERSONAGGIO.md)**.
- **Luogo:** *[dove sono adesso, in una riga]*
- **Barra di stato:** Statica **0/6** · Allarme **0/4** · Finestra **—** · Condizioni **0/4** · Mossa di Ruolo **pronta** · Legame **non speso**
- **Squadra:** *[chi c'è, e in che stato]*
- **Zone:** *[fatte / corrente / mai viste]*
- **Tiri effettuati:** *[quanti, e com'è andata — serve a capire se il ritmo dei dadi è sano]*
- **Addosso al personaggio, oltre agli attrezzi:** *[cose raccolte in gioco]*
- ⏸️ **Scena aperta:** *[la domanda esatta su cui il giocatore si è fermato. Senza questa riga, riprendere costa dieci minuti.]*

---

## COME SI GIOCA — infrastruttura locale

*[Questa sezione non cambia da una campagna all'altra: si copia com'è. La versione completa sta nel [README](README.md).]*

```bash
python server.py        # → http://127.0.0.1:7327
```

Il GM scrive la scena in `partita.json` → `python build.py` rigenera `plancia.html` → la pagina aperta si aggiorna da sola. Il giocatore scrive nella casella in fondo e preme **Invia al GM**: la mossa finisce in `mosse.jsonl` e `python attesa.py` sveglia il GM.

---

## FATTI ACCERTATI
*(cose che il giocatore ha davvero visto o sentito, non cose che il GM sa)*

*[La distinzione è tutta qui. Quello che sa solo il GM sta in TRAMA.md e non entra in questa lista finché il tavolo non ci arriva. Numerare le voci: si citano per numero quando si scrive una scena nuova.]*

1. *[fatto, in una riga, con i numeri esatti che il giocatore ha sentito]*
2. …

---

## MISTERI APERTI

*[Le domande che il tavolo si è posto ad alta voce e che non hanno ancora risposta. Se una resta ferma per due sessioni, la trama sta girando a vuoto e va spinta: vedi TRAMA.md §8.4.]*

1. *[domanda, formulata come se la ponesse il personaggio]*
2. …

---

## PNG INCONTRATI

| Chi | Dove | Stato |
|---|---|---|
| *[nome — Ruolo]* | *[dov'è adesso]* | *[incolume / ferito / cosa ha appena fatto o ammesso]* |

*[Aggiornare la colonna «Stato» a ogni scena in cui il PNG parla. Un PNG che non cambia mai stato non è un personaggio, è un mobile.]*

---

## REGISTRO EVENTI

### Sessione 1 — *[nome missione]* · in corso

**Scena 01 — [titolo]** *(zona)*
- *[cosa ha fatto il giocatore, e con che esito]*
- *[i tiri: quanti dadi, perché, cosa è uscito — «**2d6 → Rumore**»]*
- *[i movimenti delle tracce, sempre con il prima e il dopo: «**Statica 1 → 2**»]*
- *[gli indizi sbloccati, per numero e titolo]*

**Scena 02 — …**

*[Una riga per beat, non un riassunto narrativo: il testo bello sta già nella plancia. Questo registro serve a ritrovare in fretta quando è successo cosa.]*

---

## STORICO DEI LEGAMI
*(la sequenza dei Legami riscritti è la storia vera del personaggio)*

| Missione | Legame | Esito |
|---|---|---|
| *[missione]* | *[a chi, e la frase]* | *in corso* |

*[Il Legame si riscrive a fine missione — è obbligatorio, vedi REGOLE.md §6. Tenere le versioni vecchie: rilette in fila raccontano il personaggio meglio di qualunque scheda.]*

---

## MISSIONI CHIUSE

*[Per ognuna: cosa è stato portato fuori, cosa è stato lasciato dentro, su cosa si è mentito nel rapporto. Le tre domande dello Sgancio, e la terza è il seme della missione successiva.]*

*(nessuna)*
