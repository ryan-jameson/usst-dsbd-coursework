import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.metrics import roc_auc_score, f1_score, average_precision_score
import numpy as np
import os
from tqdm import tqdm

from src.dataset import MultimodalDataset, build_vocab
from src.models import HyCF_TFM

def train_model(data_dir='data', epochs=10, batch_size=32, lr=1e-3):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # 1. Prepare Data
    print("Building Vocabulary...")
    vocab = build_vocab(data_dir)
    print(f"Vocab Size: {len(vocab)}")
    
    train_dataset = MultimodalDataset(data_dir, split='train', vocab=vocab)
    val_dataset = MultimodalDataset(data_dir, split='test', vocab=vocab) # Use test as val for demo
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 2. Init Model
    model = HyCF_TFM(
        text_vocab_size=len(vocab),
        time_series_dim=5,
        img_feat_dim=2048
    ).to(device)
    
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # 3. Training Loop
    best_auc = 0
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in loop:
            text, ts, img, label = [x.to(device) for x in batch]
            
            optimizer.zero_grad()
            output = model(text, ts, img)
            loss = criterion(output, label)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            loop.set_postfix(loss=loss.item())
            
        # 4. Validation
        val_metrics = evaluate(model, val_loader, device)
        print(f"Epoch {epoch+1} Results:")
        print(f"Train Loss: {train_loss/len(train_loader):.4f}")
        print(f"Val AUC: {val_metrics['auc']:.4f} | F1: {val_metrics['f1']:.4f} | AUPRC: {val_metrics['auprc']:.4f}")
        
        if val_metrics['auc'] > best_auc:
            best_auc = val_metrics['auc']
            torch.save(model.state_dict(), 'best_model.pth')
            print("Saved Best Model!")

def evaluate(model, loader, device):
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for batch in loader:
            text, ts, img, label = [x.to(device) for x in batch]
            output = model(text, ts, img)
            all_preds.extend(output.cpu().numpy())
            all_targets.extend(label.cpu().numpy())
            
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    
    try:
        auc = roc_auc_score(all_targets, all_preds)
        auprc = average_precision_score(all_targets, all_preds)
        
        # Threshold for F1
        preds_binary = (all_preds > 0.5).astype(int)
        f1 = f1_score(all_targets, preds_binary)
    except Exception as e:
        print(f"Metric calculation error: {e}")
        auc, f1, auprc = 0, 0, 0
        
    return {'auc': auc, 'f1': f1, 'auprc': auprc}

if __name__ == "__main__":
    train_model()
