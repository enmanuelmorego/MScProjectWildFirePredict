import numpy as np
import torch
import torch.nn as nn
import pandas as pd
import time

from scripts.s00_set_parameters import DATA_DIR
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tempfile import TemporaryDirectory

def fine_tune_resnet18(model, criterion, optimizer, scheduler, num_epochs = 25, weights_fname = "test_resnet18.pt"):
    start = time.time()
    with TemporaryDirectory() as tempdir:
        best_model_params_path = DATA_DIR/"MLModels"/weights_fname
        torch.save(model.state_dict(), best_model_params_path)
        best_f1 = 0.0

        for epoch in range(num_epochs):
            print(f'Epoch {epoch}/{num_epochs - 1}')
            print('-' * 10)

            # Train and validation phases
            for phase in ['train', 'validate']:
                if phase == 'train':
                    # Set model to training mode
                    model.train() 
                else:
                    # Evaluate the model
                    model.eval()
                running_loss = 0.0
                running_correct = 0

                # Iterate over data.
                for inputs, labels in dataloaders[phase]:
                    inputs = inputs.to(device)
                    labels = labels.to(device)

                    # zero the parameter gradients
                    optimizer.zero_grad()

                    # forward
                    # track history if only in train
                    with torch.set_grad_enabled(phase == 'train'):
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)

                        # backward + optimize only if in training phase
                        if phase == 'train':
                            loss.backward()
                            optimizer.step()

                    # statistics
                    running_loss += loss.item() * inputs.size(0)
                    running_corrects += torch.sum(preds == labels.data)
                if phase == 'train':
                    scheduler.step()

                epoch_loss = running_loss / dataset_sizes[phase]
                epoch_acc = running_corrects.double() / dataset_sizes[phase]

                print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

                # deep copy the model
                if phase == 'val' and epoch_acc > best_f1:
                    best_acc = epoch_acc
                    torch.save(model.state_dict(), best_model_params_path)

            print()

        time_elapsed = time.time() - start
        print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'Best val Acc: {best_f1:4f}')

        # load best model weights
        model.load_state_dict(torch.load(best_model_params_path, weights_only=True))
    return model
