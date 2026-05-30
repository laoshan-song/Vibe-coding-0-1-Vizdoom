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
    parser.add_argument('--val-split', type=float, default=0.2)
    parser.add_argument('--patience', type=int, default=5, help='Early stopping patience (0 to disable)')
    parser.add_argument('--cpu', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    spec = get_scenario_spec(args.scenario)
    if spec.pipeline != 'teacher_bc_ppo':
        raise ValueError(f'scenario={args.scenario} uses {spec.pipeline}, BC is not the primary path')
    if not 0.0 <= args.val_split < 1.0:
        raise ValueError('--val-split must be in the range [0.0, 1.0)')

    dataset_path = Path(args.dataset or default_demo_path(args.scenario))
    model_path = Path(args.model_path or default_bc_path(args.scenario))
    device = torch.device('cpu' if args.cpu or not torch.cuda.is_available() else 'cuda')

    data = np.load(dataset_path)
    observations = torch.tensor(data['observations'], dtype=torch.float32)
    actions = torch.tensor(data['actions'], dtype=torch.long)
    obs_dim = observations.shape[1]
    action_dim = int(actions.max().item()) + 1

    n_total = len(observations)
    if n_total < 1:
        raise ValueError(f'dataset={dataset_path} does not contain any observations')
    n_val = int(n_total * args.val_split)
    n_train = n_total - n_val

    indices = torch.randperm(n_total)
    train_idx = indices[:n_train]
    val_idx = indices[n_train:]

    train_obs, train_actions = observations[train_idx], actions[train_idx]
    val_obs, val_actions = observations[val_idx], actions[val_idx]
    has_validation = n_val > 0

    model = BCAgent(obs_dim, action_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = torch.nn.CrossEntropyLoss()

    train_loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(train_obs, train_actions),
        batch_size=args.batch_size,
        shuffle=True,
    )

    best_val_loss = float('inf')
    best_state = None
    patience_counter = 0

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        train_correct = 0
        for batch_obs, batch_actions in train_loader:
            batch_obs = batch_obs.to(device)
            batch_actions = batch_actions.to(device)
            logits = model(batch_obs)
            loss = criterion(logits, batch_actions)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_loss += float(loss.item()) * batch_actions.size(0)
            train_correct += int((logits.argmax(dim=1) == batch_actions).sum().item())

        train_loss /= n_train
        train_acc = train_correct / n_train

        model.eval()
        if has_validation:
            with torch.no_grad():
                val_actions_device = val_actions.to(device)
                val_logits = model(val_obs.to(device))
                val_loss = float(criterion(val_logits, val_actions_device).item())
                val_acc = int((val_logits.argmax(dim=1) == val_actions_device).sum().item()) / n_val

            print(
                f'epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f} '
                f'val_loss={val_loss:.4f} val_acc={val_acc:.4f}'
            )
            monitor_loss = val_loss
        else:
            print(f'epoch={epoch} train_loss={train_loss:.4f} train_acc={train_acc:.4f}')
            monitor_loss = train_loss

        if monitor_loss < best_val_loss:
            best_val_loss = monitor_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        elif args.patience > 0:
            patience_counter += 1
            if patience_counter >= args.patience:
                metric_name = 'val_loss' if has_validation else 'train_loss'
                print(f'early stopping at epoch={epoch} (best {metric_name}={best_val_loss:.4f})')
                break

    if best_state is not None:
        model.load_state_dict(best_state)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({'obs_dim': obs_dim, 'action_dim': action_dim, 'state_dict': model.state_dict()}, model_path)
    metric_name = 'val_loss' if has_validation else 'train_loss'
    print(f'saved bc model to {model_path} {metric_name}={best_val_loss:.4f}')


if __name__ == '__main__':
    main()
