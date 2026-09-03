
from sklearn.metrics import f1_score
import torch
import torch.nn as nn
import time
import os


from torch.utils.data import Dataset, DataLoader
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

def fine_tune_resnet18(model: nn.Module, 
                       criterion: nn.Module, 
                       optimizer: torch.optim.Optimizer, 
                       scheduler, 
                       num_epochs: int, 
                       
                       dataloaders: dict[str, DataLoader], # type: ignore
                       device: str) -> nn.Module:
    """Fine-tunes a pre-trained ResNet18 model on Sentinel-2 wildfire data
    
    This module and process follows the structure and logic of the PyTorch tutorial on transfer learning:
    https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html    
    Some elements and sections of this tutorial were adapted to fit the specific requirements of this project

    The model uses F1 score instead of Accuracy, given that the dataset is imbalanced 

    Args:
        model (nn.Module): Pre-trained ResNet18 model to be fine-tuned - Uses defaults weights as starting point
        criterion (nn.Module): Loss function used for training - Quantifies the difference between the models predictions and true labels
                               for binary classificaiton, `nn.CrossEntropyLoss()` is typically used
        optimizer (torch.optim.Optimizer): Optimizer used for updating model parameters
        scheduler: Learning rate scheduler to adjust the learning rate during training
        num_epochs (int, optional): Number of epochs to train the model.
        dataloaders (dict[str, DataLoader]): Dictionary containing DataLoaders for training and validation datasets
        device (str): Device to run the training on ('cuda' or 'cpu')
    """
    # Initiliase timer to track how long training takes
    start = time.time()
    # Creates a temporary directory to store the best model parameters during training 
    # File(s) get deleted when the program exits the with block
    with TemporaryDirectory() as tempdir:
        best_model_params_path = os.path.join(tempdir, 'best_model_params.pt')
        torch.save(model.state_dict(), best_model_params_path)

        # Initialise best_f1 variable OUTSIDE the epoch loop to track the best score across all epochs
        best_f1      = 0.0

        # Loop over epochs for training and validation
        for epoch in range(num_epochs):
            print(f'Epoch {epoch}/{num_epochs - 1}')
            print('-' * 10)

            # Train and validation phases
            for phase in ['train', 'val']:
                if phase == 'train':
                    # Set model to training mode
                    model.train() 
                else:
                    # Evaluate the model
                    model.eval()
            
                # Initialize variables to track predictions, labels, and loss
                all_preds    = []
                all_labels   = []
                running_loss = 0.0

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
                        # Obtain predicted class index (0 = No fire, 1 = Fire)
                        _, preds = torch.max(outputs, 1)
                        loss = criterion(outputs, labels)

                        # backward + optimize only if in training phase
                        if phase == 'train':
                            loss.backward()
                            optimizer.step()

                    # Accumulate statistics
                    running_loss += loss.item() * inputs.size(0) 
                    all_preds.extend(preds.cpu().numpy())
                    all_labels.extend(labels.cpu().numpy())

                if phase == 'train':
                    scheduler.step()

                # Accumulate batch loss scaled by batch size so that an average loss
                # across the entire dataset can be calculated at the end of the epoch
                epoch_loss = running_loss / len(dataloaders[phase].dataset) # type: ignore
                # Calculate F1 score
                epoch_f1 = f1_score(all_labels, all_preds, average='macro')

                print(f'{phase} Loss: {epoch_loss:.4f} F1 Score: {epoch_f1:.4f}')

                # deep copy the model
                if phase == 'val' and epoch_f1 > best_f1:
                    best_f1 = epoch_f1
                    torch.save(model.state_dict(), best_model_params_path)

        time_elapsed = time.time() - start
        print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'Best val F1 Score: {best_f1:4f}')

        # load best model weights
        model.load_state_dict(torch.load(best_model_params_path, weights_only=True))
    return model
