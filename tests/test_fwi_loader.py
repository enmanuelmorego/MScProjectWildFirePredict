import loaders.fwi_loader as fl
from pathlib import Path

def test_fwi_select_files_correct_years():
    years = [2017, 2018, 2019,2020,2027]

    csv_paths = [Path(f) for f in ['2018FWI.csv', '2020FWI.csv']]
    grb_paths = [Path(f) for f in ['2020FWI.grib', '2021FWI.grib', '2019FWI.grib']]
    
    out = fl.fwi_select_files(csv_paths, grb_paths, years)
    print(out)
    expect = {'available_csv' : [Path('2018FWI.csv'), Path('2020FWI.csv')], 
              'available_grib': [Path('2019FWI.grib')],
              'required_years': {'2017', '2027'}}
    assert out == expect

def test_check_drive_fwi_nomatching_years():
    years = [2019, 2020, 2017,2019]
    csv_paths = [Path(f) for f in ['2015FWI.csv', '2010FWI.csv']]
    grb_paths = [Path(f) for f in ['2015FWI.grib', '2012FWI.grib']]

    out = fl.fwi_select_files(csv_paths, grb_paths, years)
    expect = {'available_csv' : [], 
              'available_grib': [],
              'required_years': {'2017', '2019', '2020'}}
    assert out == expect

def test_check_drive_fwi_full_match():
    years = [2017, 2019, 2020,2021]
    csv_paths = [Path(f) for f in ['1990FWI.csv', '2017FWI.csv', '2018FWI.csv', '2019FWI.csv', '2020FWI.csv']]
    grb_paths = [Path(f) for f in ['2019FWI.grib', '2020FWI.grib', '2021FWI.grib']]
    out = fl.fwi_select_files(csv_paths, grb_paths, years)
    

    expect = {'available_csv': [Path('2017FWI.csv') ,
                                Path('2019FWI.csv') , 
                                Path('2020FWI.csv') ], 
             'available_grib': [Path('2021FWI.grib')],
             'required_years': set()}
    assert out == expect

def test_check_drive_fwi_empty_files():
    years     = [2019, 2020, 2017,2021]
    csv_paths = []
    grb_paths = []
    out       = fl.fwi_select_files(csv_paths, grb_paths, years)
    expect    = {'available_csv': [], 'available_grib': [], 'required_years': {'2017', '2019', '2020', '2021'}}
    assert out == expect