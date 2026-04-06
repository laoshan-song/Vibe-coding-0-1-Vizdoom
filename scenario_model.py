import torch
import torch.nn as nn


class BCAgent(nn.Module):
    def __init__(self, obs_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, action_dim),
        )

    def forward(self, x):
        return self.net(x)


def load_bc_model(model_path, device):
    payload = torch.load(model_path, map_location=device)
    model = BCAgent(payload['obs_dim'], payload['action_dim']).to(device)
    model.load_state_dict(payload['state_dict'])
    model.eval()
    return model
