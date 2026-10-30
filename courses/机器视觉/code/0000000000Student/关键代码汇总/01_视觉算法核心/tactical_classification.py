import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import json
import os

class TemporalGCN(nn.Module):
    def __init__(self, input_dim=6, hidden_dim=64, output_dim=9, num_nodes=23, num_frames=16):
        super().__init__()
        self.num_nodes = num_nodes
        self.num_frames = num_frames
        
        self.gcn_linear = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        self.transformer_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_dim * num_nodes,
                nhead=4,
                dim_feedforward=hidden_dim * 4,
                dropout=0.3,
                batch_first=True
            ),
            num_layers=2
        )
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * num_nodes, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, output_dim)
        )
    
    def _compute_adjacency(self, features):
        positions = features[:, :, :2]
        batch_size, num_nodes, _ = positions.shape
        
        dist_matrix = torch.cdist(positions, positions)
        adj_matrix = torch.exp(-dist_matrix / 10.0)
        
        mask = torch.eye(num_nodes, device=features.device).unsqueeze(0).expand(batch_size, -1, -1)
        adj_matrix = adj_matrix * (1 - mask)
        
        row_sum = adj_matrix.sum(dim=-1, keepdim=True) + 1e-6
        adj_matrix = adj_matrix / row_sum
        
        return adj_matrix
    
    def forward(self, x):
        batch_size, num_frames, num_nodes, input_dim = x.shape
        
        gcn_outputs = []
        for t in range(num_frames):
            frame_features = x[:, t, :, :]
            adj_matrix = self._compute_adjacency(frame_features)
            gcn_out = self.gcn_linear(frame_features)
            gcn_out = torch.matmul(adj_matrix, gcn_out)
            gcn_outputs.append(gcn_out)
        
        sequence = torch.stack(gcn_outputs, dim=1)
        sequence_flat = sequence.view(batch_size, num_frames, -1)
        
        transformer_out = self.transformer_encoder(sequence_flat)
        
        global_feature = transformer_out[:, -1, :]
        logits = self.classifier(global_feature)
        
        return logits

class TacticalDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return torch.tensor(self.features[idx], dtype=torch.float32), \
               torch.tensor(self.labels[idx], dtype=torch.long)

class TacticalClassifier:
    def __init__(self, model_path=None):
        self.tactical_classes = [
            '阵地进攻', '快速反击', '边路进攻', '中路渗透',
            '阵地防守', '收缩防守', '高位逼抢',
            '定位球', '死球'
        ]
        self.model = TemporalGCN()
        
        if model_path and os.path.exists(model_path):
            if torch.cuda.is_available():
                self.model.load_state_dict(torch.load(model_path))
            else:
                self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
        
        self.model.eval()
        self._is_trained = model_path is not None and os.path.exists(model_path)

    def load_model(self, model_path):
        if model_path and os.path.exists(model_path):
            if torch.cuda.is_available():
                self.model.load_state_dict(torch.load(model_path))
            else:
                self.model.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.model.eval()
            self._is_trained = True

    def train_on_mock(self, num_samples=200, epochs=3, batch_size=8, lr=1e-4):
        """Convenience method: generate mock data and perform short training to calibrate classifier."""
        features, labels = generate_mock_data(num_samples)
        self.train(features, labels, epochs=epochs, batch_size=batch_size, lr=lr)
        # mark as trained
        self._is_trained = True
        # save a quick checkpoint
        try:
            os.makedirs('../outputs', exist_ok=True)
            self.save_model('../outputs/tactical_classifier_calibrated.pt')
        except Exception:
            pass
    
    def train(self, train_features, train_labels, val_features=None, val_labels=None, 
              epochs=50, batch_size=8, lr=1e-4):
        
        train_dataset = TacticalDataset(train_features, train_labels)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        if val_features is not None and val_labels is not None:
            val_dataset = TacticalDataset(val_features, val_labels)
            val_loader = DataLoader(val_dataset, batch_size=batch_size)
        else:
            val_loader = None
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0
            
            for features, labels in train_loader:
                optimizer.zero_grad()
                outputs = self.model(features)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            avg_train_loss = train_loss / len(train_loader)
            
            if val_loader:
                self.model.eval()
                val_loss = 0.0
                correct = 0
                
                with torch.no_grad():
                    for features, labels in val_loader:
                        outputs = self.model(features)
                        loss = criterion(outputs, labels)
                        val_loss += loss.item()
                        preds = torch.argmax(outputs, dim=1)
                        correct += (preds == labels).sum().item()
                
                avg_val_loss = val_loss / len(val_loader)
                val_acc = correct / len(val_loader.dataset)
                
                print(f'Epoch {epoch+1}/{epochs} | Train Loss: {avg_train_loss:.4f} | '
                      f'Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.4f}')
            else:
                print(f'Epoch {epoch+1}/{epochs} | Train Loss: {avg_train_loss:.4f}')
            
            scheduler.step()
    
    def predict(self, features, mc_dropout=False, mc_samples=8, temperature=1.0):
        """
        Predict with optional MC-dropout uncertainty and temperature scaling.
        - features: sequence input (num_frames, num_nodes, dim) or list-like
        - mc_dropout: if True, perform multiple stochastic forward passes with dropout enabled
        - mc_samples: number of stochastic samples
        - temperature: float >0 for temperature scaling (1.0 = no scaling)
        """
        self.model.eval()

        import numpy as _np
        arr = _np.array(features, dtype=float)
        # Expect shape either (num_frames, num_nodes, dim) or (batch, num_frames, num_nodes, dim)
        if arr.ndim == 3:
            inputs = torch.tensor(arr, dtype=torch.float32).unsqueeze(0)
        elif arr.ndim == 4:
            inputs = torch.tensor(arr, dtype=torch.float32)
        else:
            # try to flatten/reshape conservatively to (1, num_frames, num_nodes, dim)
            raise ValueError(f'Unsupported feature shape: {arr.shape}')

        if mc_dropout:
            # enable dropout during inference
            self.model.train()
            probs = []
            with torch.no_grad():
                for _ in range(mc_samples):
                    out = self.model(inputs)
                    logits = out / float(max(temperature, 1e-6))
                    p = F.softmax(logits, dim=1)
                    probs.append(p.cpu().numpy())
            probs = np.mean(np.vstack(probs), axis=0)
            # set back to eval
            self.model.eval()
        else:
            with torch.no_grad():
                out = self.model(inputs)
                logits = out / float(max(temperature, 1e-6))
                probs = F.softmax(logits, dim=1).cpu().numpy()

        probs = probs[0]
        predicted_idx = int(np.argmax(probs))

        return {
            'tactical_class': self.tactical_classes[predicted_idx],
            'class_index': predicted_idx,
            'probabilities': {cls: float(p) for cls, p in zip(self.tactical_classes, probs.tolist())}
        }
    
    def save_model(self, model_path):
        torch.save(self.model.state_dict(), model_path)

def generate_mock_data(num_samples=100):
    features = []
    labels = []
    
    for _ in range(num_samples):
        sequence = []
        for _ in range(16):
            nodes = []
            for _ in range(23):
                node = [
                    np.random.uniform(0, 105),
                    np.random.uniform(0, 68),
                    np.random.uniform(0, 30),
                    np.random.uniform(-np.pi, np.pi),
                    np.random.randint(0, 2),
                    np.random.uniform(0, 1)
                ]
                nodes.append(node)
            sequence.append(nodes)
        features.append(sequence)
        labels.append(np.random.randint(0, 9))
    
    return features, labels

def main():
    classifier = TacticalClassifier()
    
    features, labels = generate_mock_data(100)
    
    train_features, val_features = features[:80], features[80:]
    train_labels, val_labels = labels[:80], labels[80:]
    
    print("Starting training...")
    classifier.train(train_features, train_labels, val_features, val_labels, epochs=10)
    
    classifier.save_model('../outputs/tactical_classifier.pt')
    print("Model saved!")
    
    test_sample = features[90]
    prediction = classifier.predict(test_sample)
    print("\nPrediction:")
    print(json.dumps(prediction, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()