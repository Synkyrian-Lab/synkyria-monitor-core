from synkyria import SynkyriaMonitor

monitor = SynkyriaMonitor()
state = monitor.step(epoch=1, train_loss=2.5, val_acc=0.1)

print("✅ SUCCESS: The Synkyria Library is installed and importing correctly!")
print(f"   Monitor Status: {state.status}")
print(f"   CRQ: {state.crq}")
print("🚀 Ready for production use.")
