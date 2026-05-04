"""
Module of data transformations
"""
import pandas as pd

def merge_viirs(viirs_dict: dict[str, pd.DataFrame], append_noaa: bool = True) -> dict[str, pd.DataFrame | dict | None ]:
    """Takes a dictionary containing data frame from VIIRS products (NOAA and SNPP) and merged them into a single data frame.
    Data from SNPP takes precedence over NOAA as SNPP data is more robust and undergoes more strict QA

    Args:
        viirs_dict (dict[str, pd.DataFrame]): Dictionary containing NOAA and SNPP data frames
        append_noaa (bool, optional): Option for user to completly ignore NOAA data. Defaults to True.

    Raises:
        ValueError: When SNPP data is not provided 

    Returns:
        dict[str, Any]: `df`: Data frame merged. `data_report`: a dictionary containing information on the rows and data origin
    """

    cols_merge = ['longitude','latitude','acq_date']
    df_snpp    = viirs_dict.get('snpp')
    df_noaa    = viirs_dict.get('noaa')

    if df_snpp is None:
        raise ValueError("❌ SNPP data is required")

    if append_noaa and df_noaa is not None:
        # Find values in NOAA not in SNPP 
        df_diff = df_noaa.loc[~df_noaa.set_index(cols_merge).index.isin(df_snpp.set_index(cols_merge).index)]
        df_out  = pd.concat([df_snpp, df_diff], ignore_index = True)

        data_report = {'total_rows_snpp': df_snpp.shape[0],
                       'total_rows_noaa': df_diff.shape[0]}
        return {'df'         : df_out,
                'data_report': data_report}
    else:
        return {'df'         : df_snpp,
                'data_report': None}
