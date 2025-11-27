
# Synkyria Monitor – Core v1.0.0

> Finite-horizon stability monitor for deep learning training runs.  
> Detects doomed trajectories early, tolerates transient shocks, and saves compute.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17740804.svg)](https://doi.org/10.5281/zenodo.17740804)

---

## 1. What is Synkyria Monitor?

**Synkyria Monitor** is a lightweight, model-agnostic watchdog for training loops.

It tracks short-term training dynamics (loss & validation accuracy) and computes two
canonical indices:

- **CRQ – Crisis Quotient**  
  Measures downside volatility in the loss (how violently things are spiking).

- **SCP – Suspended Coherence Pulse**  
  Measures how well validation performance is being “held” over a short window.

Based on these indices, the monitor exposes a small **governance layer**:

- **Status**: `WARMUP`, `HEALTHY`, `RISK`, `HOLDING`, `COLLAPSE`, `CHRONIC_FAILURE`
- **Actions**:  
  - `"NONE"` – keep going  
  - `"REDUCE_LR"` – apply “therapy” (typically halve the learning rate)  
  - `"STOP"` – kill the run (zombie / doomed trajectory)

The goal is simple:

> **Save time, energy, and money** by stopping bad runs early,  
> without panicking on transient noise or recoverable shocks.

---

## 2. Installation (local dev / pilot use)

From the project root:

```bash
cd Synkyria_Monitor_Core_v1_0_0

# (Optional but recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # on macOS / Linux
# .venv\Scripts\activate    # on Windows

# Install the library locally
pip install --upgrade pip
pip install .
```

To verify the installation:

```bash
python examples/test_library.py
```

You should see something like:

```text
✅ SUCCESS: The Synkyria Library is installed and importing correctly!
   Monitor Status: WARMUP
   CRQ: 0.0
🚀 Ready for production use.
```

---

## 3. Minimal API usage

The public API is exposed via the package namespace:

```python
from synkyria import SynkyriaMonitor

monitor = SynkyriaMonitor()

for epoch in range(1, num_epochs + 1):
    # your training loop here...
    train_loss = ...
    val_acc = ...

    state = monitor.step(epoch, train_loss, val_acc)

    print(
        f"[Epoch {epoch:02d}] Loss={train_loss:.3f} | Val={val_acc:.3f} || "
        f"CRQ={state.crq:.2f} SCP={state.scp:.2f} -> [{state.status}]"
    )

    if state.action == "REDUCE_LR":
        # Example: halve the learning rate
        lr *= 0.5
        print(f"    >>> Synkyria: Reducing LR to {lr:.6f} to stabilise the field.")

    if state.action == "STOP":
        print("    >>> Synkyria: HARD STOP triggered. Run is structurally doomed.")
        print(f"    >>> SAVINGS: Saved {num_epochs - epoch} epochs of compute time.")
        break
```

### 3.1. The `CompanionState` object

Each call to `step(...)` returns a `CompanionState` with:

* `epoch: int` – current epoch
* `status: str` – one of:

  * `"WARMUP"`, `"HEALTHY"`, `"RISK"`, `"HOLDING"`, `"COLLAPSE"`, `"CHRONIC_FAILURE"`
* `crq: float` – Crisis Quotient (0.0–1.0)
* `scp: float` – Suspended Coherence Pulse (0.0–1.0)
* `action: str` – `"NONE"`, `"REDUCE_LR"`, or `"STOP"`

You can log these values directly or push them into your own dashboard / metrics system.

---

## 4. Included demos

All demos live in `examples/` and use the public API.

Run them from the project root with the virtual environment activated, e.g.:

```bash
python examples/death_spiral_demo.py
```

### 4.1. `nanogpt_stress_test.py`

**Scenario:** Gradual overfitting / data poisoning.

Shows that Synkyria:

* stays quiet while training is healthy,
* raises **RISK** as `CRQ` spikes and `SCP` weakens,
* applies `"REDUCE_LR"`,
* eventually triggers `"STOP"` on a structurally doomed run,
  reporting how many epochs of compute were saved.

---

### 4.2. `transient_shock_demo.py`

**Scenario:** “Bad batch” / transient noise between epochs 8–10, then recovery.

Demonstrates:

* **Shock detection** with clear logs (`SYSTEM SHOCK DETECTED`),
* temporary **RISK / HOLDING** state,
* and crucially, **no premature STOP**.

Near epoch 15 you should see:

```text
>>> SUCCESS: Synkyria recognised the recovery and released the hold!
```

This is the “intelligent tolerance” behaviour: the monitor acts, but does not panic.

---

### 4.3. `death_spiral_demo.py`

**Scenario:** Permanent gradient explosion starting at epoch 6 (“death spiral”).

Demonstrates the **kill switch**:

* multiple critical failures,
* `"REDUCE_LR"` attempted once,
* then `"STOP"` once `SCP` confirms **structural collapse**.

The demo prints the number of epochs (and by implication, cost) that were avoided:

```text
🛑 SYNKYRIA KILL SWITCH ACTIVATED 🛑
    REASON: Structural collapse confirmed (SCP < 0.30 or chronic crisis).
    VALUE:  Prevented 17 epochs of wasted compute.
```

---

### 4.4. `production_demo.py`

**Scenario:** Enterprise-style “zombie run” detection on a simulated multi-node cluster.

This is the **pitch-ready** demo:

* descriptive header (`SYNKYRIA ENTERPRISE PROTECTION LIVE DEMO`),
* scenario type and cluster cost,
* clear per-epoch logs of model status,
* and an **emergency stop** message with estimated dollar savings.

Example output:

```text
🛑 EMERGENCY STOP TRIGGERED BY SYNKYRIA 🛑
   REASON: Structural collapse confirmed (SCP < 0.30).
   VALUE:  Prevented 12 epochs of wasted compute.
   SAVINGS: Estimated $1,680 (assuming cluster cost).
```

---

## 5. Plugging into real training code

### 5.1. Keras / TensorFlow (conceptual sketch)

You can call Synkyria in your training loop or inside a custom callback:

```python
from synkyria import SynkyriaMonitor
from tensorflow.keras.callbacks import Callback

monitor = SynkyriaMonitor()

class SynkyriaKerasCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        loss = float(logs.get("loss", 0.0))
        val_acc = float(logs.get("val_accuracy", 0.0))

        state = monitor.step(epoch + 1, loss, val_acc)

        if state.action == "REDUCE_LR":
            old_lr = float(self.model.optimizer.learning_rate.numpy())
            new_lr = old_lr * 0.5
            self.model.optimizer.learning_rate.assign(new_lr)
            print(f"[Synkyria] REDUCE_LR: {old_lr:.6f} → {new_lr:.6f}")

        if state.action == "STOP":
            print("[Synkyria] STOP: structurally doomed run – stopping training.")
            self.model.stop_training = True
```

Then:

```python
model.fit(
    x_train,
    y_train,
    validation_data=(x_val, y_val),
    epochs=50,
    callbacks=[SynkyriaKerasCallback()],
)
```

### 5.2. PyTorch / HuggingFace / Lightning

The pattern is the same:

1. Compute `train_loss` and `val_acc` for each epoch (or evaluation window).
2. Call `state = monitor.step(epoch, train_loss, val_acc)`.
3. Log `state.status`, `state.crq`, `state.scp`.
4. Apply `REDUCE_LR` and respect `STOP` according to your training framework.

Future versions may include first-class helpers for HuggingFace and Lightning,
but the core logic is purposely simple and framework-agnostic.

---

## 6. Requirements

* Python **3.9+**
* `numpy >= 1.22`

---

## 7. License

## 7. License

Synkyria Monitor – Core v1.0.0 is released under a **custom source-available license**
intended for research, evaluation, and internal pilot use only.

In short:

- You **may** use it internally for research, prototyping, and proof-of-concept pilots.
- You **may not** incorporate it into commercial products or paid services, or
  redistribute/sublicense it, without prior written permission.

See the `LICENSE` file in the repository for the full terms.


---

## 8. Citation (optional)

If you use **Synkyria Monitor** in academic work or internal reports, you can cite it as:

> P. Kalomoirakis, *Synkyria Monitor – Finite-Horizon Stability as an Architectural Framework*, 2025.

(Full BibTeX entry can be added here once the corresponding paper / preprint is public.)

---

