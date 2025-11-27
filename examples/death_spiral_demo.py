import time
import random

from synkyria import SynkyriaMonitor


def simulate_death_spiral():
    print("=== Synkyria Monitor – The 'Death Spiral' Test ===")
    print("Scenario: Permanent gradient explosion starting at Epoch 6.")
    print("Goal: Prove the monitor KNOWS when to quit (cost saving).\n")

    monitor = SynkyriaMonitor()

    # Initial training metrics
    lr = 0.001
    current_val_acc = 0.10
    current_loss = 2.5

    # We simulate a relatively long run (25 epochs)
    max_epochs = 25

    for epoch in range(1, max_epochs + 1):
        # --- 1. Simulate training dynamics ---
        # Until epoch 5: normal training
        # From epoch 6 onwards: permanent collapse (death spiral)
        is_dying = epoch >= 6

        if is_dying:
            print(f"    [!] CRITICAL FAILURE: Gradients exploding... (Epoch {epoch})")
            # Loss explodes, accuracy drops aggressively
            current_loss += random.uniform(0.5, 1.5)
            current_val_acc -= random.uniform(0.08, 0.15)
        else:
            # Normal healthy training
            current_loss -= random.uniform(0.05, 0.15)
            current_val_acc += random.uniform(0.03, 0.05)

        # Clamp values to reasonable ranges
        current_loss = max(0.1, current_loss)
        current_val_acc = min(0.99, max(0.05, current_val_acc))

        # --- 2. Call the Synkyria Monitor (the product) ---
        state = monitor.step(epoch, current_loss, current_val_acc)

        # --- 3. Log output ---
        print(
            f"[Epoch {epoch:02d}] Loss={current_loss:.3f} | Val={current_val_acc:.3f} || "
            f"CRQ={state.crq:.2f} SCP={state.scp:.2f} -> [{state.status}]"
        )

        # --- 4. Execute monitor actions ---
        if state.action == "REDUCE_LR":
            lr *= 0.5
            print(
                f"    >>> MONITOR INTERVENTION: Reducing LR to {lr:.6f} (attempting therapy)."
            )

        if state.action == "STOP":
            print("\n🛑 SYNKYRIA KILL SWITCH ACTIVATED 🛑")
            print("    REASON: Structural collapse confirmed (SCP < 0.30 or chronic crisis).")
            print(f"    VALUE:  Prevented {max_epochs - epoch} epochs of wasted compute.")
            print("    CONTEXT: This is exactly the kind of 'zombie run' Synkyria prevents.")
            break

        time.sleep(0.2)

    print("\n--- End of death spiral demo ---")


if __name__ == "__main__":
    simulate_death_spiral()
