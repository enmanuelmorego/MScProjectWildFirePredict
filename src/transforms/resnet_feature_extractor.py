import numpy as np
import torch
import torch.nn as nn


from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from torchvision.models import (resnet18, ResNet18_Weights)
from torchvision.models.feature_extraction import create_feature_extractor
from pathlib import Path


class SentinelData(Dataset):
    '''
    Class to load `Sentinel2` data from disk, stored in `.npz` file

    Each Class/Sample object consists of
        - Sentinel2 image as an np array of pixels
        - Binary wildifre label (True/False)
        - Composite key, which is the primary key/unique identifier of the datapoints in the project

    Images are transformed from Height Width Channels to Channels Height Width to match PyTorch requirements and later perform feature extraction 
    '''
    def __init__(self, npz_file: Path):
        """Initialise the class object by first loading the data from the `npz` file

        Args:
            npz_file (Path): Path to the `npz` file to load the img data along wiht fire label and composite keys
        """        
        data      = np.load(npz_file)
        self.x    = data['x']
        self.y    = data['y']
        self.keys = data['composite_key']

    def __len__(self) -> int:
        """Returns the number of samples in the dataset 

        Returns:
            int: Total number of observations in the dataset 
        """        
        return len(self.x)

    def __getitem__(self, idx: int) -> dict:
        """Fetches a single sample from the dataset using `idx` variable

        Args:
            idx (int): Index of observation to retrieve from saple

        Returns:
            dict: Dictionary contaning: 
            - `pixel_data` (torch.Tensor): Sentinel-2 image in CHW format.
            - `fire_label` (bool): Binary wildfire label.
            - `composite_key` (str): Unique identifier for the observation.
        """        
        # Change/permute image from HeightWidthChannel to CHW as the CNN model expects
        pixel_data = torch.from_numpy(self.x[idx]).permute(2,0,1)
        fire_label = self.y[idx]
        composite_key = str(self.keys[idx])

        return {"pixel_data": pixel_data,
                "fire_label": fire_label,
                "composite_key": composite_key}
    
    def sample_summary(self, idx=0) -> None:
        """Print a summary of the dataset and an example sample

           Displays dataset size, image dimensions before and after tensor
           transformation, data types, available labels, and the selected sample's
           label and composite key.

        Args:
            idx (int, optional): Index of the observation to describe. Defaults to 0.
        """        

        sample = self[idx]

        print("SentinelDataset Sample Summary")
        print("------------------------------")
        print("Showing full data attributes and original attributes vs (->) performed transformations\n")
        print(f"{'Total imgs':<12} : {len(self)}")
        print(f"{'Image shape':<12} : {str(self.x.shape[1:]):<20} -> {tuple(sample['pixel_data'].shape)}")
        print(f"{'Image dtype':<12} : {str(self.x.dtype):<20} -> {sample['pixel_data'].dtype}")
        print(f"{'All labels':<12} : {np.unique(self.y)}")
        print(f"{'Label':<12} : {str(self.y.dtype):<20} -> {sample['fire_label']} ({type(sample['fire_label']).__name__})")
        print(f"{'Key':<12} : {str(self.keys.dtype):<20} -> {sample['composite_key']} ({type(sample['composite_key']).__name__})")

class ResNetFeatExtractor(nn.Module):
    """ResNet18 feature extractor, that inherits from `nn.Module` and uses pretrained/existing weights

    The class loads a pre trained ResNet18 model and uses the torchvision `create_feature_extractor` API to return the output
    of the global average pooling layer (`avgpool`). All pretrained weights are frozen so the class only works as a feature extractor
    and doesnt update parameters/weights

    """    
    def __init__(self):
        """Initiliase the pretrained ResNet18 feature extractor

        Loads the default pretrained weights, uses `create_feature_extractor` to skip classification layer, and freezes all the parameters to prevent 
        the model from updating these values
        """        
        # Initialize nn.Module class before defining FeatureExtractor
        super().__init__()

        # Load pre trained weights
        weights = ResNet18_Weights.DEFAULT
        self.model = resnet18(weights = weights)
        # Remove final classification layer (as we only need feature extraction)
        self.extractor = create_feature_extractor(self.model, 
                                                  return_nodes = {"avgpool": "features"})
        # Freeze weights
        for param in self.model.parameters():
            param.requires_grad = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extracts the features from a given batch of Sentinel2 images

        Args:
            x (torch.Tensor): Batch of inputs of Sentinel2 images

        Returns:
            torch.Tensor: Flattened features extracted from the images
        """        
        features = self.extractor(x)
        return features['features'].flatten(1)
    
def extract_resnet_features(sentinel_files: list[Path], batch_size: int = 32, shuffle: bool = False):

    total_files = len(sentinel_files)
    for idx, f in enumerate(sentinel_files):

        currently_at = f"[{idx}/{total_files}]"
        print(f"{currently_at} | Loaded Sentinel Data:  Features Extracted  ", end = "\r", flush = True)
        sentinel_data = SentinelData(f)
        loader = DataLoader(sentinel_data, batch_size = batch_size, shuffle = shuffle)
        print(f"{idx}/{total_files} - Loaded Sentinel Data: ✅ Features Extracted  ", end = "\r", flush = True)


