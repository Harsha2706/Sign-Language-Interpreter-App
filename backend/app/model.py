import torch
import torch.nn as nn
import torch.nn.functional as F

class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super(Attention, self).__init__()
        self.attn = nn.Linear(hidden_dim, 1, bias=True)

    def forward(self, x):
        # x is (batch, seq_len, hidden_dim)
        scores = self.attn(x).squeeze(-1)  # (batch, seq_len)
        alpha = F.softmax(scores, dim=-1)  # (batch, seq_len)
        context = torch.bmm(alpha.unsqueeze(1), x).squeeze(1)  # (batch, hidden_dim)
        return context

class SignLanguageModel(nn.Module):
    def __init__(self, input_dim=258, num_classes=37):
        super(SignLanguageModel, self).__init__()
        
        # CNN layers
        # In PyTorch, Conv1d expects (batch_size, in_channels, seq_len)
        self.cnn = nn.Sequential(
            nn.Conv1d(in_channels=input_dim, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, padding=1),
            nn.ReLU()
        )
        
        # BiLSTM layer
        # expects (batch, seq_len, input_size) if batch_first=True
        self.bilstm = nn.LSTM(input_size=64, hidden_size=128, num_layers=1, 
                              batch_first=True, bidirectional=True)
        
        # Attention
        self.attention = Attention(hidden_dim=256) # 128 * 2 for bidirectional
        
        # Fully connected layer
        self.fc = nn.Linear(256, num_classes)

    def forward(self, x):
        # x input shape: (batch, seq_len, input_dim)
        
        # Conv1d expects (batch, channels, seq_len)
        x = x.transpose(1, 2)
        
        c = self.cnn(x)
        
        # LSTM expects (batch, seq_len, channels)
        c = c.transpose(1, 2)
        
        out, _ = self.bilstm(c)
        
        context = self.attention(out)
        
        logits = self.fc(context)
        return logits
