import numpy as np
import torch

from torch.utils.data import Dataset
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