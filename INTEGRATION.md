# Lightning — Unified Aesthetic Integration Guide

This package gives you (1) a single drop-in `style.css` that unifies every
page, (2) a new **How to Use / API** page, and (3) a rebuilt **Presentation**
with the four judging criteria woven through as recurring narrative beats.

## What's in the package

```
lightning_unified/
├── INTEGRATION.md                  ← this file
├── static/
│   ├── css/style.css               REPLACES demos/static/css/style.css
│   └── js/
│       ├── how_to_use.js           NEW   demos/static/js/how_to_use.js
│       └── presentation.js         REPLACES demos/static/js/presentation.js
├── templates/
│   ├── _partials/
│   │   ├── head.html               NEW   demos/templates/_partials/head.html
│   │   └── navbar.html             NEW   demos/templates/_partials/navbar.html
│   ├── how_to_use.html             NEW   demos/templates/how_to_use.html
│   └── presentation.html           REPLACES demos/templates/presentation.html
└── patches/
    └── fastapi_app.patch.py        Manual patch for demos/fastapi_app.py
```

## Step 1 — Drop in the static files (1 minute)

```bash
# from your repo root
cp lightning_unified/static/css/style.css           demos/static/css/style.css
cp lightning_unified/static/js/how_to_use.js        demos/static/js/how_to_use.js
cp lightning_unified/static/js/presentation.js      demos/static/js/presentation.js
```

That overwrites the existing `style.css`. Every page that links to it (which
is all of them) immediately picks up the unified design system. The old
in-template `<style>` blocks become harmless — overridden by the new tokens.

## Step 2 — Drop in the templates and partials (1 minute)

```bash
mkdir -p demos/templates/_partials
cp lightning_unified/templates/_partials/head.html    demos/templates/_partials/head.html
cp lightning_unified/templates/_partials/navbar.html  demos/templates/_partials/navbar.html
cp lightning_unified/templates/how_to_use.html        demos/templates/how_to_use.html
cp lightning_unified/templates/presentation.html      demos/templates/presentation.html
```

## Step 3 — Wire up the navbar in your existing 6 templates (5 minutes)

For each of these:

- `demos/templates/index.html`
- `demos/templates/adversarial.html`
- `demos/templates/audit.html`
- `demos/templates/visualization.html`
- `demos/templates/agent_explorer.html`
- `demos/templates/admin.html`

Find the existing `<head>` section and replace its contents with:

```jinja
<head>
{% include "_partials/head.html" %}
</head>
```

Then find the existing `<nav>...</nav>` block (or whatever serves as the page's
top navbar — likely a Bootstrap `<nav class="navbar...">`) and replace the entire
block with:

```jinja
{% include "_partials/navbar.html" %}
```

That's it for the templates. Everything else — your existing markup, your
existing IDs, your existing JavaScript — keeps working. The new `style.css`
overrides Bootstrap's colors and your old class names map to the new tokens
through backwards-compat aliases in the CSS.

## Step 4 — Pass `active` and `page_title` from each route (3 minutes)

Open `demos/fastapi_app.py` and update each `templates.TemplateResponse(...)`
call so the navbar can highlight the current page. Example:

```python
# Before
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

# After
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request, "index.html",
        {"page_title": "Demo", "active": "main"},
    )
```

The `active` value should match the navbar partial's branches:

| Page                | active value      |
| ------------------- | ----------------- |
| `/`                 | `main`            |
| `/adversarial`      | `adversarial`     |
| `/audit`            | `audit`           |
| `/visualization`    | `visualization`   |
| `/agent-explorer`   | `agent_explorer`  |
| `/admin`            | `admin`           |
| `/how-to-use`       | `how_to_use`      |
| `/presentation`     | `presentation`    |

`patches/fastapi_app.patch.py` has the exact snippets to copy.

## Step 5 — Add the `/how-to-use` route (1 minute)

In `demos/fastapi_app.py`, add:

```python
@app.get("/how-to-use", response_class=HTMLResponse)
async def how_to_use(request: Request):
    return templates.TemplateResponse(
        request, "how_to_use.html",
        {"page_title": "How to Use", "active": "how_to_use"},
    )
```

## Step 6 — Make sure `POST /api/analyze` returns the right shape (5 minutes)

Both the How-to-Use playground and the presentation's slide-4 demo POST to
`/api/analyze`. They expect this response shape:

```json
{
  "decision":   "REFUSE",
  "confidence": 0.97,
  "rationale":  "...",
  "citations":  [{ "authority": "ITAR", "section": "22 CFR 121.1 IV(h)(1)", "text": "..." }],
  "proof":      { "steps": ["fact(...).", "rule(...) :- ..."], "regime": "usml" },
  "regimes":    ["usml", "mtcr"]
}
```

If your existing `/api/analyze` returns a different shape, adapt it — see
`patches/fastapi_app.patch.py` for a reference implementation that wraps
your real `lightning.check()` call.

If `/api/analyze` is not yet implemented, the presentation's slide 4
gracefully falls back to a deterministic mock so the live demo is never
the thing that crashes in front of a panel.

## Step 7 — Restart and verify (1 minute)

```bash
uv run python demos/fastapi_app.py
```

Walk the eight pages:

1. **`/`** — primary 3-pane demo, new aesthetic
2. **`/adversarial`** — adversarial bench
3. **`/audit`** — audit ledger
4. **`/visualization`** — proof tree forensics
5. **`/agent-explorer`** — agent explorer
6. **`/admin`** — admin console (already in unified style)
7. **`/how-to-use`** — NEW: API docs + live playground
8. **`/presentation`** — REBUILT: 7 slides, criteria rail at top

The navbar and the cyan-accent / dark-navy aesthetic should be identical on every page.

---

## Design tokens, for reference

If you ever want to tweak: every color is a CSS custom property in `style.css`.
Top of the file. Change `--accent-primary` once and the entire UI follows.

| Token                  | Use                                   |
| ---------------------- | ------------------------------------- |
| `--bg-deep`            | page background, behind everything    |
| `--bg-surface`         | panels and cards                      |
| `--accent-primary`     | cyan — primary brand accent           |
| `--accent-success`     | green — ALLOW, healthy status         |
| `--accent-warning`     | amber — ESCALATE, standby             |
| `--accent-danger`      | red — REFUSE, errors                  |
| `--accent-novel`       | purple — Novelty criterion            |
| `--font-mono`          | JetBrains Mono — data, code, labels   |
| `--font-sans`          | Inter / system — body prose           |

## Criterion-color mapping (presentation)

| Criterion                | Color                 | CSS var               |
| ------------------------ | --------------------- | --------------------- |
| Novelty of Approach      | Purple                | `--accent-novel`      |
| Technical Difficulty     | Cyan                  | `--accent-primary`    |
| Potential National Impact| Green                 | `--accent-success`    |
| Problem-Solution Fit     | Amber                 | `--accent-warning`    |

The presentation's criteria rail (top of screen) starts with all four badges
greyed out. As each slide advances, the criteria it touches go to **active**
(filled, glowing). Criteria already touched by an earlier slide stay
**touched** (outlined in their color). By slide 7, all four are filled at
once — a visual ledger of how the talk laddered up to 100%.

Each slide also ends with an in-content **criterion callout** — a small chip
that names which criterion the slide just demonstrated. Judges literally
watch the rubric fill in.

## Slide map

| #   | Title                          | Touches                          |
| --- | ------------------------------ | -------------------------------- |
| 1   | Cold open: the gap is real     | Fit                              |
| 2   | LLM filters leak (20% vs 80%)  | Novelty                          |
| 3   | Three layers, one trust prop.  | Technical, Novelty               |
| 4   | Live: cross-regime catch       | Technical, Fit                   |
| 5   | Live: 5 evasions, same answer  | Novelty, Technical               |
| 6   | Agents, deployable             | Impact, Fit                      |
| 7   | The ask                        | All four                         |

Default per-slide dwell: 40 / 50 / 60 / 65 / 65 / 60 / 45 seconds (~6 min total).
Adjust `DWELL` at the top of `presentation.js` to match your speaking cadence.

## Keyboard shortcuts (presentation mode)

| Key             | Action                            |
| --------------- | --------------------------------- |
| `→` / `Space`   | Next slide                        |
| `←`             | Previous slide                    |
| `Home`          | First slide                       |
| `End`           | Last slide                        |
| `1`–`7`         | Jump directly to slide N          |
| `P`             | Play / pause auto-advance         |
| `Esc`           | Exit presentation, return to `/`  |
