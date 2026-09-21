# swi_iceberg — User Manual

**Software package usage · version 1.0**

**Package:** `swi_iceberg` (Python 3.10+, NumPy; no other runtime dependency)
**Code license:** Apache-2.0 ([LICENSE-CODE](../LICENSE-CODE))
**Design specification:** [specification_swi_iceberg.md](../specification_swi_iceberg.md)
(CC BY 4.0) — the *iceberg fleet* design lives there; this manual covers only how to
use the software.
**Verification harness:** local tooling, not part of this repository; the page it
builds is published under [fleet/](fleet/) — see section 7.

---

## 1. Install

```bash
pip install -e .            # from the repository root
```

```python
from swi_iceberg import build_iceberg, IcebergFeed, IcebergPipeline
from swi_iceberg import to_ascii, to_json, to_raster, global_zone_index
```

---

## 2. Batch API: `build_iceberg`

```python
glyph = build_iceberg(values, resolution=1.0, z_min=-3.0, z_max=3.0)
```

| Argument | Meaning | Default |
|---|---|---|
| `values` | any array-like of numbers (signed domains allowed) | — |
| `resolution` | band width in MADN (σ̂) units | `1.0` → six bands over ±3 |
| `z_min`, `z_max` | clipping envelope in MADN units | `-3.0`, `3.0` |

Returns an immutable `IcebergGlyph`:

| Field | Meaning |
|---|---|
| `n` | sample count |
| `median`, `madn` | robust center and scale (MADN = 1.4826 · MAD) |
| `population` | uint32 counts per band, low → high (**width** encoding) |
| `edges` | band edges in MADN units (len = bands + 1) |
| `band_lo`, `band_hi` | observed value range inside each band (**height** encoding); NaN when a band is empty |
| `lower`, `upper` | absolute ±3 MADN envelope |
| `topping`, `bottoming` | retained counts beyond +3 (topping) / −3 (seat pad) MADN |
| `mode`, `value` | `"collapsed"` and the median when MADN = 0 |
| `.normalized` | `population / n` |

Errors: `InsufficientDataError` below 100 samples; `ValueError` for non-positive
resolution or `z_max <= z_min`.

```python
>>> glyph.population
array([  43,  291,  666,  675,  280,   42], dtype=uint32)
>>> print(to_ascii(glyph))          # quick terminal view
```

---

## 3. Rendering helpers

- `to_ascii(glyph, width=40)` — dependency-free text rendering (bands high → low,
  run length ∝ population, observed range printed per band).
- `to_json(glyph)` — the canonical handoff payload (statistics only, no pixels):
  `mode, n, median, madn, resolution, z_min, z_max, lower, upper, edges, population,
  normalized, band_lo, band_hi, topping, bottoming, value, spec_version, display_version`.
  NaN ranges serialize to `null`. This is what the browser harness consumes. The two
  version fields travel on independent axes: `spec_version` guards the handoff schema
  (which fields exist), `display_version` guards the drawing rules the renderer
  implements (visual spec §2). The package exports both as `SPEC_VERSION` and
  `DISPLAY_VERSION` constants from `swi_iceberg`.
- `to_raster(glyph, height_px, width_px)` — optional 2D bitmap (a render artifact).

---

## 4. Streaming feed: `IcebergFeed`

Initial batch, then **one value at a time**:

```python
feed = IcebergFeed()                 # resolution / z_min / z_max / min_samples
feed.feed_batch(first_samples)       # must reach >= 100
feed.feed_one(new_value)             # incremental update, arrival order
feed.ready, feed.n                   # state
feed.median                          # exact, O(1), no floating-point accumulation
feed.madn                            # exact, recomputed on demand
glyph = feed.glyph()                 # InsufficientDataError below 100
feed.reset()                         # fresh window
```

Numerical stability: the median is maintained as an **order statistic** (sorted
container), so it is exact with no running-sum drift — the incremental analogue of
Welford's algorithm for the mean. MADN and the band binning depend on the current
median, so they are recomputed exactly on demand instead of accumulated.

---

## 5. Wait-out pipeline: `IcebergPipeline`

Batches of **1..N** samples, processed after a **2-second wait-out** (configurable),
no matter how many accumulated:

```python
pipe = IcebergPipeline(flush_interval=2.0)   # default 2 s
pipe.start()                                 # background wait-out flusher
pipe.submit(single_value)                    # N = 1
pipe.submit(batch_of_any_size)               # N = many
pipe.submit(values, reset=True)              # reset parameter: fresh window first
pipe.flush()                                 # manual flush on demand
pipe.pending, pipe.n, pipe.batches_processed
glyph = pipe.glyph()                         # processed state (flush first to include pending)
pipe.reset(); pipe.stop()
```

Updates are incremental (sorted-insert into the order statistics); a flush processes
whatever is buffered, even a single sample.

---

## 6. Zone helper

```python
global_zone_index(value, median, madn)   # 0..5 for the six pooled σ̂ bands, None beyond ±3
```

Used by the harness for the per-zone show/hide toggles.

---

## 7. The verification harness (iceberg fleet viewer)

The harness source is local tooling — a Vite + TypeScript + Tailwind application that
renders inline SVG — and is not part of this repository. Its built page is published
in [`fleet/`](fleet/). GitHub Pages serves this whole `docs/` folder as the site root,
so the landing page is <https://swi-iceberg.swi-energy.com/> and the fleet page is
<https://swi-iceberg.swi-energy.com/fleet/>; the `github.io` address
<https://2makeitwork.github.io/swi_cake/fleet/> keeps serving the same files.

The commands below describe the maintainer steps; where they run and their exact
paths are recorded in the harness's own (local) README.

```bash
python <fleet-generator>                                   # default 6-object payload
python <fleet-generator> --seed=1 --fleets=12              # payloads for the "Random fleet" pool
python <fleet-generator> --seed=101 --count=48 --fleets=3  # larger synthetic fleets
python <fleet-generator> --count=300 --out=<stress-payload>.json
npm install && npm run dev           # in the harness directory: http://localhost:5178
npm run typecheck && npm run build   # static bundle in the harness's dist/ directory
# alternate dataset:  http://localhost:5178/?data=devices300.json
# republish: copy the built bundle into docs/fleet/ and commit it
```

Hosting: the publishing source is branch `main`, folder `/docs`, and
[`docs/.nojekyll`](.nojekyll) keeps the Jekyll step out of the build. The site root,
[`index.html`](index.html), is **generated from the repository README** by the harness
build — edit the README and rebuild rather than editing that HTML, or the landing page
and the repository front door will drift apart. The custom hostname lives in
[`CNAME`](CNAME) as `swi-iceberg.swi-energy.com`, which is a
`CNAME` record to `2makeitwork.github.io` in the `swi-energy.com` zone (Cloudflare
name servers). Only that one label is pointed at this site — `swi-energy.com` and
`www.swi-energy.com` serve the company site and must keep their own records. When the
record is proxied through Cloudflare, set SSL/TLS to "Full (strict)" and enable
"Always Use HTTPS"; GitHub issues its own certificate for the hostname, so leave the
record un-proxied until that certificate exists.

The four rendering-contract invariants are still asserted on every load, but the
page no longer draws the pass/fail list (it is shared as a demo): the results go to
one console line and to `window.__SWI_VERIFY__`, which is what the browser
verification step reads. The **Random fleet** button picks another payload from
`fleets/index.json` — the pool is pre-generated by the fleet generator above, because
a static host cannot run it; each pooled fleet is real reference-implementation
output, and its seed is shown next to the button.

### 7.1 Default iceberg fleet (6 objects)

![default iceberg fleet](figures/manual_fleet_default.png)

Each column is one swi_iceberg on a shared absolute axis: band **width** = population
share, band **height** = observed value range, solid line = object median, dashed =
global median, faint bands = pooled reference clipped to the sky/ground envelope
(3 × global median), red carets at the roof = objects whose raw samples shoot through.

### 7.2 Tooltips

Hovering any object column shows object · zone (σ̂) · sample count · percentage of
that object's total (topping / seat pad beyond ±3 σ̂). Hit-tested per column, so it
works at any density.

![tooltip](figures/manual_tooltip.png)

### 7.3 Vertical zoom and panning

Mouse wheel = vertical zoom (anchored at the cursor); the vertical scrollbar pans
the zoomed window; roof/floor axis readings follow the visible window.

![vertical zoom](figures/manual_vzoom.png)

### 7.4 Curves only

Toggle **median / max / min curves** independently, and **curves only** to hide the
objects (slots preserved, never collapsed) leaving the waves, background, and roof
markers.

![curves only](figures/manual_curves_only.png)

### 7.5 Ultra compact view (large fleets)

The **px per object** slider (1–18) sets horizontal density; the normal
width-encoded rendering scales to the slot — 18 px gives every object exactly the
compact slot width, 1 px degenerates to spines (~18× denser). The number beside the
slider states the density actually drawn: the auto-fit slot (18–56 px) while ultra
compact is off, the slider value when it is on, and `slider × zoom` after a horizontal
zoom. Shift+wheel = horizontal zoom in either mode (ceiling 160 px per object); the
horizontal scrollbar pans, and the lineup re-fits itself when the window is resized.

![300 objects, ultra compact view](figures/manual_fleet_300_ultra.png)

### 7.6 Overshoot and roof-breach example (v1.1)

Open <https://swi-iceberg.swi-energy.com/fleet/?data=overshoot.json&curve=median> (or
`?data=overshoot.json` and tick **median curve**). The fleet is a tight normal cluster plus
three objects whose medians sit above the pooled sky/ground clip. It exercises the three
v1.1 display rules together:

- **Roof-breach (visual spec §9):** the red carets at the roof, each labelled with that
  object's raw maximum (e.g. `9467`), mark objects whose samples pass the clip; the roof
  carpet shows the column continues past the ceiling.
- **Median overshoot (visual spec §8):** the blue median curve rises above the roof line at
  the overshooting objects. A run of consecutive overshoots stays above until it ends, and
  the final object leaves the top edge open-ended rather than pinning flat to the roof.
- **Pooled-clip axis (visual spec §7):** the vertical axis is bounded by the clip, so the
  normal cluster fills the frame instead of being squashed by the tall objects.

The **roof clip** slider (3–10) raises the sky clip as a multiple of the pooled median; the
**max curve** toggle overlays each object's raw maximum so the overshoot is easier to trace.

### 7.7 Exporting figures

```bash
node <figure-script> <payload>.json out.svg \
     [--median-curve] [--collapse-hidden] [--vzoom=<f>] [--compare]
```

The standalone figure script reads the same payload the page reads and calls the same
renderer, so an export is the same drawing code as the browser view.

`--compare` produces the histogram-vs-swi_iceberg comparison grid used in the README:

![histogram vs swi_iceberg](figures/swi_iceberg_vs_distribution.svg)

---

## 8. Tests

The test suite is local tooling and is not part of this repository; it runs with
`python -m pytest <tests-directory> -q` from the repository root.

Covers the statistical invariants (median/MADN, six bands, count conservation,
observed-range-within-envelope, zero-MAD collapse, <100 rejection), the streaming
feed (streamed == batch), and the pipeline (1..N batches, wait-out flush,
incremental equality, reset).

---

## 9. License

Executable code: **Apache-2.0** ([LICENSE-CODE](../LICENSE-CODE)).
Specification text and figures: **CC BY 4.0** ([LICENSE](../LICENSE)).
