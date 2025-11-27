"""
synkyria.monitor
----------------

Core monitoring engine for the Synkyria Monitor – v1.0 (Core).

This module implements a lightweight, production-ready companion that
tracks training dynamics over a short sliding window and emits
finite-horizon stability signals:

    - CRQ (Crisis Quotient):   downside volatility of the loss
    - SCP (Suspended Coherence): robustness of validation performance

The governance logic follows the Synkyrian pattern:

    * WARMUP          – not enough history yet
    * HEALTHY         – field is stable, no intervention needed
    * RISK            – early warning, typically triggers LR reduction
    * HOLDING         – extended risk with partial coherence maintained
    * COLLAPSE        – structural failure, hard stop
    * CHRONIC_FAILURE – long-term instability, hard stop

Public API
~~~~~~~~~~

End–users are expected to import and instantiate :class:`SynkyriaMonitor`:

    from synkyria import SynkyriaMonitor

    monitor = SynkyriaMonitor()
    state = monitor.step(epoch, train_loss, val_acc)

For advanced / legacy use cases, :class:`SynkyrianTrainingCompanion`
remains available as the underlying engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque
from typing import Deque, List

import numpy as np


# ---------------------------------------------------------------------------
# Data structure returned at every monitoring step
# ---------------------------------------------------------------------------

@dataclass
class CompanionState:
    """
    Lightweight snapshot of the companion's assessment at a given epoch.

    Attributes
    ----------
    epoch:
        Current training epoch (1-based or arbitrary step index).
    status:
        One of:
        - "WARMUP"
        - "HEALTHY"
        - "RISK"
        - "HOLDING"
        - "COLLAPSE"
        - "CHRONIC_FAILURE"
    crq:
        Crisis Quotient in [0, 1]. Higher = more severe downside volatility
        of the loss over the recent window.
    scp:
        Suspended Coherence in [0, 1]. Higher = validation performance is
        well held. Values below ~0.3 typically indicate structural failure.
    action:
        One of:
        - "NONE"       – no intervention
        - "REDUCE_LR"  – suggest halving (or similar) of the learning rate
        - "STOP"       – suggest hard stop of the run
    """

    epoch: int
    status: str
    crq: float
    scp: float
    action: str


# ---------------------------------------------------------------------------
# Core engine – v1.0
# ---------------------------------------------------------------------------

class SynkyrianTrainingCompanion:
    """
    Core Synkyrian monitoring engine for training runs.

    This class maintains short-term history of loss and validation accuracy,
    computes CRQ/SCP indices, and applies Synkyrian governance logic with
    tolerance and coherence override.

    Parameters
    ----------
    window_size:
        Number of recent epochs to keep in the rolling window. Must be
        at least 2 to compute volatility.
    crq_threshold:
        Threshold on the Crisis Quotient above which the system is considered
        at risk *when the field is not well held*.
    scp_threshold:
        Threshold below which validation coherence is considered weak and
        contributes to "RISK" classification.
    hold_floor:
        If SCP exceeds this value (e.g. 0.80), the field is considered
        "held" and transient CRQ spikes are tolerated.
    scp_stop:
        If SCP drops below this value (e.g. 0.30) under sustained risk,
        the run is treated as structural collapse and a STOP is emitted.
    chronic_risk_epochs:
        If the system remains in "RISK" for this many consecutive epochs,
        it is classified as "CHRONIC_FAILURE" and a STOP is emitted even
        if SCP is not catastrophically low.
    crq_scale:
        Scaling factor for normalising positive loss jumps into [0, 1].
    scp_sensitivity:
        Sensitivity factor mapping validation drop into [0, 1] coherence.
        Higher values make SCP decline faster as validation deteriorates.
    """

    def __init__(
        self,
        window_size: int = 5,
        crq_threshold: float = 0.8,
        scp_threshold: float = 0.4,
        hold_floor: float = 0.80,
        scp_stop: float = 0.30,
        chronic_risk_epochs: int = 6,
        crq_scale: float = 10.0,
        scp_sensitivity: float = 5.0,
    ) -> None:
        if window_size < 2:
            raise ValueError("window_size must be at least 2.")

        self.history_loss: Deque[float] = deque(maxlen=window_size)
        self.history_val: Deque[float] = deque(maxlen=window_size)
        self.window_size = window_size

        self.crq_threshold = crq_threshold
        self.scp_threshold = scp_threshold
        self.hold_floor = hold_floor
        self.scp_stop = scp_stop
        self.chronic_risk_epochs = chronic_risk_epochs

        self.crq_scale = crq_scale
        self.scp_sensitivity = scp_sensitivity

        self.risk_streak: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """
        Reset all internal history and risk counters.

        Useful when starting a new training run within the same process.
        """
        self.history_loss.clear()
        self.history_val.clear()
        self.risk_streak = 0

    def step(self, epoch: int, train_loss: float, val_acc: float) -> CompanionState:
        """
        Ingest a new (loss, val_acc) observation and emit a CompanionState.

        Parameters
        ----------
        epoch:
            Current epoch index (or generic step counter).
        train_loss:
            Training loss at this epoch.
        val_acc:
            Validation accuracy (or any held-out performance metric)
            at this epoch.

        Returns
        -------
        CompanionState
            The current state, including suggested action.
        """
        # Update rolling history
        self.history_loss.append(float(train_loss))
        self.history_val.append(float(val_acc))

        # Not enough history yet: WARMUP
        if len(self.history_val) < self.window_size:
            return CompanionState(
                epoch=epoch,
                status="WARMUP",
                crq=0.0,
                scp=1.0,
                action="NONE",
            )

        # ----------------------------
        # 1. Crisis Quotient (CRQ)
        # ----------------------------
        recent_losses: List[float] = list(self.history_loss)
        loss_jumps = [
            recent_losses[i] - recent_losses[i - 1]
            for i in range(1, len(recent_losses))
        ]
        positive_jumps = [j for j in loss_jumps if j > 0]

        if not positive_jumps:
            crq = 0.0
        else:
            # Map mean positive jump into [0, 1] via a simple scale+clip.
            crq = float(min(1.0, np.mean(positive_jumps) * self.crq_scale))

        # ----------------------------
        # 2. Suspended Coherence (SCP)
        # ----------------------------
        recent_val: List[float] = list(self.history_val)
        val_drop = max(recent_val) - recent_val[-1]

        # SCP = 1.0 (solid coherence) -> 0.0 (broken coherence)
        scp = float(max(0.0, 1.0 - (val_drop * self.scp_sensitivity)))

        # ----------------------------
        # 3. Governance Logic (v1.0)
        # ----------------------------
        status = "HEALTHY"
        action = "NONE"

        # Synkyrian insight:
        # If SCP is high (> hold_floor), the field is considered "held".
        # In that regime we tolerate CRQ spikes (e.g., transient shocks).
        field_is_held = scp > self.hold_floor

        # Risk trigger:
        # - either high CRQ while the field is *not* well held
        # - or SCP below the scp_threshold
        is_risky = (crq > self.crq_threshold and not field_is_held) or (
            scp < self.scp_threshold
        )

        if is_risky:
            self.risk_streak += 1
            status = "RISK"

            # First time in RISK: propose therapy (LR reduction)
            if self.risk_streak == 1:
                action = "REDUCE_LR"

            # Prolonged risk – evaluate kill switch
            elif self.risk_streak >= 3:
                # Structural collapse: coherence broken
                if scp < self.scp_stop:
                    status = "COLLAPSE"
                    action = "STOP"

                # Chronic failure: long risk streak without full collapse
                elif self.risk_streak >= self.chronic_risk_epochs:
                    status = "CHRONIC_FAILURE"
                    action = "STOP"

                else:
                    # Intermediate region: we acknowledge risk but the field
                    # still holds enough coherence to justify tolerance.
                    status = "HOLDING"
        else:
            # Field is stable or recovering: reset risk streak
            self.risk_streak = 0

        return CompanionState(
            epoch=epoch,
            status=status,
            crq=crq,
            scp=scp,
            action=action,
        )


# ---------------------------------------------------------------------------
# Public-facing alias
# ---------------------------------------------------------------------------

class SynkyriaMonitor(SynkyrianTrainingCompanion):
    """
    Official public-facing monitor for the Synkyria library.

    This class simply subclasses :class:`SynkyrianTrainingCompanion`
    without modification, providing a stable, user-friendly entry point
    for external integrations (Keras callbacks, HuggingFace trainers,
    Lightning modules, etc.).

    Typical usage
    -------------

    >>> from synkyria import SynkyriaMonitor
    >>> monitor = SynkyriaMonitor()
    >>> state = monitor.step(epoch, train_loss, val_acc)
    >>> state.status, state.action
    ('HEALTHY', 'NONE')
    """

    pass
