# src/model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, lstm_out):
        attn_weights = torch.softmax(self.attn(lstm_out), dim=1)
        context = torch.sum(attn_weights * lstm_out, dim=1)
        return context

class SignLanguageModel(nn.Module):
    def __init__(self, input_dim, num_classes, cnn_channels=64, lstm_hidden=128):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(input_dim, cnn_channels, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(cnn_channels, cnn_channels, kernel_size=3, padding=1),
            nn.ReLU()
        )
        self.bilstm = nn.LSTM(cnn_channels, lstm_hidden, num_layers=1, 
                              batch_first=True, bidirectional=True)
        self.attention = Attention(lstm_hidden*2)
        self.fc = nn.Linear(lstm_hidden*2, num_classes)
        

    def forward(self, x):
        x = x.permute(0, 2, 1)  # (batch, input_dim, seq_len)
        x = self.cnn(x)
        x = x.permute(0, 2, 1)  # (batch, seq_len, cnn_channels)
        lstm_out, _ = self.bilstm(x)
        context = self.attention(lstm_out)
        out = self.fc(context)
        return F.log_softmax(out, dim=1)