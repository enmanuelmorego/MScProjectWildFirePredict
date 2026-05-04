"""
Method that contains all the functions to load the FWI data
"""
from pathlib import Path
import os

def select_fwi_files(fwi_csv: list[Path], fwi_grib: list[Path], requested_years: list[int] ) -> dict:
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