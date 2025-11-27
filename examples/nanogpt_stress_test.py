import time
import random
from synkyria import SynkyriaMonitor


def simulate_transformer_training():
    print("=== Synkyrian Pilot: NanoGPT Architecture ===")
    print("Starting training run... (Simulated Hardware: NVIDIA A100)")
    
    # Initialise the Synkyria stability companion
    monitor = SynkyriaMonitor()
    
    # Training parameters
    lr = 0.001
    current_val_acc = 0.10
    current_loss = 2.5
    
    for epoch in range(1, 21):
        # 1. Simulate training dynamics
        is_stressed = epoch >= 10  # data poisoning / stress after epoch 10
        
        if is_stressed:
            current_loss += random.uniform(0.05, 0.2)
            current_val_acc -= random.uniform(0.01, 0.05)
        else:
            current_loss -= random.uniform(0.05, 0.1)
            current_val_acc += random.uniform(0.02, 0.04)
            
        # Clamp values
        current_loss = max(0.1, current_loss)
        current_val_acc = min(0.99, max(0.0, current_val_acc))

        # 2. Call the monitor (your product)
        state = monitor.step(epoch, current_loss, current_val_acc)
        
        # 3. Log output
        print(
            f"[Epoch {epoch:02d}] Loss={current_loss:.3f} | Val={current_val_acc:.3f} || "
            f"CRQ={state.crq:.2f} SCP={state.scp:.2f} -> [{state.status}]"
        )
        
        # 4. Apply suggested actions
        if state.action == "REDUCE_LR":
            lr *= 0.5
            print(f"    >>> Synkyria: Reducing LR to {lr:.6f} to stabilise the field.")
        
        if state.action == "STOP":
            print("    >>> Synkyria: HARD STOP triggered. Run is structurally doomed.")
            print(f"    >>> SAVINGS: Saved {20 - epoch} epochs of compute time.")
            break
            
        time.sleep(0.2)


if __name__ == "__main__":
    simulate_transformer_training()
