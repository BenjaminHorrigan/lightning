# Lightning Demo — 3 New Pages

Drop-in templates and JS for the `/adversarial`, `/audit`, and `/visualization`
routes. Sci-fi tactical-display aesthetic over Bootstrap 5.1.3 + vanilla JS.
No build step.

## Layout

```
demos/
├── templates/
│   ├── index.html           # already exists
│   ├── adversarial.html     # NEW
│   ├── audit.html           # NEW
│   └── visualization.html   # NEW
└── static/
    ├── css/
    │   ├── style.css                # existing — append style_additions.css
    │   └── style_additions.css      # NEW — sci-fi base styles
    └── js/
        ├── app.js                   # already exists
        ├── adversarial.js           # NEW
        ├── audit.js                 # NEW
        └── visualization.js         # NEW
```

## Integration steps

1. Copy the three `.html` files into `demos/templates/`.
2. Copy the three `.js` files into `demos/static/js/`.
3. Append the contents of `style_additions.css` to your existing
   `demos/static/css/style.css`. (Or rename it to `style.css` if your
   existing file is empty.)
4. Routes already exist server-side — no FastAPI changes needed.

## Endpoints consumed

| Page          | Endpoint                                | Method |
|---------------|-----------------------------------------|--------|
| adversarial   | `/api/adversarial/run`                  | GET    |
| audit         | `/api/audit/summary?days=30`            | GET    |
| audit         | `/api/audit/recent?limit=10`            | GET    |
| audit         | `/api/audit/verify?audit_id=<id>`       | POST   |
| visualization | `/api/analyze`                          | POST   |
| visualization | `/api/visualization/generate`           | POST   |

## Design notes

- **Adversarial**: Lightning vs GPT baseline showdown. Two metric cards with
  count-up animations, color-coded (success-green winner, danger-red loser),
  per-case table with stagger-reveal rows, verdict banner with delta score.
- **Audit**: Cryptographic ledger. Four summary metric cards, Bootstrap-style
  table with audit_id (truncated hash), timestamp, decision badge, and inline
  Verify button. On verify success, the row expands inline to show the full
  hash chain (entry hash, previous hash, proof hash, signed-at).
- **Visualization**: Two-stage forensic flow. Tactical textarea for protocol
  intake, then a split metadata-panel + D3 iframe. Sample protocol button
  loads a turbopump spec for instant demo. Reset button returns to intake.

## Color conventions

- ALLOW    → success green (`#00ff88`)
- REFUSE   → danger red (`#ff3355`)
- ESCALATE → warning amber (`#ffb800`)
- System accent (cyan `#00d4ff`) for Lightning brand and primary CTAs

## Browser support

Modern browsers (Chrome, Firefox, Safari, Edge — last 2 versions). Uses
fetch, async/await, CSS custom properties, no transpilation.

## Iframe sandbox note

The visualization page's D3 iframe uses
`sandbox="allow-scripts allow-same-origin"`. This is intentional — it lets
D3 load from CDN inside the iframe while the iframe's own document context
still isolates DOM and CSS from the parent page (which was the original
"sandbox the D3 viz" requirement). With `allow-scripts` alone, D3 fails
to load and the visualization stays blank.
