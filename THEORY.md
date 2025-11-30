# Synkyrian Theory Background

This repository implements a **practical, minimal dashboard** for finite-horizon
stability in training runs. Internally, however, it is aligned with a broader
theoretical programme: **Synkyrian Stability and Holding**.

The goal of this document is not to reproduce the full theory, but to make clear:

- what the *canonical* Synkyrian quantity is,
- how the Monitor’s indices (CRQ, SCP) relate to it,
- and how this software connects to the surrounding papers and tools.

---

## 1. Canonical holding index \(H_{\mathrm{rig}}\)

At the theoretical level, the core quantity is the **rigorous finite-horizon
holding index**:

\[
H_{\mathrm{rig}}(x; T)
\;:=\;
-\,\frac{1}{T}\,\log q_T(x),
\]

where

- \(x \in X\) is an initial state (or configuration),
- \(F \subset X\) is a set of failure states,
- \(\tau_F\) is the first hitting time of \(F\),
- and \(q_T(x) = \mathbb{P}_x(\tau_F \le T)\) is the probability that the system
  fails before time \(T\).

Intuitively, \(H_{\mathrm{rig}}(x;T)\) measures **how “expensive” it is for the
system to collapse** before the horizon \(T\):

- large \(H_{\mathrm{rig}}\)  → failure before \(T\) is rare (strong holding),
- small \(H_{\mathrm{rig}}\)  → failure before \(T\) is likely (weak holding).

In the Synkyrian framework, \(H_{\mathrm{rig}}\) plays the role of a **canonical
reference functional**:

- it is defined at the level of trajectories and failure sets,
- classical risk tools (first-passage bounds, spectral inequalities, MEPP-style
  principles) can be interpreted in relation to it,
- and any *surrogate* index that claims to measure “holding” can be compared
  against \(H_{\mathrm{rig}}\) via axioms and bounds.

The paper

> P. Kalomoirakis, *Synkyrian Stability as an Architectural Framework:  
> From Classical Risk Tools to Viability, Latency, and Morphogenesis*, Zenodo (2025).

develops this picture in detail, including kernel bottlenecks, latency-aware
indices, and morphogenetic interpretations of finite-horizon hazard.

---

## 2. CRQ and SCP as operational surrogates

The **Synkyria Monitor – Core** does *not* attempt to estimate
\(H_{\mathrm{rig}}\) directly from sparse training signals. That would require
a much richer probabilistic and geometric modelling layer.

Instead, the Monitor implements two **operational surrogates**:

- **CRQ – Crisis Quotient**  
  A scalar proxy for *crisis intensity*. It tracks how violently the loss
  behaves over a short window (downside volatility, spikes, instability),
  highlighting regimes where the run is structurally at risk.

- **SCP – Suspended Coherence Pulse**  
  A scalar proxy for *held coherence*. It tracks how well validation performance
  (or another viability proxy) is being “held” over a short window, even under
  shocks. High SCP means there is still a coherent core pulse; low SCP suggests
  structural collapse or chronic failure.

You can think of CRQ and SCP as coarse projections of the deeper hazard geometry:

- CRQ ~ “how dense and intense are crises becoming?”  
- SCP ~ “is there still a viable pulse that can recover after shocks?”

In the full Synkyrian theory, these would correspond to more refined quantities
in a hazard-landscape or information-geometric manifold. In this v1.0.1
software, they are deliberately kept simple and robust so that:

- they can be computed directly from standard training logs,
- they are easy to read and reason about,
- and they are conservative enough for **pilot use** in real systems.

The Monitor’s governance layer (`WARMUP`, `HEALTHY`, `RISK`, `HOLDING`,
`COLLAPSE`, `CHRONIC_FAILURE` + actions `NONE` / `REDUCE_LR` / `STOP`) is
built on top of these indices as a pragmatic interface for early warning and
intervention.

---

## 3. Relation to other Synkyrian works

The design of Synkyria Monitor is conceptually aligned with three other pillars
of the Synkyrian–Tropic programme:

1. **Synkyrian Stability (finite-horizon viability, kernels, latency)**  
   Provides the formal framework for \(H_{\mathrm{rig}}\), kernel bottlenecks,
   and the idea of stability as *finite-horizon holding* rather than asymptotic
   equilibrium.

2. **Tropic Information Theory (information as load)**  
   Reframes information not as massless bits but as **load** on a finite
   capacity field. This underpins the idea that training signals, logs, and
   interventions all contribute to a limited carrying capacity and must be
   filtered and governed accordingly.

3. **Synkyrian Geometric Morphogenesis (hazard geometry and transitions)**  
   Introduces a geometric reading of viability: hazard landscapes, bottlenecks,
   and morphogenetic transitions. In this view, a training run traverses a
   landscape where crises, recoveries, and collapses correspond to geometric
   events.

4. **Tropic Synkyria Manifesto (conceptual front end)**  
   Summarises the conceptual stance: viability instead of equilibrium,
   information as weight, the necessity of refusal, and form as assimilated
   history. Synkyria Monitor is one concrete, applied “instrument” that
   embodies these ideas for neural network training.

Together, these works form a **unified story**: Synkyria Monitor is not an
isolated heuristic, but a minimal, code-level companion to a broader
geometric–probabilistic view of finite-horizon viability.

---

## 4. Future directions

Version v1.0.1 is intentionally minimal. It focuses on:

- simple indices (CRQ, SCP),
- clear, interpretable statuses,
- and ease of integration into existing training loops.

Future versions may explore:

- tighter links between CRQ/SCP and explicit bounds on \(H_{\mathrm{rig}}\),
- hazard-aware indices that use short-term first-passage estimates,
- extensions to **networked / multi-model settings** (e.g. clusters, ensembles,
  interacting services),
- and richer dashboards that reflect the underlying **hazard geometry** more
  directly.

For now, this repository should be read as a **pilot-ready, didactic companion**:
a way to bring finite-horizon viability thinking into everyday training practice,
without requiring users to implement the full Synkyrian machinery.
