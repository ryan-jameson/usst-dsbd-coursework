import torch
from torch.utils.data import Dataset
import pandas as pd
import numpy as np
import os
import json

class MultimodalDataset(Dataset):
    def __init__(self, data_dir, split='train', vocab=None, max_len=50):
        """
        Args:
            data_dir: Path to generated data
            split: 'train' or 'test' (we will split the full csv inside)
            vocab: Dict mapping word -> index
            max_len: Max sequence length for text
        """
        self.data_dir = data_dir
        self.max_len = max_len
        
        # Load clinical data
        df = pd.read_csv(os.path.join(data_dir, 'clinical_data.csv'))
        
        # Load TS data
        ts_df = pd.read_csv(os.path.join(data_dir, 'lab_vitals_ts.csv'))
        
        # Simple Split (80/20) based on index
        train_len = int(0.8 * len(df))
        if split == 'train':
            self.df = df.iloc[:train_len].reset_index(drop=True)
        else:
            self.df = df.iloc[train_len:].reset_index(drop=True)
            
        self.patient_ts = ts_df.groupby('patient_id')
        self.vocab = vocab
        
    def __len__(self):
        return len(self.df)
    
    def tokenize(self, text):
        words = text.lower().replace('.', '').replace(',', '').split()
        indices = [self.vocab.get(w, self.vocab.get('<UNK>', 1)) for w in words]
        
        # Pad or Truncate
        if len(indices) < self.max_len:
            indices += [self.vocab.get('<PAD>', 0)] * (self.max_len - len(indices))
        else:
            indices = indices[:self.max_len]
            
        return torch.tensor(indices, dtype=torch.long)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        pid = row['patient_id']
        
        # 1. Text
        text_tensor = self.tokenize(row['text'])
        
        # 2. Time Series
        # Extract 7x5 matrix
        ts_group = self.patient_ts.get_group(pid).sort_values('day')
        ts_vals = ts_group[['BNP', 'Creatinine', 'Sodium', 'HR', 'SBP']].values
        ts_tensor = torch.tensor(ts_vals, dtype=torch.float32)
        
        # 3. Image Features
        img_path = os.path.join(self.data_dir, row['img_path'])
        img_feat = np.load(img_path)
        img_tensor = torch.tensor(img_feat, dtype=torch.float32)
        
        # 4. Label
        label = torch.tensor([row['label']], dtype=torch.float32)
        
        return text_tensor, ts_tensor, img_tensor, label

def build_vocab(data_dir):
    df = pd.read_csv(os.path.join(data_dir, 'clinical_data.csv'))
    all_text = " ".join(df['text'].tolist())
    words = set(all_text.lower().replace('.', '').replace(',', '').split())
    
    vocab = {'<PAD>': 0, '<UNK>': 1}
    for i, w in enumerate(words):
        vocab[w] = i + 2
    return vocab
