"""
Example of running multiple experiments with different configurations.
"""
import time
import random
import itertools
import pandas as pd
from kepler import experiment, save_dataframe, save_dict

# Define parameter grid
learning_rates = [0.001, 0.01, 0.1]
batch_sizes = [16, 32, 64]
optimizers = ["adam", "sgd"]

# Generate all combinations of parameters
param_grid = list(itertools.product(learning_rates, batch_sizes, optimizers))

# Run experiments for each parameter combination
for lr, bs, opt in param_grid:
    # Define experiment configuration
    config = {
        "learning_rate": lr,
        "batch_size": bs,
        "optimizer": opt,
        "epochs": 5,
    }
    
    # Create experiment name based on parameters
    exp_name = f"Train-LR{lr}-BS{bs}-{opt.upper()}"
    
    # Run the experiment
    with experiment(exp_name, config=config, tags=["grid_search"]) as exp:
        print(f"Running experiment: {exp.name} (ID: {exp.id})")
        
        # Simulate training loop
        results = []
        for epoch in range(config["epochs"]):
            # Simulate training for this epoch
            time.sleep(0.2)  # Simulate computation
            
            # Generate some fake metrics with parameter-dependent behavior
            # Higher learning rates converge faster but might be less stable
            # Larger batch sizes might have smoother convergence
            base_accuracy = 0.7
            lr_factor = 0.1 if lr == 0.001 else 0.2 if lr == 0.01 else 0.3
            bs_factor = 0.05 if bs == 16 else 0.1 if bs == 32 else 0.15
            opt_factor = 0.1 if opt == "adam" else 0.05
            
            # Add some randomness and epoch progression
            accuracy = min(0.99, base_accuracy + lr_factor * (1 - 0.5**epoch) + 
                          bs_factor * (epoch / config["epochs"]) + 
                          opt_factor * (1 - 0.7**epoch) + 
                          random.uniform(-0.02, 0.02))
            
            loss = max(0.01, 0.5 - 0.4 * (accuracy - 0.7))
            
            # Store results for this epoch
            results.append({
                "epoch": epoch + 1,
                "accuracy": accuracy,
                "loss": loss,
            })
            
            print(f"Epoch {epoch+1}/{config['epochs']}: accuracy={accuracy:.4f}, loss={loss:.4f}")
            
            # Set metrics in the experiment
            exp.set_metric(f"accuracy_epoch_{epoch+1}", accuracy)
            exp.set_metric(f"loss_epoch_{epoch+1}", loss)
        
        # Create a DataFrame from the results
        results_df = pd.DataFrame(results)
        
        # Save the DataFrame
        save_dataframe(results_df, "training_metrics", exp.id)
        
        # Save final metrics
        final_metrics = {
            "final_accuracy": results[-1]["accuracy"],
            "final_loss": results[-1]["loss"],
            "best_accuracy": max(r["accuracy"] for r in results),
            "best_epoch": max(range(len(results)), key=lambda i: results[i]["accuracy"]) + 1,
        }
        
        # Save the final metrics
        save_dict(final_metrics, "final_metrics", exp.id)
        
        # Set the final metrics in the experiment
        for key, value in final_metrics.items():
            exp.set_metric(key, value)
        
        print(f"Experiment completed: {exp.name} (ID: {exp.id})")
        print(f"Best accuracy: {final_metrics['best_accuracy']:.4f} at epoch {final_metrics['best_epoch']}")
        print("-" * 50)

print("All experiments completed!")
print("Run 'expman tui' to view the experiments in the terminal UI")
print("Or 'expman list' to see a list of experiments")
print("Or 'expman list --sort final_accuracy --reverse' to see experiments sorted by accuracy")