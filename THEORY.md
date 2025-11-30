# Synkyrian Theory Background for Synkyria Monitor – Core v1.0.1

This document gives a compact, theory-first overview of the Synkyrian framework
underlying **Synkyria Monitor – Core v1.0.1**.  
It is not required to *use* the library, but it explains where the ideas
(CRQ, SCP, finite-horizon viability) come from and how they relate to the
broader Synkyrian programme.

The relevant references are:

- **Synkyrian Stability as an Architectural Framework:  
  From Classical Risk Tools to Viability, Latency, and Morphogenesis**  
  (Kalomoirakis, 2025, Zenodo preprint)

- **Tropic Information Theory: Information as Holding Load and  
  the Necessity of Selective Deletion** (Kalomoirakis, 2025, preprint)

- **Synkyrian Geometric Morphogenesis: Hazard Landscapes, Information Weight,  
  and Tropic Holding** (Kalomoirakis, 2025, preprint)

- **Minimal Synkyrian Training Companion (v1.0)** and  
  **Synkyria Monitor – Core v1.0.1** (software releases on Zenodo)


---

## 1. Rigorous finite-horizon holding index

In the Synkyrian stability paper, a stochastic system is modelled as a
Markov process on a state space $X$ with a set of failure states $F \subset X$.
For an initial condition $x \in X$ and a time horizon $T > 0$, we define the
failure probability

$$
q_T(x) \=\ \mathbb{P}_x\bigl(\tau_F \le T\bigr),
$$

where $\tau_F$ is the first hitting time of the failure set $F$.

The **rigorous finite-horizon holding index** is then

$$
H_{\mathrm{rig}}(x;T)
\:=\
-\frac{1}{T}\\log q_T(x).
$$

Intuitively:

- large $H_{\mathrm{rig}}$ means “failure before time $T$ is expensive / unlikely”,
- small $H_{\mathrm{rig}}$ means “failure before time $T$ is cheap / likely”.

Under mild axioms (monotonicity in $T$, consistency under coarse-graining,
conservativity under surrogates), this quantity plays the role of a **canonical
finite-horizon viability index**. Other “Synkyrian” indices are compared to
$H_{\mathrm{rig}}$ and are considered valid if they are conservative surrogates:
they do not overestimate the true viability.


---

## 2. From the Holding Equation to practical indices

In more structured settings (e.g. open thermodynamic systems), one can express
$H_{\mathrm{rig}}$ or its surrogates in terms of measurable flows:

- support / input flux $\Phi_S(t)$,
- dissipation / loss $\sigma(t)$,
- effective load / resistance $L(t)$.

A minimal “holding equation” has the schematic form

$$
\dot{H}(t) = \alpha N(t) - \beta L(t) H(t),
$$

with

$$
N(t) = \Phi_S(t) - \sigma(t), \qquad L(t) \ge 0,
$$

and $\alpha, \beta > 0$ parameters.  
Here $H(t)$ is a **stock of holding** whose dynamics respect basic
Second-Law-style constraints: net inflow increases viability, dissipation
and load deplete it.

In the Synkyrian theory:

- $H_{\mathrm{rig}}$ is the canonical, probability-based index;
- differential “holding equations” provide **mesoscopic models** that connect
  $H$ to observable fluxes and loads in particular domains (thermodynamics,
  networks, training dynamics, etc.).


---

## 3. Where CRQ and SCP fit in

**Synkyria Monitor – Core** does *not* attempt to estimate $H_{\mathrm{rig}}$
directly. Instead, it implements two **operational surrogates** for use on
finite training logs:

- **CRQ – Crisis Quotient**  
  A normalised measure of **downside volatility** in the loss:
  roughly, how violently and persistently the loss spikes over a sliding window.

- **SCP – Suspended Coherence Pulse**  
  A normalised measure of **short-term held coherence** in validation performance:
  roughly, how well validation accuracy is being “held” over a window despite noise.

Conceptually, we think of a training run as a trajectory in a latent “hazard
landscape”. True $H_{\mathrm{rig}}$ would be the log-hazard of failure before
a horizon $T$; in practice, we only see a short time series of loss / accuracy.
CRQ and SCP are designed so that:

- high CRQ $\Rightarrow$ **crisis intensity** is building up,
- low SCP $\Rightarrow$ **coherence** is no longer being held.

The governance logic in the monitor (statuses + actions) is then calibrated so
that:

- **chronic high CRQ** and **low SCP** push the system toward `STOP`  
  (structurally doomed / death spiral),
- transient spikes in CRQ with recovering SCP are treated as shocks that can
  be tolerated with `RISK` / `HOLDING` states.

From a Synkyrian viewpoint, CRQ and SCP are **finite-horizon, field-level
symptoms** that track how close the run is to a collapse event in the
underlying hazard geometry.


---

## 4. Tropic Information Theory: information as load

In **Tropic Information Theory**, a unit of information $x$ (an email, a batch,
a request, an update) is not just a string but carries three key attributes:

- $M(x)$ – morphogenetic value (how much it contributes to a form in gestation),
- $R(x)$ – resonance with the current field (how well it fits the current state),
- $c(x)$ – holding cost (how much load it adds if kept).

The field has finite capacity $K_{\max}$ and a time-dependent load $L(t)$.
Holding information increases $L(t)$; deletion or assimilation decreases it.

In this setting, any policy that:

- keeps the field viable (no overload),
- and achieves **non-zero morphogenetic throughput**

must reject or delete a strictly positive fraction of incoming units.
Zero deletion is equivalent either to overload or to vanishing morphogenesis.

For **Synkyria Monitor**, this viewpoint appears in two ways:

1. The monitor itself is an **information filter** over the training log:
   it must ignore a large amount of harmless noise while reacting to
   a smaller set of genuinely structural signals.

2. In potential future extensions, the monitor can be combined with a
   **Tropic load tracker** over a collection of runs, treating each run,
   alert and intervention as a unit that carries morphogenetic value,
   resonance and cost at the level of a research organisation or platform.


---

## 5. Synkyrian Geometric Morphogenesis

The **Synkyrian Geometric Morphogenesis** work interprets $H_{\mathrm{rig}}$ and
related indices as defining a **hazard landscape** over the state space:

- valleys $\Rightarrow$ relatively safe regions,
- saddles / necks $\Rightarrow$ bottlenecks and transition channels,
- steep cliffs $\Rightarrow$ collapse zones.

As information is held (increasing $L(t)$), the landscape is bent: cliffs sharpen,
channels thin, and some previously viable paths become impossible.

Synkyria Monitor fits into this picture as a **local probe** of the hazard
geometry along a 1D trajectory (a single training run). It does not reconstruct
the full manifold but tries to answer:

- “Are we approaching a cliff?” (CRQ high)
- “Is there still a coherent basin being held?” (SCP reasonably high)
- “Has the run entered a chronic collapse regime?” (CRQ high, SCP low,
  status `COLLAPSE` / `CHRONIC_FAILURE`)

In more advanced work, one could imagine:

- aggregating many runs into an empirical hazard landscape,
- studying **morphogenetic transitions** between training regimes,
- and connecting the Synkyria dashboard to network-level or
  multi-kernel architectures.


---

## 6. Limitations and scope of the current implementation

It is important to be explicit about the gap between theory and code:

- The definitions of $H_{\mathrm{rig}}$, hazard landscapes and Tropic load are
  **mathematically rigorous** but live at a more abstract level.

- The CRQ / SCP formulas in `synkyria/monitor.py` are **practical surrogates**:
  sliding-window statistics on loss / validation accuracy tuned to be:

  - conservative (prefer false alarms over missed collapses),
  - simple enough to understand and debug,
  - cheap to compute inside real training loops.

- Synkyria Monitor – Core v1.0.1 should therefore be read as:

  > an *applied* Synkyrian companion,  
  > grounded in a rigorous finite-horizon viability framework,  
  > but intentionally simplified for day-to-day use.

Future versions may tighten the connection to the full Synkyria theory by:

- incorporating more direct hazard-style estimators,
- adding explicit latency / queueing indices,
- and extending from single-run monitoring to **networked / multi-kernel**
  companions for large-scale training systems.
