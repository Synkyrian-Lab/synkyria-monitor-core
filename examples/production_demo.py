import time
import random
from synkyria import SynkyriaMonitor


def run_enterprise_simulation():
    print("\n==================================================")
    print("   🛡️  SYNKYRIA ENTERPRISE PROTECTION LIVE DEMO   ")
    print("==================================================\n")
    print("scenario_type: 'Zombie Run' Detection")
    print("hardware_sim:  Multi-Node GPU Cluster ($120/hour)")
    print("--------------------------------------------------")
    
    # Call the Synkyria monitor from the installed library
    monitor = SynkyriaMonitor()
    
    # Simulated training parameters
    lr = 0.001
    current_val_acc = 0.10
    current_loss = 2.5
    
    # Run for up to 20 epochs
    for epoch in range(1, 21):
        # --- PHYSICS SIMULATION ---
        # From Epoch 6 onwards the model suffers a permanent failure (collapse)
        if epoch >= 6:
            current_loss += random.uniform(0.4, 0.8)       # Loss goes up
            current_val_acc = max(0.05, current_val_acc - 0.05)  # Accuracy drops
            simulated_event = "[!] MODEL COLLAPSE (Gradient Explosion)"
        else:
            current_loss -= 0.10
            current_val_acc += 0.04
            simulated_event = "Normal Training..."
        
        # --- SYNKYRIA INTERVENTION (The Product) ---
        # This line is the core API call:
        state = monitor.step(epoch, current_loss, current_val_acc)
        
        # --- DASHBOARD OUTPUT ---
        print(
            f"EPOCH {epoch:02d} | Loss: {current_loss:.2f} | Acc: {current_val_acc:.2f} | "
            f"Event: {simulated_event}"
        )
        
        print(
            f"   └── [Synkyria Monitor] Status: {state.status} "
            f"(CRQ: {state.crq:.2f} | SCP: {state.scp:.2f})"
        )

        # --- ACTIONS ---
        if state.action == "REDUCE_LR":
            print("       >>> ⚠️  THERAPY APPLIED: Reducing learning rate...")
        
        if state.action == "STOP":
            print("\n🛑 EMERGENCY STOP TRIGGERED BY SYNKYRIA 🛑")
            print("   REASON: Structural collapse confirmed (SCP < 0.30).")
            print(f"   VALUE:  Prevented {20 - epoch} epochs of wasted compute.")
            print("   SAVINGS: Estimated $1,680 (assuming cluster cost).")
            break  # Stop the run here
        
        print("-" * 50)
        time.sleep(0.4)  # Slow down a bit so humans can read


if __name__ == "__main__":
    run_enterprise_simulation()
