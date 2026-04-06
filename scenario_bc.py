import argparse
from pathlib import Path

import numpy as np
import torch

from scenario_model import BCAgent
from scenario_catalog import default_bc_path, default_demo_path, get_scenario_spec, list_scenarios


def parse_args():
    parser = argparse.ArgumentParser(description='Train a BC model for a built-in scenario.')
    parser.add_argument('--scenario', choices=list_scenarios(), required=True)
    parser.add_argument('--dataset', default=None)
    parser.add_argument('--model-path', default=None)
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--batch-size', type=int, default=512)
    parser.add_argument('--learning-rate', type=float, default=1e-3)
    parser.add_argument('--cpu', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    if spec.pipeline != 'teacher_bc_ppo':
        raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, BC is not the primary path')

    dataset_path = Path(args.dataset or default_demo_path(args.scenario))
    model_path = Path(args.model_path or default_bc_path(args.scenario))
    device = torch.device('cpu' if args.cpu or not torch.cuda.is_available() else 'cuda')

    data = np.load(dataset_path)
    observations = torch.tensor(data['observations'], dtype=torch.float32)
    actions = torch.tensor(data['actions'], dtype=torch.long)
    obs_dim = observations.shape[1]
    action_dim = int(actions.max().item()) + 1

    model = BCAgent(obs_dim, action_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = torch.nn.CrossEntropyLoss()
    loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(observations, actions),
        batch_size=args.batch_size,
        shuffle=True,
    )

    for epoch in range(1, args.epochs + 1):
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        model.train()
        for batch_obs, batch_actions in loader:
            batch_obs = batch_obs.to(device)
            batch_actions = batch_actions.to(device)
            logits = model(batch_obs)
            loss = criterion(logits, batch_actions)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * batch_actions.size(0)
            total_correct += int((logits.argmax(dim=1) == batch_actions).sum().item())
            total_samples += batch_actions.size(0)
        print(
            f'epoch={epoch} loss={total_loss / total_samples:.4f} '
            f'accuracy={total_correct / total_samples:.4f}'
        )

    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'obs_dim': obs_dim, 'action_dim': action_dim, 'state_dict': model.state_dict()}, model_path)
    print(f'saved bc model to {model_path}')


if __name__ == '__main__':
    main()
