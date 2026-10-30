import torch
import torch.nn as nn
import torch.nn.functional as F

class TextEngine(nn.Module):
    """
    Simulates the ClinicalBERT Text Engine.
    In a full production setting, this would be a HuggingFace Transformer.
    Here we use a simple Embedding + LSTM/AvgPool for efficiency in the demo.
    """
    def __init__(self, vocab_size, embed_dim=128, output_dim=64, use_llm_emb=False, llm_dim=1536):
        super(TextEngine, self).__init__()
        self.use_llm_emb = use_llm_emb
        
        if use_llm_emb:
            # Input is already a 1536-d float vector
            self.projector = nn.Linear(llm_dim, output_dim)
        else:
            self.embedding = nn.Embedding(vocab_size, embed_dim)
            # Simple attention or pooling
            self.encoder = nn.LSTM(embed_dim, output_dim, batch_first=True)
            self.fc = nn.Linear(output_dim, output_dim)
        
    def forward(self, x):
        if self.use_llm_emb:
            # x: [batch, llm_dim]
            # Simple projection + ReLU
            return F.relu(self.projector(x))
        else:
            # x: [batch, max_len]
            embedded = self.embedding(x) # [batch, seq_len, embed_dim]
            _, (hn, cn) = self.encoder(embedded)
            # Use final hidden state as text summary
            return self.fc(hn[-1]) # [batch, output_dim]

class TimeSeriesEngine(nn.Module):
    """
    LSTM/GRU based engine for longitudinal lab values.
    """
    def __init__(self, input_dim=5, hidden_dim=64, num_layers=2):
        super(TimeSeriesEngine, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, hidden_dim)
        
    def forward(self, x):
        # x: [batch, seq_len(7), input_dim(5)]
        out, _ = self.lstm(x)
        # We can take the last state, or the full sequence for the Fusion module?
        # HyCF-TFM Paper says: "Transformer... using Self-Attention across time steps and modalities"
        # So we might want to project the time-series features to a common embedding space.
        return self.fc(out[:, -1, :]) # Taking last state for simplicity in this version, 
                                      # or we can return the whole sequence `out` if fusion handles time steps.

class ImageEngine(nn.Module):
    """
    Projector for pre-extracted ResNet features.
    """
    def __init__(self, input_dim=2048, output_dim=64):
        super(ImageEngine, self).__init__()
        self.fc = nn.Linear(input_dim, output_dim)
        
    def forward(self, x):
        return F.relu(self.fc(x))

class HyCF_TFM(nn.Module):
    """
    The complete Multimodal Fusion Framework.
    """
    def __init__(self, text_vocab_size, time_series_dim=5, img_feat_dim=2048, fusion_dim=64, use_llm_emb=False, llm_dim=1536):
        super(HyCF_TFM, self).__init__()
        
        self.text_engine = TextEngine(text_vocab_size, output_dim=fusion_dim, use_llm_emb=use_llm_emb, llm_dim=llm_dim)
        self.ts_engine = TimeSeriesEngine(input_dim=time_series_dim, hidden_dim=fusion_dim)
        self.img_engine = ImageEngine(input_dim=img_feat_dim, output_dim=fusion_dim)
        
        # Longitudinal Fusion Module (Transformer Encoder)
        # We treat each modality as a "token" in the sequence given to the Transformer.
        # Token 1: Text Summary
        # Token 2: Image Summary
        # Token 3: Time Series Summary
        # (Simplified Fusion)
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=fusion_dim, nhead=4, batch_first=True)
        self.fusion_module = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        self.classifier = nn.Sequential(
            nn.Linear(fusion_dim * 3, 32), # Concat output of 3 tokens
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
    def forward(self, text_x, ts_x, img_x):
        # 1. Extract Features
        text_emb = self.text_engine(text_x) # [batch, fusion_dim]
        ts_emb = self.ts_engine(ts_x)       # [batch, fusion_dim]
        img_emb = self.img_engine(img_x)    # [batch, fusion_dim]
        
        # 2. Stack as sequence -> [batch, 3, fusion_dim]
        fusion_input = torch.stack([text_emb, ts_emb, img_emb], dim=1)
        
        # 3. Transformer Fusion
        fusion_out = self.fusion_module(fusion_input) # [batch, 3, fusion_dim]
        
        # 4. Flatten and Classify
        # Alternatively, use a CLS token or AvgPool
        flat = fusion_out.view(fusion_out.size(0), -1)
        return self.classifier(flat)
