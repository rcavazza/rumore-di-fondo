---
name: flux-image
description: Generate images from a text description using FLUX.2 on Cloudflare Workers AI, falling back automatically to a keyless service when credentials are absent, then save them to disk and show them inline in the chat as downloadable files. Use this skill whenever the user asks to create, generate, draw, illustrate, or visualize an image, picture, illustration, logo, icon, poster, cover, mockup, avatar, or artwork — including when they just describe something visual and say "make me one" without naming a tool, ask for variants of an image, or want an image for a document, slide deck, or website they're working on. Also use it for image-to-image edits from a source image URL.
---

# Generating images

Two backends, same output contract — each script prints one JSON line per image with a `path`, so
everything downstream is identical regardless of which one ran.

| | `scripts/cloudflare.py` | `scripts/generate.py` |
|---|---|---|
| Service | Cloudflare Workers AI | Pollinations |
| Models | FLUX.2 klein, FLUX.1 schnell, SDXL, Leonardo | `sana` only |
| Setup | two env vars | none at all |
| Quality | good to excellent | rough |
| Size | true 1024×1024 | silently downscales to 768 |
| Speed | 5–30 s | 5 s, then 30–45 s once queued |

**Always run `cloudflare.py`.** There is nothing to decide and nothing to check first: it uses
Cloudflare when the two environment variables are present and silently re-runs `generate.py` when
they aren't, printing a `"backend": "pollinations"` line so you know which one produced the files.
Never invoke `generate.py` directly — going through `cloudflare.py` is what makes the good path the
default.

The quality gap is why it's ordered that way: on an identical prompt, FLUX.2 klein produced
recognisable scoops of gelato melting onto a plate, while Pollinations' `sana` produced a smooth pink
blob. If you see the fallback line, mention once that setting the two variables would give much
better results, then carry on with the image you have.

The job isn't finished when the file lands on disk. The user asked to *see* the image, so the
final step is always to surface it in the chat.

## Workflow

**1. Write the prompt in English, and make it specific.**

This matters more than any parameter. The model follows English reliably and drifts on other
languages — a verified example: `"un gatto rosso astronauta, stile acquerello"` came back as a
glossy photorealistic render, while `"watercolor painting of a red cat astronaut, loose brush
strokes, paper texture"` came back as an actual watercolor. Same model, same seed range.

So when the user writes in another language, translate their idea into English and expand it with
the concrete visual detail they implied: medium (photo, oil painting, 3D render, line art),
lighting, composition, mood, color palette. Keep their intent — you're adding specificity, not
inventing a different picture. Their words still name the file, so they can find it later.

**Anchor objects as objects.** Pollinations' `sana` leans hard toward anime character art, and it
will hijack a request the moment the wording gives it an opening. A real failure:
"a cat made of ice cream… waffle cone texture on the ears, pastel background" produced a pink-haired
anime catgirl. The phrase `cat ears` is an overwhelming character trope in the training data, and
`pastel` plus `soft light` finished the job.

The fix is context, not negation — the model largely ignores "no people" and "not anime", but it
follows the world you put the subject in. Name the object category and the setting: *dessert still
life*, *on a white ceramic plate*, *food photography*, *product shot on a marble counter*. Rewriting
the same request as "dessert still life photograph of a sculpture of a sitting cat carved out of ice
cream, melting onto a plate" produced exactly the intended thing. Watch for this whenever the
subject is an object shaped like a creature, a mascot, a toy, or a figurine.

The anime pull is much weaker on FLUX.2, but the underlying habit — reading a described object as a
stylised character — shows up on every model, so the object-anchoring is worth doing regardless of
which backend runs.

**2. Run the generator.**

One command, every time:

```bash
python ".claude/skills/flux-image/scripts/cloudflare.py" "your english prompt"
```

That's the whole invocation for a normal request — `flux2-klein-4b` at 1024×1024 is already the
default, so don't pass `--model` unless you have a reason from the table below. Files land in
`~/Pictures/cloudflare-ai/` (or `~/Pictures/pollinations/` on the fallback); pass `--out` to redirect
them when the image belongs to a project the user is building.

Output is one JSON line per image with the saved `path`.

Give the command a generous timeout — **300000 ms or more**. Cloudflare answers in 5–30 s, but the
fallback throttles anonymous traffic by holding the connection open instead of returning an error, so
its first image lands in about 5 seconds and each queued one takes 30–45. That slowness is the
service working normally, not a hang, and killing the command early is the main way this fails.

**Budget the Cloudflare free tier: 10,000 neurons/day, and the models differ enormously.**

| Model | Cost at 1024² | Images/day | Use it for |
|---|---|---|---|
| **`flux2-klein-4b`** (default) | 104 neurons | **~95** | everything, unless told otherwise |
| `phoenix` | ~2160 neurons | **~4** | the final render — best quality measured so far |
| `flux2-klein-9b` | 1364 neurons | **~7** | final render when Phoenix misreads the subject |
| `flux-schnell` | 58 neurons | ~173 | only if 4B is exhausted; no seed control |
| `lucid-origin` | ~2590 neurons | **~3** | rarely worth it; matches 4B at 25× the cost |
| `sdxl`, `sdxl-lightning`, `dreamshaper` | not in the pricing table | ? | skip — weakest results of the set |

**Stay on the default.** A handful of images a day is not a budget anyone can work inside, and one
careless `--model phoenix` on a first draft burns a quarter of the day. Switch only when the user has
seen a 4B result, approved the direction, and wants the good version — say what you're spending when
you do, and go straight back to 4B afterwards.

On one controlled test (an ice-cream cat sculpture, identical prompt across all of them), Leonardo
Phoenix produced the only complete, coherent subject — full body, correct textures, garnish — while
the cheaper models managed a plausible bust. `flux2-dev` is available but untested. SDXL Lightning
was clearly the weakest of the paid-tier models, worse than FLUX.1 schnell at no saving.

A trap worth knowing: 9B bills a flat 1363.64 neurons for the *first megapixel*, so a 512×512 costs
exactly as much as a 1024×1024. Never generate small on 9B — it wastes three quarters of the charge.
4B bills per 512² tile and does scale down, giving ~383 images/day at 512×512.

These are computed from the published rates, not measured. The authoritative figure is the
dashboard under Workers AI → Usage; if the two disagree, the dashboard wins.

**3. Look at what came back, then show it.**

`Read` the files before sending them. This is cheap and it is the difference between handing over a
picture and handing over a surprise — the catgirl above went out to the user unseen, and they had to
be the one to point out that it wasn't a cat made of ice cream. You wrote the prompt, so you're the
one who can tell at a glance whether the image answers it.

If it clearly missed, say so and regenerate before sending rather than shipping it with an apology
attached. If it's merely imperfect, send it and name the flaw yourself in the caption — users are
fine with a rough draft and much less fine with being told something is great when it isn't.

Then send every path in a single `SendUserFile` call with `display: "render"` — that puts the image
inline where the user can see it and gives them a download card. Caption it with what varies between
the images (seed, style, variant) so they can tell you which one to iterate on.

Then mention the folder they're saved in, once. Don't paste the raw URLs — they're long, and the
user already has the file.

## Cloudflare options (`cloudflare.py`)

`--model` takes an alias: `flux2-klein-4b`, `flux2-klein-9b`, `flux2-dev`, `flux-schnell`,
`lucid-origin`, `phoenix`, `sdxl`, `sdxl-lightning`, `dreamshaper` — or a full `@cf/...` path.
`--list-models` asks the account what it can actually run, which beats trusting any list. Two
inpainting/img2img models (`@cf/runwayml/stable-diffusion-v1-5-*`) also show up there; they need a
source image and aren't wired into this script.

Also: `--n` (variants), `--steps`, `--width`/`--height`, `--seed`, `--out`.

**Two API quirks, both found the hard way — the published docs are wrong about them.**

FLUX.2 models reject JSON bodies outright and require `multipart/form-data`; a JSON request returns
`400 required properties at '/' are 'multipart'`. FLUX.1 schnell is the opposite — it takes JSON but
400s on *any* field beyond `prompt` and `steps`, including `seed`, even though the docs advertise
seed support. The script already encodes each model correctly and strips unsupported fields, so this
only matters if you add a model: pass `--encoding multipart` if it rejects JSON, and expect to probe
its accepted fields rather than trusting the docs page.

Practical consequence: **you cannot pin a seed on flux-schnell**, so it can't do the
hold-the-composition-and-change-one-thing trick below. Use a FLUX.2 model when the user wants a
controlled variation.

Multiple prompts in one call each produce `--n` images:

```bash
python ".../cloudflare.py" "a red fox in snow, golden hour" "a red fox in snow, blue twilight" --n 2
```

## The fallback backend (`generate.py`)

You should never run this directly — `cloudflare.py` delegates to it. It's documented here only so
its extra flags are findable when the fallback is the one running: `--image URL` for image-to-image,
`--enhance` to let the service rewrite a vague prompt, `--private` to keep a personal subject off the
public feed, `--logo` to keep the watermark (`--nologo` is already default). It shares `--n`,
`--width`/`--height`, `--seed` and `--out` with the Cloudflare script.

Its one real trap: requested sizes are advisory. Ask for 1024×1024 and you'll usually get 768×768.
The script reports what actually arrived and adds a `note` when they differ, so quote the delivered
size rather than the one you asked for.

## Iterating

Users rarely love the first image. When they ask for a change, decide what kind it is:

- **Small adjustment** ("same but warmer", "less busy") — reuse the seed from the JSON output and
  edit the prompt. Holding the seed keeps the composition and changes only what you described.
- **Different idea** — drop the seed and let it randomize. Reusing a seed here just anchors you to
  a layout the user didn't like.
- **"Show me some options"** — one prompt with `--n 3`, or two or three prompt variants at `--n 1`.
  Cheap on `flux2-klein-4b`; on Pollinations warn them it'll take a minute or two, and on
  `flux2-klein-9b` don't do it at all — three variants is nearly half the day's budget.

Pay extra attention when reviewing images that involve text, a specific number of things, or hands —
the model garbles all three routinely, and those are the failures users notice immediately.

## Credentials

`cloudflare.py` reads `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` from the environment and
never writes either one — persisting a token is the user's call, not something to do on their behalf.
Both must be present in the environment; the repository README explains how to set them.

If the fallback line appears, the token isn't in the environment. Give the user this to run once,
rather than exporting it yourself in a shell that dies with the command:

```bash
setx CLOUDFLARE_API_TOKEN "their-token"
```

`setx` only affects new processes, so the current session still needs an `export` to work right away.

A token scoped to Workers AI alone cannot read the account id (`/accounts` returns empty, `/user`
returns `9109`), so there's no way to discover it from the token — ask the user for it. The same
scoping means neuron usage isn't readable either; point them at the dashboard instead of guessing.

## When it fails

A line with `"ok": false` carries an `error`.

Cloudflare:
- **`400 ... 'multipart'`** or **`Additional or unevaluated properties`** — wrong encoding or an
  unsupported field for that model. See the quirks above; this is a code fix, not a retry.
- **`HTTP 429` / neuron exhaustion** — the daily free tier is spent. Say so and offer either
  `flux2-klein-4b` (13× cheaper than 9B) or the Pollinations fallback, rather than silently
  switching models on the user.
- **`HTTP 401/403`** — the token lacks the Workers AI permission or has been revoked.

Pollinations:
- **Timeout or connection reset** — the queue was long. The script already retries with backoff;
  running it again usually works.
- **Non-image response** — the service returned an error page. Almost always transient; retry once,
  and if it persists check `https://image.pollinations.ai/prompt/test` directly.

If every image failed, the script exits non-zero. Say so plainly rather than reporting partial
success. Don't silently retry more than once or twice — each attempt can cost 30+ seconds, and
telling the user the service is struggling is more useful than a long quiet stall.
