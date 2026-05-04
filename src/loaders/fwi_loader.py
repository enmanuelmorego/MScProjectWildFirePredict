"""
Method that contains all the functions to load the FWI data
"""
import src.utils.file_utils as fu

from pathlib import Path
import cdsapi
import os

def fwi_select_files(fwi_csv: list[Path], fwi_grib: list[Path], requested_years: list[int] ) -> dict:
  """  Function to check .csv and .grib file availability in Google Drive for Fire Weather Index data
  Each FWI file corresponds to a full year worth of data, therefore, the checks are performed in a year by year basis 
  - Compare the years with a list of available files provided 
  - It extracts the csv that matches the requested years
  - Then it extracts the .grib files if the year is part of the `requested_years` set and `not in` the extracted/available .csv files
  - Then it extract the years for which no .csv nor .grib are available (this is later used to download the .grib from the API)

  Purpose:
    Reduce the computational load of donwloading the .grib files from the API anytime time the analysis is ran
    - For the required analysis, extract the .csv file names to be used if available 
    - Identify any .grib files that have not yet been transformed to .csv so these can be transformed rather than downlaoding new data again
    - Identify gaps in the data and download data only relevant for the present analysis

  Args:
      fwi_csv (list[Path]): List of file paths of available, processed csv files
      fwi_grib (list[Path]): List of file paths of available, processed grib files
      requested_years (list[int]): List of requested years, provided by user in `set_parameters.py` file

  Returns:
      dict: Dictionary with available files (if there are existing files in storage that matches the required years) and required years if the prior is not true

  Example:
    out_dict = {'available_csv' : ['2017FWI.csv', '2018FWI.csv'],
                'available_grib': ['2019FWI.grib', '20202FWI.grib']
                'required_years': {'2021', '2022'}}
  """  
 # initialise output dictionary

  requested_years_str = [str(y) for y in requested_years]
  csv_yrs             = set([os.path.basename(fy)[0:4] for fy in fwi_csv if os.path.basename(fy)[0:4] in requested_years_str])
  grib_yrs            = set([os.path.basename(fy)[0:4] for fy in fwi_grib if os.path.basename(fy)[0:4] in requested_years_str and os.path.basename(fy)[0:4] not in csv_yrs])
  all_files           = csv_yrs | grib_yrs
  missing_yrs         = set([my for my in requested_years_str if my not in all_files])

  matched_csv_files  = [f for f in fwi_csv  if os.path.basename(f)[0:4] in csv_yrs]
  matched_grib_files = [f for f in fwi_grib if os.path.basename(f)[0:4] in grib_yrs]

  return {'available_csv' : matched_csv_files,
          'available_grib': matched_grib_files,
          'required_years': missing_yrs}

def fwi_file_availability_wrapper(data_dir: Path, requested_years: list[int], dir_name: str ):
  """Wrapper function that searches and checks which files are available as csv, grib and which need downloading

  Args:
      data_dir (Path): Directory of data storage
      requested_years (list[int]): Years requested to process (from `set_parameters.py` file)
      dir_name (str): Name of directory (FWI in this case)

  Returns:
      _type_: _description_
  """    
  fwi_csv_files  = fu.get_filepaths(data_dir, dir_name, "csv")
  fwi_grib_files = fu.get_filepaths(data_dir, dir_name, "grib")
  fwi_files      = fwi_select_files(fwi_csv_files, fwi_grib_files, requested_years)
  return fwi_files

def fwi_fetch_from_api(required_years: set, fwi_data_dir: Path) -> None:
  """ Function to fetch the FWI data from CEMS Early Warning Data Store for the required years passed in the argument
  Uses cdsapi to fetch the data and download the corresponding .grib file

  Args:
      required_years (set): A set of strings containing the years required to download
      fwi_data_dir (Path): Path of the FWI data folder
  """
  print("\t📈 Fetching FWI data from CDS API...")
  for y in required_years:
    fname         = f"{y}FWI.grib"
    out_file_path = Path(fwi_data_dir)/fname
    dataset       = "cems-fire-historical-v1"
    request       = {"product_type"  : "reanalysis",
                     "variable"      : ["fire_weather_index"],
                     "dataset_type"  : "consolidated_dataset",
                     "system_version": ["4_1"],
                     "year"          : [y],
                     "month"         : ["01", "02", "03",
                                        "04", "05", "06",
                                        "07", "08", "09",
                                        "10", "11", "12"],
                     "day"           : ["01", "02", "03",
                                        "04", "05", "06",
                                        "07", "08", "09",
                                        "10", "11", "12",
                                        "13", "14", "15",
                                        "16", "17", "18",
                                        "19", "20", "21",
                                        "22", "23", "24",
                                        "25", "26", "27",
                                        "28", "29", "30",
                                        "31"],
                     "grid"          : "original_grid",
                     "data_format"   : "grib"}
      
    client = cdsapi.Client()
    client.retrieve(dataset, request, out_file_path.as_posix())


