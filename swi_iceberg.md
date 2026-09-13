# swi_iceberg

## A Robust Six-Band MADN Glyph with Population-Width Encoding and Global Context

**Design specification — version 1.0**

**Introduced by:** Sven Pauline
**Year:** 2026
**Copyright:** © 2026 Sven Pauline. Associated with Sheer Will Industry (SWI).
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Status:** Canonical design specification (language-agnostic, publishable)
**Companion document:** *swi_iceberg Implementation Specification* (project binding)
**DOI:** _10.5281/zenodo.<reserved — filled at publication>_

---

## 0. Naming, provenance, and canonical citation

### 0.1 Name

We propose and name this composite visualization the **swi_iceberg glyph** — a
robust, median-centered, MADN-scaled band glyph, pronounced **"sweet iceberg."**
The `swi` prefix associates the glyph with **Sheer Will Industry (SWI)**; the
**iceberg** metaphor names its core idea — a compact visible hull whose submerged
tail mass is still accounted for rather than allowed to dominate the view. The
underlying statistic is **MADN** (defined in §3). Authorship is carried in the
citation line (§0.3), not in the name.

### 0.2 Provenance

- **Originator / copyright holder:** Sven Pauline.
- **Association / brand:** Sheer Will Industry (SWI).
- **Introduced concept:** the swi_iceberg glyph.
- **Content license:** CC BY 4.0 — anyone may reuse the specification with attribution.
- **Scholarly provenance:** a permanent DOI identifies each published version.

### 0.3 Canonical citation

> Pauline, Sven. (2026). *swi_iceberg: A Robust Six-Band MADN Glyph with
> Population-Width Encoding and Global Context* (Version 1.0). Zenodo.
> https://doi.org/10.5281/zenodo.<reserved>

### 0.4 Attribution

Reuse should carry attribution in a manner appropriate to the medium (Creative
Commons recommends the TASL approach: Title, Author, Source, License) and indicate
whether changes were made. Suggested string:

> swi_iceberg — © 2026 Sven Pauline (copyright owner), associated with Sheer Will
> Industry (SWI). Used under CC BY 4.0.

---

## 1. Abstract

The **swi_iceberg glyph** is a categorical distribution mark for comparing groups
of observations (devices, servers, cohorts) whose distributions may differ in
location, spread, skewness, tail weight, and sample size.

Each category is rendered as a vertically stacked **six-band glyph** centered on
its median and scaled by the **Median Absolute Deviation Normalized** (MADN). All
bands share one horizontal population scale: **a band's width is proportional to
the fraction of that category's samples falling within it.** A band's **height is
the observed value range occupied by the samples inside it**, so the vertical
silhouette reflects where the data actually sits rather than a fixed theoretical
block.

The six body bands cover the interval from \(-3\) to \(+3\) MADN about the median.
Observations beyond that robust envelope do not stretch the glyph toward the raw
minimum or maximum; their population is instead carried by two additional tail
regions — **bottoming** (below \(-3\)) and **topping** (above \(+3\)) — drawn at a
fixed symbolic height and encoded by width alone.

A self-similar background applies the identical construction to the pooled data,
giving fleet-wide context without a foreground/context encoding asymmetry.

---

## 2. Motivation and problem space

When comparing categorical distributions (for example, response-latency
distributions across a fleet of devices), an analyst needs to answer several
questions at once. The table below notes where common marks fall short.

| Question | Why existing marks struggle |
|---|---|
| Where does the center lie? | The mean is distorted by outliers; the median needs an explicit mark. |
| How wide is the robust core? | The standard deviation is inflated by tails; box plots use the interquartile range but hide multi-modality. |
| Is there heavy-tail mass? | Box-plot whiskers stretch to extremes and destroy the vertical scale; violin plots show density but obscure tail *mass*. |
| Do categories have different counts? | Variable-width glyphs can conflate width-as-sampling-noise with width-as-uncertainty. |
| What is the global reference? | Backgrounds often differ visually from foregrounds, forcing a second legend. |

The swi_iceberg glyph resolves these through a unified band architecture in which
location and scale use robust estimators (median and MADN), occupied value range
is carried by band **height**, population is carried uniformly by band **width**,
tails never hide (they become width-only regions that do not pull the vertical
axis outward), and context is self-similar (the global background is built from
exactly the same statistical recipe).

---

## 3. Statistical foundation

### 3.1 Notation

For category \(i \in \{1,\dots,K\}\), let

\[
X_i = \{x_{i1}, x_{i2}, \dots, x_{iN_i}\}
\]

be the set of valid numeric observations (invalid and missing entries removed
beforehand), with sample count \(N_i = |X_i|\).

### 3.2 Robust center

\[
m_i = \operatorname{median}(X_i)
\]

The median is the center of the glyph and is rendered as a **solid horizontal
rule** across the glyph footprint (§8).

### 3.3 Robust scale (MADN)

Define the median absolute deviation

\[
\operatorname{MAD}_i = \operatorname{median}_{x \in X_i}\bigl(|x - m_i|\bigr),
\]

and normalize it for consistency under a Gaussian reference:

\[
\hat{\sigma}_i = \operatorname{MADN}_i = 1.4826 \cdot \operatorname{MAD}_i.
\]

The factor \(1.4826\) makes MADN a consistent estimator of the standard deviation
for normally distributed data, so band boundaries read like familiar "one sigma /
three sigma" lines, while MADN itself remains a robust scale statistic with a 50%
breakdown point and does not assume normality. Each observation receives a robust
score

\[
z = \frac{x - m_i}{\hat{\sigma}_i} \qquad (\hat{\sigma}_i > 0).
\]

> Where this quantity carries a local name — for example the historical **"SWI
> sigma"** — that name denotes MADN as defined here. For a general specification,
> **MADN** is the preferred term.

### 3.4 Robust display envelope (the "waterline")

The central body is bounded by the \(\pm 3\) MADN interval

\[
L_i \equiv m_i - 3\hat{\sigma}_i, \qquad U_i \equiv m_i + 3\hat{\sigma}_i.
\]

These limits are the iceberg's waterline: observations inside are placed by their
actual value; observations outside are accounted for by the tail regions but do
not dictate the glyph's vertical extent (§7).

---

## 4. Six-band partition

The body partitions the envelope \([L_i, U_i]\) into **six mutually exclusive,
equal-width bands of one MADN each**, numbered bottom-to-top like floors of a
building. Two additional tail regions collect the population outside the envelope.

| Region | Robust z-range | Name |
|---|---|---|
| \(Z_{i,0}\) | \(x < L_i\) (z < −3) | Bottoming (basement) |
| \(Z_{i,1}\) | \([-3, -2)\) | Lower outer |
| \(Z_{i,2}\) | \([-2, -1)\) | Lower mid |
| \(Z_{i,3}\) | \([-1, 0)\) | Lower inner |
| \(Z_{i,4}\) | \([0, +1)\) | Upper inner |
| \(Z_{i,5}\) | \([+1, +2)\) | Upper mid |
| \(Z_{i,6}\) | \([+2, +3]\) | Upper outer |
| \(Z_{i,7}\) | \(x > U_i\) (z > +3) | Topping (roof) |

Equivalently, for the two body-end bands the envelope is closed, and every valid
observation belongs to exactly one region:

\[
X_i = \bigsqcup_{k} Z_{i,k}, \qquad Z_{i,a} \cap Z_{i,b} = \varnothing \;\; (a \ne b).
\]

An implementation may adopt a different but internally consistent convention for
observations that land exactly on a boundary. The default resolution is one MADN
per band; a finer resolution (smaller band width in MADN units) simply increases
the number of body bands and is a configurable parameter, not a change of model.

Let

\[
n_{i,k} = |Z_{i,k}|, \qquad N_i = \sum_{k} n_{i,k}.
\]

---

## 5. Population encoding by horizontal width

The **normalized population proportion** of region \(k\) is

\[
p_{i,k} = \frac{n_{i,k}}{N_i} \in [0,1], \qquad P_{i,k} = 100\,p_{i,k}\,\%,
\]

and the proportions sum to unity, \(\sum_k p_{i,k} = 1\).

Let \(W_{\max}\) be a single reference width **shared by every category and every
region**. The width of region \(k\) is

\[
\boxed{\,w_{i,k} = W_{\max} \cdot p_{i,k}\,} \qquad\text{so}\qquad w_{i,k} \propto \frac{n_{i,k}}{N_i}.
\]

Consequences:

- A region holding 50% of a category's samples is twice as wide as one holding 25%.
- Widths are comparable across categories because each is normalized by that
  category's own \(N_i\); a category with a huge \(N_i\) does not automatically
  print wider marks than a tiny-\(N_i\) category.
- Each region is centered on the category's nominal x-coordinate \(x_i\):
  \[
  x_{i,k}^{\text{left}} = x_i - \tfrac{w_{i,k}}{2}, \qquad
  x_{i,k}^{\text{right}} = x_i + \tfrac{w_{i,k}}{2},
  \]
  so changes in width never shift the glyph's visual center.
- If a region is empty (\(n_{i,k}=0\)), its width is zero and it is not drawn
  (optionally shown as a gap marker).

Width therefore represents **normalized population**, not absolute count.

---

## 6. Vertical encoding — occupied range in height

The six **body bands** encode, on the vertical axis, the value range their samples
actually occupy. For a non-empty body band \(Z_{i,k}\),

\[
y^{\min}_{i,k} = \min(Z_{i,k}), \qquad y^{\max}_{i,k} = \max(Z_{i,k}), \qquad
h_{i,k} = y^{\max}_{i,k} - y^{\min}_{i,k}.
\]

Because band membership is already constrained by the band's MADN boundaries, these
extremes cannot leave the band; an implementation may additionally intersect the
observed range with the band's absolute limits \([\,m_i + z^{lo}_k\hat{\sigma}_i,\;
m_i + z^{hi}_k\hat{\sigma}_i\,]\) to guard against boundary rounding.

The band is drawn as the axis-aligned rectangle

\[
R_{i,k} = \bigl[x_i - \tfrac{w_{i,k}}{2},\; x_i + \tfrac{w_{i,k}}{2}\bigr]
        \times \bigl[\,y^{\min}_{i,k},\; y^{\max}_{i,k}\bigr].
\]

This yields the glyph's core bivariate read:

\[
\boxed{\text{height} = \text{occupied value range}}, \qquad
\boxed{\text{width} = \text{normalized population}},
\]

which are independent encodings. Two categories may share a band width (equal
population fraction) yet differ in band height (that population spread over a
wider or narrower value range); a band that is tall and thin means "few of my
samples, but scattered across a wide value range in this MADN floor."

---

## 7. Display clipping at ±3 MADN (not winsorization)

An individual glyph does **not** extend its body to the raw sample minimum or
maximum; the body is bounded by \([L_i, U_i]\). An observation \(x \gg U_i\) does
not produce an arbitrarily tall upper band, and \(x \ll L_i\) does not produce an
arbitrarily tall lower band.

This is **display clipping**, not statistical deletion and not statistical
winsorization: the original observations are **not** replaced by boundary values.
They remain part of the distribution and are represented by the **bottoming** and
**topping** regions.

The bottoming and topping are drawn as fixed symbolic-height stubs anchored at the
\(-3\) and \(+3\) boundaries. Their vertical thickness is a rendering parameter and
encodes nothing; their quantitative encoding is horizontal width:

\[
w_{i,\text{bot}} = W_{\max}\,p_{i,\text{bot}}, \qquad
w_{i,\text{top}} = W_{\max}\,p_{i,\text{top}}.
\]

A wide topping therefore means "a large fraction of this category's samples are
catastrophically slow," without a single extreme value destroying the vertical
scale. If a tail region's population is zero, it need not be drawn.

---

## 8. Medians — object and global

- **Object median** \(m_i\): a **solid** horizontal line across the glyph. It is
  not a band and its width encodes no population.
- **Global median** \(M\): a **dashed** horizontal line spanning the plot (§10).

| Indicator | Statistic | Rendering |
|---|---|---|
| Object median | \(m_i\) | Solid line within each glyph |
| Global median | \(M\) | Dashed horizontal reference line |

Together they give simultaneous local and global location: "where is this device's
center, and how does it sit against the fleet's center?"

---

## 9. Color semantics

A diverging palette keyed to band position (adjust hue to brand and accessibility
constraints):

| Region | Signed deviation | Suggested fill | Comment |
|---|---|---|---|
| Bottoming | \(< -3\hat{\sigma}\) | deep forest green | out-of-envelope low tail |
| \(Z_{i,1}\) | \([-3,-2)\) | green | well below median |
| \(Z_{i,2}\) | \([-2,-1)\) | green | below median |
| \(Z_{i,3}\) | \([-1,0)\) | pale green | slightly below median |
| \(Z_{i,4}\) | \([0,+1)\) | amber | slightly above median |
| \(Z_{i,5}\) | \([+1,+2)\) | orange | above median |
| \(Z_{i,6}\) | \([+2,+3]\) | red-orange | well above median |
| Topping | \(> +3\hat{\sigma}\) | dark red | out-of-envelope high tail |

Colors follow a continuous green → yellow → orange → red progression from bottom
to top. Color must never be the sole carrier of meaning: band **position** provides
a redundant encoding, so the glyph stays readable in grayscale or for a
color-blind viewer.

---

## 10. Global reference background

The plot carries a global contextual distribution from the pooled sample

\[
X_G = \bigcup_{i=1}^{K} X_i, \qquad N_G = |X_G|,
\]
\[
M = \operatorname{median}(X_G), \qquad
\hat{\Sigma} = 1.4826 \cdot \operatorname{median}_{x \in X_G}|x - M|.
\]

The background uses the **same band construction and the same signed color
semantics** as the object glyphs — it is itself one swi_iceberg glyph of the pooled
sample, drawn at low opacity and centered on the plot, with a dashed line at \(M\).
Because it is the *same algorithm on a different sample base*, its band widths are
the pooled population fractions and are therefore **non-equal wherever the fleet's
distribution is uneven** (a fleet concentrated near its median shows one wide band;
a heavy-tailed fleet shows a fat topping). This self-similarity means a reader
learns one statistical grammar and applies it to both layers.

There is exactly **one intentional asymmetry** between foreground and background:

| Property | Foreground (per-category) | Global background |
|---|---|---|
| Opacity | Opaque / near-opaque | Faint (\(\alpha \approx 0.08\)–\(0.15\)) |
| Width | Per-category, centered at \(x_i\) | Pooled population fraction, centered on the plot (same encoding, own scale) |
| Tail regions | Clipped to fixed stub height (§7) | Not clipped at \(\pm3\) MADN, but bounded by a **global sky/ground envelope** \(=\min(10\,M,\ \max X_G)\) / \(\max(-10\,M,\ \min X_G)\); pooled tails bleed to that envelope and the plot border turns red where samples exceed it |
| Median | Solid, per-category | Dashed, spanning the plot |

The background is not clipped at \(M \pm 3\hat{\Sigma}\): its outer color regions
continue past \(\pm3\hat{\Sigma}\) so the background remains a complete global
reference even though individual glyph bodies are robustly clipped. It is,
however, bounded by a **global sky/ground envelope** — the smaller of \(10\,M\) and
the pooled maximum (and symmetrically the larger of \(-10\,M\) and the pooled
minimum) — so a single extreme cannot shoot through the plot. Where pooled samples
lie beyond that envelope, the corresponding plot border edge is drawn in a warning
color to signal the shoot-through. The **visible vertical axis is bounded by this
sky/ground envelope and the per-glyph \(\pm3\) MADN envelopes** so that a single
extreme cannot stretch the scale and squash every glyph.

**Why the asymmetry is deliberate:** an individual glyph is an object to be
compared with neighbors, so its body clips vertical tail extent while preserving
tail population in width; the background is a reference frame, so it preserves the
MADN boundaries but does not terminate them.

---

## 11. Complete visual encoding

| Visual property | Statistical meaning |
|---|---|
| x-position | Category |
| y-position | Absolute measured value |
| Body-band height | Observed value range occupied within that band |
| Region width | Fraction of the category's samples in that region |
| Band color | Signed MADN region |
| Bottoming width | Fraction below \(-3\) object MADN |
| Topping width | Fraction above \(+3\) object MADN |
| Solid line | Object median |
| Faint background bands | Pooled / global MADN context (bounded by the global sky/ground envelope) |
| Dashed line | Global median |

---

## 12. Conservation of population

Because the regions form a partition of the category population,

\[
\sum_{k} n_{i,k} = N_i \qquad\text{and}\qquad \sum_{k} p_{i,k} = 1.
\]

Every valid sample contributes to exactly one region; clipped observations are not
lost from the population accounting — they move into bottoming or topping. This is
the key property that distinguishes display clipping from data removal, and it is
the primary implementation invariant (§14).

---

## 13. Interpretation guide

To read one glyph, then the fleet:

1. **Level** — where the solid median sits on the absolute axis, and relative to
   the dashed global median (a category centered inside the red global bands is
   high for the fleet).
2. **Silhouette** — is the building taller above or below the median? (skew)
3. **Band widths** — are the inner bands wider than the outer ones (mass near the
   median)? Is the topping disproportionately thick (heavy upper tail)? The
   bottoming (many unexpectedly fast samples)?
4. **Band heights** — a band stretched over a wide value range signals high
   conditional variance in that MADN floor; a gap between two fat bands signals
   multi-modality.
5. **Neighbors** — compare the lineup: does category A show a thin lower band and a
   fat topping where category B is symmetric?

---

## 14. Statistical invariants

1. The median is always the center of a glyph.
2. MADN is \(1.4826 \times \operatorname{median}(|x - \operatorname{median}(x)|)\).
3. The default envelope is \(\pm 3\) MADN; it is configurable.
4. The body is partitioned into equal-width MADN bands (default six over \(\pm3\));
   each band's **width** is its normalized population and its **height** is the
   observed value range of the samples in it.
5. The body is clipped to the envelope; out-of-envelope observations are retained
   as bottoming/topping, never discarded.
6. Bands are positioned at absolute value \(m_i + z\hat{\sigma}_i\), so glyphs
   float on a shared axis.
7. All widths use one shared \(W_{\max}\) and are normalized by \(N_i\).
8. Region populations sum to \(N_i\) (equivalently, proportions sum to 1).
9. The minimum sample size is 100; below that no glyph is produced and the user is
   prompted.
10. Zero MAD collapses the glyph to a single line at the median (no artificial
    spread).
11. Signed value domains are supported; the default latency view clamps the visible
    lower bound at zero.
12. The global background uses the same construction on the pooled sample, drawn
    transparent; it is not clipped at ±3 MADN but is bounded by the global
    sky/ground envelope, with a border warning where samples exceed it.

---

## 15. Design rationale

- **Median, not mean.** A location estimator resistant to isolated extremes, and it
  naturally divides the construction into lower and upper halves.
- **MADN, not standard deviation.** MADN down-weights the very outliers the design
  is taming, keeping the waterline stable for log-normal or heavy-tailed data. The
  \(\pm1\) and \(\pm3\) lines are MADN-scale boundaries, not automatically
  normal-distribution probability intervals.
- **Population in width.** Each region's width is samples-in-region over
  samples-in-category, so population structure compares across categories
  independently of absolute count.
- **Range in height.** Central bands show the actual occupied value range, not just
  a fixed theoretical block, preserving spread information a pure count encoding
  would lose.
- **Tail mass without tail-dominated scale.** Drawing raw extremes preserves
  severity but destroys vertical resolution; deleting them preserves scale but hides
  them. The glyph takes a third path — clip vertical tail magnitude, keep tail
  population in width.
- **Self-similar focus and context.** One construction, one zone scheme, one color
  scale for glyph and background; the only differences are rendering (opacity,
  clipping, solid vs dashed).

---

## 16. Edge cases and degenerate handling

| Situation | Behavior |
|---|---|
| \(N_i = 0\) (empty category) | Draw nothing or a placeholder; never divide by zero. |
| \(N_i < 100\) | Below the canonical minimum: no glyph, prompt the user (MADN is unstable for small \(n\)). |
| \(\hat{\sigma}_i = 0\) (over half the samples identical) | Collapse to a single line at the median; do not inject an artificial epsilon. |
| Empty body band | \(p=0\), width \(0\), not drawn (optionally a gap marker). |
| All mass in one tail | e.g. \(p_{\text{top}}=1\): a wide topping at the roof anchor, the rest of the building absent — correctly signaling an entirely out-of-envelope category. |
| Strongly multimodal data | A band stores population and occupied range but not internal gaps; two clusters at opposite ends of a band read the same as continuous fill there. The glyph is a robust summary, not a full density estimate. |
| Very large \(W_{\max}\) | Choose \(W_{\max}\) so the widest expected band fills roughly 70–80% of the inter-column space; opaque mode requires \(W_{\max}\) ≤ column spacing. |

---

## 17. Relation to existing visualization families

- **Box plots** partition by quantiles and typically an interquartile range; the
  swi_iceberg glyph partitions by median-centered MADN regions and encodes
  normalized population in width — it is not a conventional box plot.
- **Variable-width box plots** vary the width of a whole box by total count; here
  width varies **independently per band** by that band's population fraction.
- **Violin and density plots** use continuously varying width (a kernel-density
  estimate); this glyph uses a small number of discrete robust zones and direct
  population fractions.
- **Candlestick charts** may resemble the silhouette but encode open/high/low/close;
  this glyph does not.
- **Statistical process-control zone charts** share the deviation-region idea but
  draw horizontal reference lines on a run chart; this glyph uses robust MADN
  scale, per-category population-width bands, observed-range heights, explicit tail
  regions, and a self-similar background bounded by a global sky/ground envelope.

---

## 18. Novelty statement

We propose and name this composite visualization; we do **not** claim that no
visually similar encoding has ever existed. A conservative statement of the
candidate differentiation is:

> The swi_iceberg glyph combines median/MADN robust bands, observed value range in
> each band's height, normalized per-band population width, a body clipped to
> \(\pm3\) MADN with tail population preserved as bottoming/topping, and a
> self-similar globally-bounded background. To the author's knowledge this exact
> combination lacks an established standard name.

This is not a patentability opinion or an exhaustive prior-art determination. A
formal literature and patent search should accompany any strong novelty claim.

---

## 19. Recommended figure legend

> **Figure X.** swi_iceberg comparison of latency distributions across \(K\)
> categories. Each vertical stack is a six-band glyph centered on its category
> median (solid black line). Bands are signed deviations in units of MADN
> (\(\hat\sigma\)): **bottoming** (\(<-3\)), **lower outer / mid / inner**
> (\(-3\) to \(0\)), **upper inner / mid / outer** (\(0\) to \(+3\)), **topping**
> (\(>+3\)). A band's **horizontal width** is proportional to the percentage of the
> category's samples in it (shared scale \(W_{\max}\)); its **vertical height** is
> the observed value range those samples occupy. The body is clipped to \(\pm3\)
> MADN so outliers cannot distort the silhouette; bottoming and topping carry the
> clipped tail population as fixed-height, width-encoded stubs. The faint
> background is the fleet-wide distribution built from the same rules (dashed line
> = global median), with its outer regions bounded by the global sky/ground
> envelope (red border edge where pooled samples exceed it).

---

## 20. Terminology

- **swi_iceberg glyph** — the complete per-category mark (six body bands plus
  bottoming/topping).
- **Body** — the six central bands from \(-3\) to \(+3\) MADN.
- **Bottoming / Topping** — the optional tail regions below \(-3\) / above \(+3\)
  object MADN.
- **MAD** — median absolute deviation. **MADN** — normalized MAD, \(1.4826\cdot\text{MAD}\).
- **SWI sigma** — application-specific alias for MADN when defined identically.
- **Object median / Global median** — per-category \(m_i\) (solid) and pooled \(M\) (dashed).
- **Population width** — a region's horizontal width proportional to its share of samples.
- **Occupied range height** — a body band's vertical extent equal to the observed value range within it.
- **Display clipping** — bounding the body at \(\pm3\) MADN while retaining out-of-envelope observations as bottoming/topping (distinct from winsorization and from deletion).

---

## 21. File metadata for deposit

- **Title:** swi_iceberg: A Robust Six-Band MADN Glyph with Population-Width Encoding and Global Context
- **Creators:** Sven Pauline (Sheer Will Industry / SWI)
- **Description:** Specification of a categorical distribution glyph — its statistical foundation (median / MADN), six-band geometry, population-width and occupied-range-height encoding, tail preservation, and self-similar global context layer.
- **Keywords:** visualization; distribution comparison; robust statistics; median absolute deviation; MADN; outlier visualization; latency; categorical data; glyph
- **License:** CC BY 4.0 (text and figures)
- **Related identifiers:** implementation repository — https://github.com/2makeitwork/swi_cake
- **Publisher:** Zenodo
- **Publication date:** _[ISO-8601, set at deposit]_

---

## 22. References

[1] Tukey, J. W. (1977). *Exploratory Data Analysis.* Addison-Wesley.
[2] Wickham, H., & Stryjewski, L. (2011). *40 Years of Boxplots.*
[3] Borgo, R., et al. (2013). *Glyph-based Visualization: Foundations, Design Guidelines, Techniques and Applications.* Eurographics State of the Art Reports.
[4] Leys, C., et al. (2013). *Do not use the mean when you are expecting a difference: Robustness of the median and MAD.* Journal of Experimental Social Psychology.
[5] Shewhart, W. (1931); Western Electric *Quality Control Handbook* — sigma-zone rules.
[6] Robust-scale convention: for a Gaussian, \(\sigma \approx 1.4826 \cdot \operatorname{MAD}\).

---

## 23. License

**swi_iceberg — design specification.** Copyright © 2026 Sven Pauline. Associated
with Sheer Will Industry (SWI).

This document is licensed under CC BY 4.0: you may share and adapt it for any
purpose, including commercially, with attribution, a link to the license, and an
indication of changes. Full text: https://creativecommons.org/licenses/by/4.0/. CC
BY 4.0 governs the copyright in this text and its figures; it grants no patent
right, and any patent position on the mechanism is separate from this copyright
license. The copyright license does not, by itself, create exclusive rights over
the underlying statistical or visualization method.

The executable reference implementation is offered under the Apache License,
Version 2.0 (see `LICENSE-CODE`).

**Authorship:** Sven Pauline, 2026.

---

## 24. Summary of defining properties

1. The object median is the center; MADN is the robust scale.
2. Six equal 1-MADN body bands span \(-3\) to \(+3\) MADN.
3. Every region's **width** is its normalized population (shared \(W_{\max}\)).
4. Every body band's **height** is the observed value range within it.
5. The body is display-clipped to \(\pm3\) MADN; extremes are retained as
   bottoming and topping (fixed height, width-encoded).
6. A solid line marks the object median; a dashed line marks the global median.
7. A self-similar, low-opacity global background, bounded by a sky/ground envelope,
   provides pooled MADN context.
8. Populations are conserved: regions partition the category.
9. Minimum \(N = 100\); zero MAD collapses to a median line.

The result separates **location**, **occupied range**, **population**, **robust
deviation**, and **global context** into distinct but coordinated visual channels.

**End of specification v1.0**
