import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_generator import generate_synthetic_data
from src.train import train_model

def main():
    print("=== HyCF-TFM Experiment Start ===")
    
    # 1. Generate Data if not exists
    if not os.path.exists('data/clinical_data.csv'):
        print("Dataset not found. Generating synthetic data...")
        generate_synthetic_data(num_samples=1000)
    else:
        print("Dataset found. Skipping generation.")
        
    # 2. Train Model
    print("Starting Training...")
    train_model(data_dir='data', epochs=5)

if __name__ == "__main__":
    main()
