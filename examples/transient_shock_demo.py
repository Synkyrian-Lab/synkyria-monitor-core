import time
import random
from synkyria import SynkyriaMonitor


def simulate_transformer_recovery():
    print("=== Synkyrian Pilot: Resilience Test (Transient Shock) ===")
    print("Scenario: Bad data batch at Epoch 8, recovery at Epoch 11.")
    print("Goal: Show that Synkyria TOLERATES the shock and RECOGNISES recovery.")
    
    monitor = SynkyriaMonitor()
    
    lr = 0.001
    current_val_acc = 0.10
    current_loss = 2.5
    
    for epoch in range(1, 21):
        # 1. Simulate physics: transient glitch
        is_glitch = 8 <= epoch <= 10
        
        if is_glitch:
            print(f"    [!] SYSTEM SHOCK DETECTED (Bad Batch/Noise) at Epoch {epoch}")
            current_loss += random.uniform(0.3, 0.5)
            current_val_acc -= random.uniform(0.02, 0.05)
        else:
            current_loss -= random.uniform(0.05, 0.15)
            current_val_acc += random.uniform(0.03, 0.05)
            
        # Clamp
        current_loss = max(0.1, current_loss)
        current_val_acc = min(0.99, max(0.0, current_val_acc))

        # 2. Call the monitor
        state = monitor.step(epoch, current_loss, current_val_acc)
        
        # 3. Log
        print(
            f"[Epoch {epoch:02d}] Loss={current_loss:.3f} | Val={current_val_acc:.3f} || "
            f"CRQ={state.crq:.2f} SCP={state.scp:.2f} -> [{state.status}]"
        )
        
        # 4. Actions
        if state.action == "REDUCE_LR":
            lr *= 0.5
            print(f"    >>> Synkyria: Reducing LR to {lr:.6f} (Therapeutic Action).")
        
        if state.action == "STOP":
            print("    >>> FAILURE: Companion panicked and killed a recoverable run! (False Positive)")
            break
            
        # Success check
        if epoch == 15 and state.status == "HEALTHY":
            print("    >>> SUCCESS: Synkyria recognised the recovery and released the hold!")

        time.sleep(0.2)


if __name__ == "__main__":
    simulate_transformer_recovery()
