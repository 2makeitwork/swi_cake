# swi_iceberg

**Compare many distributions side by side — one swi_iceberg per object.**

![swi_iceberg example: twelve objects](docs/figures/swi_iceberg_example.svg)

*Twelve example objects (simulated response latency, milliseconds). Each column is
one swi_iceberg; the faint shape behind them is every object pooled together.*

---

## The idea in one paragraph

Each object's samples are summarized around their **median**, scaled by **MADN**
(the median absolute deviation, ×1.4826 so it reads like a robust "sigma"). That
gives six horizontal bands from −3 to +3 MADN. A band's **width** tells you *how
many* of the object's samples fall in it; its **height** tells you *what value
range* those samples occupy. Samples beyond ±3 MADN are not thrown away — they are
kept as small **topping / bottoming** caps so outliers stay visible without
stretching the picture. Everything floats on one shared absolute axis, so you can
line up a whole fleet and compare level, spread, skew, and tail weight at a glance.

## How to read the picture

| What you see | What it means |
|---|---|
| Vertical position | Absolute value (ms). Objects float at their own level. |
| Band color (green → red) | Which MADN band: low → high. |
| Band **width** | Share of that object's samples in the band. |
| Band **height** | The value range those samples actually span. |
| Solid black line | That object's median. |
| Dashed line | Median of all objects pooled (the global reference). |
| Faint background | The pooled distribution, drawn with the same rules. |
| Dark green / dark red caps | Bottoming / topping — samples beyond ∓3 / +3 MADN. |
| Red top or bottom border | Some pooled samples lie beyond the global clip ("shoot through the roof/floor"). |

An empty gap between bands means *no* samples there; a thin sliver means *a few*.
Two fat bands with a gap between them (see `bimodal`) is a two-mode distribution.

## How a swi_iceberg relates to the underlying distribution

Each panel below shows one of the twelve example objects twice, on the same value
axis: its **sample histogram** (left, count growing to the right) and its
**swi_iceberg** (right). The twelve objects deliberately cover different
distribution shapes so you can see how each shape maps onto the swi_iceberg.

![swi_iceberg vs the underlying distribution for twelve example objects](docs/figures/swi_iceberg_vs_distribution.svg)

Reading the pairs:

- **Normal (tight / reference / wide)** — a bell histogram becomes a symmetric swi_iceberg
  whose middle bands are widest; a larger σ makes the swi_iceberg taller, not wider.
- **Right skew** — mass low with a tail upward: wide green/amber low bands plus a
  red topping cap.
- **Left skew** — the mirror image: wide upper bands plus a dark-green bottoming cap.
- **Long tail** — a tight bell with a thin far tail: a compact body plus a topping cap.
- **Bimodal** — two histogram clusters: two fat bands separated by an empty gap.
- **Near-uniform (plateau)** — a flat histogram: two similarly wide middle bands and
  thin outer bands.

## Install and use

Requires Python 3.10+ and NumPy (the only runtime dependency; pandas is **not**
required, though array-likes such as a pandas Series work fine).

```bash
pip install -e .
```

```python
import numpy as np
from swi_iceberg import build_iceberg, to_json

values = np.random.default_rng(0).normal(100, 15, 1500)   # any array-like, n >= 100
g = build_iceberg(values)

g.median, g.madn          # robust center and scale
g.population              # per-band sample counts (low -> high), width encoding
g.band_lo, g.band_hi      # observed value range inside each band, height encoding
g.topping, g.bottoming    # retained samples beyond +3 / -3 MADN
to_json(g)                # plain-JSON handoff payload for your own renderer
```

Fewer than 100 samples raises `InsufficientDataError`; if over half the samples are
identical (MADN = 0) the swi_iceberg collapses to a single line at the median instead of
inventing spread.

## What's in this repository

| Path | Contents |
|---|---|
| [`specification_swi_iceberg.md`](specification_swi_iceberg.md) | The **strict, publishable design specification** of the iceberg fleet (CC BY 4.0). All formal definitions, invariants, and edge cases live here. |
| [`docs/swi_iceberg_User_Manual.md`](docs/swi_iceberg_User_Manual.md) | **User manual**: package API, streaming feed, wait-out pipeline, and the verification harness, with screenshots. |
| [`src/swi_iceberg/`](src/swi_iceberg/) | Reference implementation (Apache-2.0): statistical + rendering layers. |
| [`docs/figures/`](docs/figures/) | Example graphics. |
| [`CITATION.cff`](CITATION.cff) | Canonical citation (DOI reserved until Zenodo publication). |

Tests, the browser verification harness, and the sample-data generators are local
tooling and are intentionally **not** part of this published tree.

## Provenance, license, citation

- Introduced by **Sven Pauline**, 2026; associated with **Sheer Will Industry (SWI)**.
- Specification text and figures: **CC BY 4.0** ([LICENSE](LICENSE)).
- Executable code: **Apache-2.0** ([LICENSE-CODE](LICENSE-CODE)).
- Suggested attribution: *swi_iceberg — © 2026 Sven Pauline (copyright owner),
  associated with Sheer Will Industry (SWI). Used under CC BY 4.0.*
- Cite as: Pauline, Sven (2026). *swi_iceberg: A Robust Six-Band MADN Visualization
  for the Iceberg Fleet*, v1.0 — see [CITATION.cff](CITATION.cff).

Two documents, deliberately separate: the [specification](specification_swi_iceberg.md)
defines the **iceberg fleet** design (language-agnostic), and the
[user manual](docs/swi_iceberg_User_Manual.md) defines how to use the software
package. For the full formal treatment — zone definitions, conservation invariants,
clipping rules, degenerate cases, and relation to prior work — read the
specification. This README is only a friendly front door.
