import numpy as np
import torch
import torch.nn as nn
import pandas as pd
import time


from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tempfile import TemporaryDirectory

class FineTuneDataset(Dataset):
    """Class object used to prepare Sentinel-2 data for ResNet18 fine-tuning.

    The class wraps the Sentinel-2 image data and corresponding wildfire labels
    already loaded into memory. This allows the observations to be passed to a
    `DataLoader` for batch generation during model training and validation.

    Args:
        X (np.ndarray): Sentinel-2 image data with shape `(n_samples, height, width, channels)`
        y (np.ndarray): Binary wildfire labels corresponding to each observation
    """    
    def __init__(self, X, y):
       
        self.X = X
        self.y = y

    def __len__(self):
        """Returns the number of observations in the dataset"""
        return len(self.X)

    def __getitem__(self, idx):
        """Retrieves a single Sentinel-2 observation and its corresponding label

        Args:
            idx (int): Index of the observation to retrieve

        Returns:
            tuple:
                - Image data for a single Sentinel-2 observation
                - Binary wildfire label associated with the image
        """
        pixel_data = torch.from_numpy(self.X[idx]).permute(2,0,1)
        fire_label = torch.tensor(int(self.y[idx]), dtype=torch.long)
        return pixel_data, fire_label

# def fine_tune_resnet18(model, criterion, optimizer, scheduler, num_epochs = 25, weights_fname = "test_resnet18.pt"):
#     start = time.time()
#     with TemporaryDirectory() as tempdir:
#         best_model_params_path = DATA_DIR/"MLModels"/weights_fname
#         torch.save(model.state_dict(), best_model_params_path)
#         best_f1 = 0.0

#         for epoch in range(num_epochs):
#             print(f'Epoch {epoch}/{num_epochs - 1}')
#             print('-' * 10)

#             # Train and validation phases
#             for phase in ['train', 'validate']:
#                 if phase == 'train':
#                     # Set model to training mode
#                     model.train() 
#                 else:
#                     # Evaluate the model
#                     model.eval()
#                 running_loss = 0.0
#                 running_correct = 0

#                 # Iterate over data.
#                 for inputs, labels in dataloaders[phase]:
#                     inputs = inputs.to(device)
#                     labels = labels.to(device)

#                     # zero the parameter gradients
#                     optimizer.zero_grad()

#                     # forward
#                     # track history if only in train
#                     with torch.set_grad_enabled(phase == 'train'):
#                         outputs = model(inputs)
#                         _, preds = torch.max(outputs, 1)
#                         loss = criterion(outputs, labels)

#                         # backward + optimize only if in training phase
#                         if phase == 'train':
#                             loss.backward()
#                             optimizer.step()

#                     # statistics
#                     running_loss += loss.item() * inputs.size(0)
#                     running_corrects += torch.sum(preds == labels.data)
#                 if phase == 'train':
#                     scheduler.step()

#                 epoch_loss = running_loss / dataset_sizes[phase]
#                 epoch_acc = running_corrects.double() / dataset_sizes[phase]

#                 print(f'{phase} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')

#                 # deep copy the model
#                 if phase == 'val' and epoch_acc > best_f1:
#                     best_acc = epoch_acc
#                     torch.save(model.state_dict(), best_model_params_path)

#             print()

#         time_elapsed = time.time() - start
#         print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
#         print(f'Best val Acc: {best_f1:4f}')

#         # load best model weights
#         model.load_state_dict(torch.load(best_model_params_path, weights_only=True))
#     return model
