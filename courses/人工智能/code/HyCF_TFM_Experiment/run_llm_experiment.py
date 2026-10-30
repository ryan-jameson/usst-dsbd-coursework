import os
import torch
import numpy as np
import pandas as pd
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
import torch.nn as nn
import torch.optim as optim

from src.models import HyCF_TFM
from src.llm_utils import get_embeddings_batch, generate_report
from src.data_generator import generate_synthetic_data

def prepare_llm_data(data_dir, num_samples=50):
    """
    Generates a small dataset and pre-computes LLM embeddings.
    """
    # 1. Generate Raw Data
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    print(f"Generating {num_samples} samples for LLM experiment...")
    # Using existing generator but outputting to a separate folder so we don't mess up the main one
    generate_synthetic_data(num_samples=num_samples, output_dir=data_dir)
    
    # 2. Load and Compute Embeddings
    df = pd.read_csv(os.path.join(data_dir, 'clinical_data.csv'))
    texts = df['text'].tolist()
    
    print("Fetching OpenAI Embeddings (this may take a moment)...")
    embeddings = get_embeddings_batch(texts, batch_size=10) # List of lists
    
    # Save embeddings
    emb_path = os.path.join(data_dir, 'llm_embeddings.npy')
    np.save(emb_path, np.array(embeddings))
    print(f"Embeddings saved to {emb_path}")
    
    return df, np.array(embeddings)

def load_processed_data(data_dir):
    df = pd.read_csv(os.path.join(data_dir, 'clinical_data.csv'))
    ts_df = pd.read_csv(os.path.join(data_dir, 'lab_vitals_ts.csv'))
    embeddings = np.load(os.path.join(data_dir, 'llm_embeddings.npy'))
    
    # Process Time Series per patient
    ts_data = []
    patient_ids = df['patient_id'].tolist()
    
    patient_ts_map = ts_df.groupby('patient_id')
    
    for pid in patient_ids:
        group = patient_ts_map.get_group(pid).sort_values('day')
        vals = group[['BNP', 'Creatinine', 'Sodium', 'HR', 'SBP']].values
        ts_data.append(vals)
        
    ts_data = np.array(ts_data)
    
    # Load Images
    img_data = []
    for img_path in df['img_path']:
        full_path = os.path.join(data_dir, img_path)
        img_data.append(np.load(full_path))
    img_data = np.array(img_data)
    
    labels = df['label'].values
    
    return df, embeddings, ts_data, img_data, labels

def train_and_predict():
    DIR = 'data_llm'
    
    # 1. Prepare Data (Train + Test combined generation, we split manually)
    if not os.path.exists(DIR) or not os.path.exists(os.path.join(DIR, 'llm_embeddings.npy')):
        prepare_llm_data(DIR, num_samples=55) # 50 train, 5 test
        
    df, texts_emb, ts_data, img_data, labels = load_processed_data(DIR)
    
    # Convert to Tensors
    X_text = torch.tensor(texts_emb, dtype=torch.float32)
    X_ts = torch.tensor(ts_data, dtype=torch.float32)
    X_img = torch.tensor(img_data, dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)
    
    # Split
    train_size = 50
    X_text_train, X_text_test = X_text[:train_size], X_text[train_size:]
    X_ts_train, X_ts_test = X_ts[:train_size], X_ts[train_size:]
    X_img_train, X_img_test = X_img[:train_size], X_img[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    test_df = df.iloc[train_size:].reset_index(drop=True)
    
    # 2. Model Setup (use_llm_emb=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = HyCF_TFM(
        text_vocab_size=0, # Not used
        use_llm_emb=True,
        llm_dim=1536
    ).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.BCELoss()
    
    # 3. Train
    print("Training HyCF-TFM with LLM Embeddings...")
    model.train()
    dataset = TensorDataset(X_text_train, X_ts_train, X_img_train, y_train)
    loader = DataLoader(dataset, batch_size=10, shuffle=True)
    
    for epoch in range(10): # 10 epochs for demo
        total_loss = 0
        for batch in loader:
            tx, ts, im, lb = [x.to(device) for x in batch]
            optimizer.zero_grad()
            out = model(tx, ts, im)
            loss = criterion(out, lb)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if (epoch+1) % 2 == 0:
            print(f"Epoch {epoch+1}, Loss: {total_loss/len(loader):.4f}")
            
    # 4. Predict & Generate Report
    print("\n=== Generating Reports for 5 Test Cases ===")
    model.eval()
    with torch.no_grad():
        preds = model(X_text_test.to(device), X_ts_test.to(device), X_img_test.to(device))
        preds = preds.cpu().numpy()
        
    reports = []
    for i in range(len(test_df)):
        row = test_df.iloc[i]
        prob = preds[i][0]
        
        # Extract basic info for prompt
        # Simulate getting trend info from raw TS array
        ts = X_ts_test[i].numpy() # (7, 5)
        latest_bnp = ts[-1, 0]
        start_bnp = ts[0, 0]
        trend = "Increasing" if latest_bnp > start_bnp + 50 else ("Decreasing" if latest_bnp < start_bnp - 50 else "Stable")
        latest_creat = ts[-1, 1]
        
        patient_info = {
            'text': row['text'],
            'latest_bnp': f"{latest_bnp:.1f}",
            'bnp_trend': trend,
            'latest_creat': f"{latest_creat:.2f}"
        }
        
        print(f"\nProcessing Patient {row['patient_id']} (Risk: {prob:.2%})...")
        report = generate_report(patient_info, prob)
        
        reports.append({
            'Patient ID': row['patient_id'],
            'Predicted Risk': f"{prob:.2%}",
            'Report': report
        })
        print(report)
        print("-" * 50)
        
    # Save Report
    report_df = pd.DataFrame(reports)
    report_df.to_csv("llm_generated_reports.csv", index=False)
    print("\nReports saved to llm_generated_reports.csv")

if __name__ == "__main__":
    train_and_predict()
