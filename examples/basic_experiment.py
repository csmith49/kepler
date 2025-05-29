"""
Basic example of using the expman package with the log-based experiment model.
"""
import time
import random
import pandas as pd
from kepler import experiment, save_dataframe, save_dict

# Define experiment configuration
config = {
    "learning_rate": 0.01,
    "batch_size": 32,
    "epochs": 10,
    "optimizer": "adam",
}

# Run an experiment
with experiment("Basic Example", config=config, tags=["example", "demo"]) as exp:
    print(f"Running experiment: {exp.name} (ID: {exp.id})")
    
    # Log some information
    exp.log_info("Starting training process")
    
    # Simulate training loop
    results = []
    total_epochs = config["epochs"]
    
    for epoch in range(total_epochs):
        # Update progress
        exp.update_progress(epoch + 1, total_epochs, f"Processing epoch {epoch + 1}/{total_epochs}")
        
        # Simulate training for this epoch
        time.sleep(0.5)  # Simulate computation
        
        # Generate some fake metrics
        accuracy = 0.7 + 0.02 * epoch + random.uniform(0, 0.01)
        loss = 0.5 - 0.03 * epoch + random.uniform(0, 0.01)
        
        # Store results for this epoch
        results.append({
            "epoch": epoch + 1,
            "accuracy": accuracy,
            "loss": loss,
        })
        
        print(f"Epoch {epoch+1}/{total_epochs}: accuracy={accuracy:.4f}, loss={loss:.4f}")
        
        # Log metrics in the experiment
        exp.set_metric(f"accuracy_epoch_{epoch+1}", accuracy)
        exp.set_metric(f"loss_epoch_{epoch+1}", loss)
        
        # Log resource usage (simulated)
        exp.log_resource("memory", f"{random.randint(200, 300)}MB")
        exp.log_resource("gpu_utilization", f"{random.randint(70, 95)}%")
    
    # Log completion of training
    exp.log_info("Training completed successfully")
    
    # Create a DataFrame from the results
    results_df = pd.DataFrame(results)
    
    # Save the DataFrame
    df_path = save_dataframe(results_df, "training_metrics", exp.id)
    exp.log_info(f"Saved training metrics to {df_path}")
    
    # Save final metrics
    final_metrics = {
        "final_accuracy": results[-1]["accuracy"],
        "final_loss": results[-1]["loss"],
        "best_accuracy": max(r["accuracy"] for r in results),
        "best_epoch": max(range(len(results)), key=lambda i: results[i]["accuracy"]) + 1,
    }
    
    # Save the final metrics
    metrics_path = save_dict(final_metrics, "final_metrics", exp.id)
    exp.log_info(f"Saved final metrics to {metrics_path}")
    
    # Set the final metrics in the experiment
    for key, value in final_metrics.items():
        exp.set_metric(key, value)
    
    print(f"Experiment completed: {exp.name} (ID: {exp.id})")
    print(f"Best accuracy: {final_metrics['best_accuracy']:.4f} at epoch {final_metrics['best_epoch']}")

print("Run 'expman tui' to view the experiment in the terminal UI")
print("Or 'expman list' to see a list of experiments")
print("Or 'expman info {exp.id}' to see details of this experiment")