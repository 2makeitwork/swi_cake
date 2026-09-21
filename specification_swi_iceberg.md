# swi_iceberg

## A Robust Six-Band MADN Visualization for the Iceberg Fleet

**Design specification — version 1.1 (statistical model)**

**Introduced by:** Sven Pauline
**Year:** 2026
**Copyright:** © 2026 Sven Pauline. Associated with Sheer Will Industry (SWI).
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
**Status:** Canonical **statistical** specification (language-agnostic, publishable)
**Companion documents:**
- [specification_swi_iceberg_visual.md](specification_swi_iceberg_visual.md) — the **display model**
  (geometry, colour, clipping, roof marking, background, interaction). Version 1.1 moved every
  rendering-normative section out of this document and into that one.
- *swi_iceberg User Manual* (`docs/swi_iceberg_User_Manual.md`) — software package usage
**Document split:** this specification defines the **statistical model** — the numbers and the
invariants that must hold. The visual specification defines how those numbers are **drawn**. The
`to_json` payload is the handoff contract between them.
**DOI:** _reserved — the v1.1 version DOI is minted at the next Zenodo deposit (v1.0: 10.5281/zenodo.22736442)_

---

## 0. Naming, provenance, and canonical citation

### 0.1 Name

The individual mark — one object's distribution — is called **a swi_iceberg**,
pronounced **"sweet iceberg."** A chart that lines up many swi_icebergs on one
shared value axis is called **the iceberg fleet**; it is the iceberg fleet that
makes comparison across objects readable.

The `swi` prefix associates the swi_iceberg with **Sheer Will Industry (SWI)**; the
**iceberg** metaphor names its core idea — a compact visible hull whose submerged
tail mass is still accounted for rather than allowed to dominate the view. The
underlying statistic is **MADN** (defined in §3). Authorship is carried in the
citation line (§0.3), not in the name.

### 0.2 Provenance

- **Originator / copyright holder:** Sven Pauline.
- **Association / brand:** Sheer Will Industry (SWI).
- **Introduced concept:** the swi_iceberg.
- **Content license:** CC BY 4.0 — anyone may reuse the specification with attribution.
- **Scholarly provenance:** a permanent DOI identifies each published version.

### 0.3 Canonical citation

> Pauline, Sven. (2026). *swi_iceberg: A Robust Six-Band MADN Visualization for
> the Iceberg Fleet* (Version 1.1). Zenodo. DOI reserved for the v1.1 deposit
> (the v1.0 record is https://doi.org/10.5281/zenodo.22736442).

### 0.4 Attribution

Reuse should carry attribution in a manner appropriate to the medium (Creative
Commons recommends the TASL approach: Title, Author, Source, License) and indicate
whether changes were made. Suggested string:

> swi_iceberg — © 2026 Sven Pauline (copyright owner), associated with Sheer Will
> Industry (SWI). Used under CC BY 4.0.

---

## 1. Abstract

The **swi_iceberg** is a categorical distribution mark for comparing groups
of observations (devices, servers, cohorts) whose distributions may differ in
location, spread, skewness, tail weight, and sample size.

Each category is rendered as a vertically stacked **six-band swi_iceberg** centered on
its median and scaled by the **Median Absolute Deviation Normalized** (MADN). All
bands share one horizontal population scale: **a band's width is proportional to
the fraction of that category's samples falling within it.** A band's **height is
the observed value range occupied by the samples inside it**, so the vertical
silhouette reflects where the data actually sits rather than a fixed theoretical
block.

The six body bands cover the interval from \(-3\) to \(+3\) MADN about the median.
Observations beyond that robust envelope do not stretch the swi_iceberg toward the raw
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
| Do categories have different counts? | Variable-width swi_icebergs can conflate width-as-sampling-noise with width-as-uncertainty. |
| What is the global reference? | Backgrounds often differ visually from foregrounds, forcing a second legend. |

The swi_iceberg resolves these through a unified band architecture in which
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

The median is the center of the swi_iceberg and is rendered as a **solid horizontal
rule** across the swi_iceberg footprint (§8).

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
not dictate the swi_iceberg's vertical extent (§7).

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

## 5. Normalized population (the width source)

The **normalized population proportion** of region \(k\) is

\[
p_{i,k} = \frac{n_{i,k}}{N_i} \in [0,1], \qquad P_{i,k} = 100\,p_{i,k}\,\%,
\]

and the proportions sum to unity, \(\sum_k p_{i,k} = 1\). These proportions are the
statistical quantity; **how** they are drawn — width proportional to \(p_{i,k}\) on one
shared scale, centered on the object, an empty region as a gap — is specified in the display
model, [§3 of the visual specification](specification_swi_iceberg_visual.md).

---

## 6. Observed value range in height (the height source)

For a non-empty body band \(Z_{i,k}\) the glyph retains the **observed value range** of
the samples inside it:

\[
y^{\min}_{i,k} = \min(Z_{i,k}), \qquad y^{\max}_{i,k} = \max(Z_{i,k}),
\]

carried in the handoff payload as `band_lo[k]` / `band_hi[k]` (`null` for an empty band).
Because band membership is constrained by the band's MADN boundaries, these extremes
cannot leave the band. That the drawn **height** equals this occupied range — and that an
empty band therefore reads as a gap — is the display model's rule,
[§3 of the visual specification](specification_swi_iceberg_visual.md).

---

## 7. Display clipping at ±3 MADN (not winsorization)

An individual swi_iceberg does **not** extend its body to the raw sample minimum or
maximum; the body is bounded by \([L_i, U_i]\). This is **display clipping**, not
statistical deletion and not winsorization: the original observations are **not** replaced
by boundary values — they remain in the distribution and are retained as the
**bottoming** (\(z < -3\)) and **topping** (\(z > +3\)) counts, so population stays
conserved (§12).

How the retained tails are drawn — fixed symbolic-height stubs at the ∓3 boundaries,
quantitative meaning carried by width alone — is the display model's rule,
[§6 of the visual specification](specification_swi_iceberg_visual.md).

---

## 8. Medians — object and global

The two location statistics are the **object median** \(m_i\) (§3.2) and the **global
(pooled) median** \(M\) (§10). Both are centers, not bands, and carry no population width.
Their rendering — solid for the object, dashed spanning the plot for the global — is in the
display model, [§5 of the visual specification](specification_swi_iceberg_visual.md).

---

## 9. Color semantics

Color keys to signed MADN region and follows a continuous green → amber → orange → red
progression from bottom to top; the exact palette, the tail-cap tones, and the redundancy
invariant (position carries the same meaning, so the mark survives grayscale and
colour-blindness) are specified in the display model,
[§4 of the visual specification](specification_swi_iceberg_visual.md). The statistics impose
no colour.

---

## 10. Global (pooled) reference statistics

The fleet has one pooled sample and one pooled center/scale:

\[
X_G = \bigcup_{i=1}^{K} X_i, \qquad N_G = |X_G|,
\]
\[
M = \operatorname{median}(X_G), \qquad
\hat{\Sigma} = 1.4826 \cdot \operatorname{median}_{x \in X_G}|x - M|.
\]

The **global sky/ground envelope** bounds the visible value domain so a single extreme
cannot stretch it:

\[
\text{sky} = \min(c\,M,\ \max X_G), \qquad \text{ground} = \max(-c\,M,\ \min X_G),
\]

with \(c\) a clip multiple (default \(c = 3\)). The pooled raw extremes \(\min X_G\),
\(\max X_G\) and each object's own \(\min\), \(\max\) are carried in the handoff payload
(visual spec §2) so the clip and the shoot-through tests can be evaluated without
recomputation.

How the pooled reference is **drawn** — a faint self-similar swi_iceberg of \(X_G\) at low
opacity, the one intentional foreground/background asymmetry, the raisable clip multiple,
the red border on shoot-through, and the roof-breach markers — is the display model,
[§7 and §10 of the visual specification](specification_swi_iceberg_visual.md).

---

## 11. Complete visual encoding

The full visual-encoding table — every channel (position, height, width, colour, medians,
background, and the v1.1 roof/overshoot/placeholder markers) mapped to its statistical
meaning — now lives in the display model,
[§14 of the visual specification](specification_swi_iceberg_visual.md). This document states
only the quantities those channels encode.

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

To read one swi_iceberg, then the iceberg fleet:

1. **Level** — where the solid median sits on the absolute axis, and relative to
   the dashed global median (a category centered inside the red global bands is
   high for the iceberg fleet).
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

These are the invariants of the **statistical model**; the invariants a conforming
*renderer* must satisfy are in the display model, [§15 of the visual specification](specification_swi_iceberg_visual.md).

1. The median is always the center of a swi_iceberg.
2. MADN is \(1.4826 \times \operatorname{median}(|x - \operatorname{median}(x)|)\).
3. The default envelope is \(\pm 3\) MADN; it is configurable.
4. The body is partitioned into equal-width MADN bands (default six over \(\pm3\));
   each band's **width** is its normalized population and its **height** is the
   observed value range of the samples in it.
5. The body is clipped to the envelope; out-of-envelope observations are retained
   as bottoming/topping, never discarded.
6. Bands are positioned at absolute value \(m_i + z\hat{\sigma}_i\), so swi_icebergs
   float on a shared axis.
7. All widths use one shared \(W_{\max}\) and are normalized by \(N_i\).
8. Region populations sum to \(N_i\) (equivalently, proportions sum to 1).
9. The minimum sample size is 100; below that no swi_iceberg is produced and the user is
   prompted.
10. Zero MAD collapses the swi_iceberg to a single line at the median (no artificial
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
  them. The swi_iceberg takes a third path — clip vertical tail magnitude, keep tail
  population in width.
- **Self-similar focus and context.** One construction, one zone scheme, one color
  scale for swi_iceberg and background; the only differences are rendering (opacity,
  clipping, solid vs dashed).

---

## 16. Edge cases and degenerate handling

| Situation | Behavior |
|---|---|
| \(N_i = 0\) (empty category) | Draw nothing or a placeholder; never divide by zero. |
| \(N_i < 100\) | Below the canonical minimum: no swi_iceberg, prompt the user (MADN is unstable for small \(n\)). |
| \(\hat{\sigma}_i = 0\) (over half the samples identical) | Collapse to a single line at the median; do not inject an artificial epsilon. |
| Empty body band | \(p=0\), width \(0\), not drawn (optionally a gap marker). |
| All mass in one tail | e.g. \(p_{\text{top}}=1\): a wide topping at the roof anchor, the rest of the building absent — correctly signaling an entirely out-of-envelope category. |
| Strongly multimodal data | A band stores population and occupied range but not internal gaps; two clusters at opposite ends of a band read the same as continuous fill there. The swi_iceberg is a robust summary, not a full density estimate. |
| Very large \(W_{\max}\) | Choose \(W_{\max}\) so the widest expected band fills roughly 70–80% of the inter-column space; opaque mode requires \(W_{\max}\) ≤ column spacing. |

---

## 17. Relation to existing visualization families

- **Box plots** partition by quantiles and typically an interquartile range; the
  swi_iceberg partitions by median-centered MADN regions and encodes
  normalized population in width — it is not a conventional box plot.
- **Variable-width box plots** vary the width of a whole box by total count; here
  width varies **independently per band** by that band's population fraction.
- **Violin and density plots** use continuously varying width (a kernel-density
  estimate); this swi_iceberg uses a small number of discrete robust zones and direct
  population fractions.
- **Candlestick charts** may resemble the silhouette but encode open/high/low/close;
  this swi_iceberg does not.
- **Statistical process-control zone charts** share the deviation-region idea but
  draw horizontal reference lines on a run chart; this swi_iceberg uses robust MADN
  scale, per-category population-width bands, observed-range heights, explicit tail
  regions, and a self-similar background bounded by a global sky/ground envelope.

---

## 18. Novelty statement

We propose and name this composite visualization; we do **not** claim that no
visually similar encoding has ever existed. A conservative statement of the
candidate differentiation is:

> The swi_iceberg combines median/MADN robust bands, observed value range in
> each band's height, normalized per-band population width, a body clipped to
> \(\pm3\) MADN with tail population preserved as bottoming/topping, and a
> self-similar globally-bounded background. To the author's knowledge this exact
> combination lacks an established standard name.

This is not a patentability opinion or an exhaustive prior-art determination. A
formal literature and patent search should accompany any strong novelty claim.

---

## 19. Recommended figure legend

> **Figure X.** swi_iceberg comparison of latency distributions across \(K\)
> categories. Each vertical stack is a six-band swi_iceberg centered on its category
> median (solid black line). Bands are signed deviations in units of MADN
> (\(\hat\sigma\)): **bottoming** (\(<-3\)), **lower outer / mid / inner**
> (\(-3\) to \(0\)), **upper inner / mid / outer** (\(0\) to \(+3\)), **topping**
> (\(>+3\)). A band's **horizontal width** is proportional to the percentage of the
> category's samples in it (shared scale \(W_{\max}\)); its **vertical height** is
> the observed value range those samples occupy. The body is clipped to \(\pm3\)
> MADN so outliers cannot distort the silhouette; bottoming and topping carry the
> clipped tail population as fixed-height, width-encoded stubs. The faint
> background is the iceberg fleet-wide distribution built from the same rules (dashed line
> = global median), with its outer regions bounded by the global sky/ground
> envelope (red border edge where pooled samples exceed it).

---

## 20. Terminology

- **swi_iceberg** — the complete per-category mark (six body bands plus
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

- **Title:** swi_iceberg: A Robust Six-Band MADN Visualization for the Iceberg Fleet
- **Creators:** Sven Pauline (Sheer Will Industry / SWI)
- **Description:** Specification of a categorical distribution swi_iceberg — its statistical foundation (median / MADN), six-band geometry, population-width and occupied-range-height encoding, tail preservation, and self-similar global context layer.
- **Keywords:** visualization; distribution comparison; robust statistics; median absolute deviation; MADN; outlier visualization; latency; categorical data; swi_iceberg
- **License:** CC BY 4.0 (text and figures)
- **Related identifiers:** implementation repository — https://github.com/2makeitwork/swi_cake
- **Publisher:** Zenodo
- **Publication date:** _[ISO-8601, set at deposit]_

The operational deposit steps (record creation, upload, and filling the minted DOI
into the three placeholder lines) are maintained locally together with the deposit
metadata, and are intentionally not part of this published document.

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
deviation**, and **global context** into distinct but coordinated channels. The channels
themselves — how each is drawn, and the v1.1 roof-breach, overshoot, and placeholder
markers — are specified in the display model,
[specification_swi_iceberg_visual.md](specification_swi_iceberg_visual.md).

**End of statistical specification v1.1**
