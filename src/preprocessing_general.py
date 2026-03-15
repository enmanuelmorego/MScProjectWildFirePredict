'''
Scripts that collapses and summarises data frames into specified format for analysis
'''
import pandas as pd
import geopandas as gpd
import utils as u
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.colors as colors
from pathlib import Path
from typing import Any

def summarise_viirs(df_viirs: gpd.GeoDataFrame, df_uk_grid: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Function that summarises VIIRS data and generates fire/nofire labels for each `grid_id` `date` pairs (and renames acq_date to date)

    Each VIIRS observation corresponds to an identified fire. All observations within a grid get summarised into a single
    row of data. Summary stats are taken for the following values:
        - Number of VIIRS observations in grid (`n`)
        - Max FRP value in grid
        - Mean FRP value

    Args:
        df_viirs (dataframe): Dataframe containing the data from VIIRS satellite
        df_uk_grid (GeoDataframe): Geo data frame with all the UK grid coordinates

    Returns:
        df: Dataframe with VIIRS data collapsed per grid, with max and mean values for each grid
            The dataframe contains only those `grid_id` where a VIIRS signal was present

    """
    df_viirs = df_viirs.rename(columns = {'acq_date': 'date'})
    df_viirs_joined = gpd.sjoin(df_viirs, df_uk_grid, how = 'inner', predicate = 'within')
    df_viirs_summary = (df_viirs_joined
                        .groupby(['grid_id', 'date'], as_index = False)
                        .agg(viirs_n  = ('frp', 'size'),
                             frp_max  = ('frp', 'max'),
                             frp_mean = ('frp', 'mean')))
    df_viirs_summary['fire_lbl'] = True
    
    return df_viirs_summary

def combined_dfs(dict_dfs: dict):
    """
    Combines all data sources into a single data frame with all the relevant features for the model (Except for sentinel image data)
    Left joins the df_viirs_summary to the df_daily_uk by (`grid_id`, `date`) to have a full dataset with fire observations labels and UK grid data 
    Fills in NAs for the following variables with the following values:

        - fire_lbl = False
        - viirs_n  = 0
        - far_max  = 0
        - frp_mean = 0
    """
    # Extract data frames from dictionary
    try:
        df_grids_day  = dict_dfs['df_daily_grid']
        df_viirs_summ = dict_dfs['df_viirs_summary']
        df_fwi        = dict_dfs['df_fwi']
    except KeyError as e:
        raise KeyError(f"❌ Missing required dataframe {e}")

    # Process VIIRS data
    df_viirs_grid                                     = df_grids_day.merge(df_viirs_summ, on = ['grid_id','date'], how = 'left')
    df_viirs_grid['fire_lbl']                         = (df_viirs_grid['fire_lbl']
                                                        .astype('boolean')
                                                        .fillna(False))
    df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']] = df_viirs_grid[['viirs_n', 'frp_max', 'frp_mean']].fillna(0)

    # Process FWI data
    df_fwi_viirs_grid = df_viirs_grid.merge(df_fwi,
                                            on = ['grid_id','date'],
                                            how = 'left')
    
    return df_fwi_viirs_grid

def remove_na_fwi_grid1(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Removes grid_id = 1 from the dataset as the FWI value for grid_id 1 was missing across the sample

    During spatial validation of the FWI raster-to-grid mapping, grid_id = 1 (a coastal grid in south-west England) was found to
    have missing FWI values for all day

    Rationale

        - The grid represents <0.1% of all spatial units,
        - FWI is entirely missing for that grid across all dates,
        - Imputation would introduce artificial meteorological signal,

    the grid is removed from the modelling dataset to preserve
    data integrity.

    This is only removed IF grid_id == 1 AND fwi value is NA

    Returns:
        
        pd.DataFrame
            Dataset excluding grid_id = 1.
    """
    remove = ((df['grid_id'] == 1) &
              (df['fwi_max'].isna())
              )
  
    rr = remove.sum()
    if rr > 0:
        print(f"\tℹ️  Removed {rr} rows with grid_id == 1")
    else:
        print(f"\t✅  No grids to remove - grid_id contains data")

    df_out = df[~remove].copy()
    return df_out

def preprocessing_pipeline(df_dict: dict, run_id: str) -> gpd.GeoDataFrame:
    """
    Wrapper function to execute the preprocessing tasks

    Args:
        df_dict

        run_id (str): String containing the identifiator of the run to save all the relevant logs for the current run
    """
    try:
        df_viirs   = df_dict['df_viirs']
        df_uk_grid = df_dict['df_uk_grid']
    except KeyError as e:
        raise KeyError(f"❌ Missing required dataframe {e}")

    df_viirs_summary            = summarise_viirs(df_viirs, df_uk_grid)
    df_dict['df_viirs_summary'] = df_viirs_summary
    loaded_data_mt              = u.dfs_metadata(df_dict)
    u.save_json(loaded_data_mt,"LOAD_METADATA", run_id)

    df_model_pre_raw = combined_dfs(df_dict)
    df_model_pre     = remove_na_fwi_grid1(df_model_pre_raw)

    df_model_pre['composite_key'] = (df_model_pre['grid_id'].astype(str) + 
                                     df_model_pre['date'].dt.strftime("%Y%m%d"))

    df_model_summary = {'df_type'            : type(df_model_pre).__name__,
                        'columns'            : list(df_model_pre.columns),
                        'date_from'          : df_model_pre['date'].min().strftime("%Y-%m-%d"),
                        'date_to'            : df_model_pre['date'].max().strftime("%Y-%m-%d"),
                        'total_rows'         : int(df_model_pre.shape[0]),
                        'total_grids'        : int(df_model_pre['grid_id'].nunique()),
                        'grid_min'           : int(df_model_pre['grid_id'].min()),
                        'grid_max'           : int(df_model_pre['grid_id'].max()),
                        'viirs_true_obs'     : int(df_model_pre[df_model_pre['fire_lbl'] == True].shape[0]),
                        'fire_lbl_proportion': int(df_model_pre[df_model_pre['fire_lbl'] == True].shape[0]) / int(df_model_pre.shape[0]),
                        'unique_viirs_grids' : int(df_model_pre[df_model_pre['fire_lbl'] == True]['grid_id'].nunique()),
                        'fwi_notna'          : int(df_model_pre[df_model_pre['fwi_max'].notna()].shape[0])
                        }
                        
    u.save_json(df_model_summary,"PREPROCESSING_METADATA", run_id)
    

    return df_model_pre

# -------------------------
# SAMPLING FIRE DATAPOINTS
# -------------------------  
"""
Sampling is necessary to reduce computational power and address the imbalanced dataset due to low wildfire occurrence
The chosen ratio is 1:3 but the suite of functions is flexible to adjust this ratio if needed
"""   
def sample_fire_obs(df_preproc: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Function that extracts the fire observations from the pre processed data set
    These are the observations that are to be used as `Y variable` in the analysis

    It filters only those values where the `fire_lbl == True` and select relevant columns only
    `[date, grid_id, fire_lbl]` 

    Suffix `dv` is added at the end of the column name to indicate these values relate to the `Dependent Variable` or Response values

    Args:
        df_preproc (GeoDataFrame): Preprocessed data frame containing all the grid+date combinations along with variables

    Returns:
        df (DataFrame): Dataframe containing only `fire_lbl == True` and columns  `[date_dv, grid_id_dv, fire_lbl_dv]` 
    """
    df = df_preproc[df_preproc['fire_lbl'] == True].copy()
    df = df[['date', 'grid_id', 'fire_lbl']]
    df = df.add_suffix('_dv')
    return df

def sample_nofire_obs(df_preproc                  :gpd.GeoDataFrame, 
                      df_fire                     : pd.DataFrame, 
                      nofire_proximity_window_days: int,
                      nofire_total_samples        : int,
                      random_seed                 : int) -> pd.DataFrame:
    """
    Function that extracts the no fire observations from the pre processed data set
    
    The function iterates thru `df_fire` (which is all the fire observations) and for each `grid_id` finds all nofire observations that fall
    within +/- `nofire_proximity_window_days` 

    Then `nofire_total_samples` determines how many of these available nofire dates will be kept. This is the fire to nofire ratio controller

    Final dataframe also contained the renamed columns below, with the suffix `dv` to indicate that this data is the dependent variable
    `[date, grid_id, fire_lbl]` 


    Args:
        df_preproc (GeoDataFrame): Preprocessed data frame containing all the grid+date combinations along with variables
        df_fire (df): Dataframe containing the fire observations to be used as the Y variables
        nofire_proximity_window_days (int): Number of allowed days (+/-) from anchor date (date of fire observation)
        nofire_total_samples (int): Total number of no fire values to sample 
        random_seed (int): value to be used as the random seed in the sampling procedure

    Returns:
        df (DataFrame): Dataframe containing only `fire_lbl == False` and columns  `[date_dv, grid_id_dv, fire_lbl_dv]` 
    """
    df_nofire = df_preproc[df_preproc['fire_lbl'] == False].copy()
    list_nofire = []
    sampled_set = set()
    df_nofire_grouped = df_nofire.groupby('grid_id')

    for r in df_fire.itertuples():
        r: Any
        anchor_grid_id   = r.grid_id_dv
        anchor_date      = r.date_dv

        if anchor_grid_id not in df_nofire_grouped.groups:
            continue
        # Reduce the size of the data frame to check for values
        df_grid = df_nofire_grouped.get_group(anchor_grid_id)
        # Extract ALL potential no fire candidate values
        df_nofire_sample = df_grid[(
                                      # Find days within a 30 day range of current date 
                                      ((df_grid['date'] >= (anchor_date - pd.DateOffset(days=nofire_proximity_window_days))) &
                                       (df_grid['date'] <= (anchor_date + pd.DateOffset(days=nofire_proximity_window_days)))) &
                                      # Avoid sampling the same value if it was already sampled by another fire lbl
                                       ~df_grid['composite_key'].isin(sampled_set)
                                      )]
        # Randomly select from the nofire available datapoints
        df_nofire_sample = df_nofire_sample.sample(n = min(nofire_total_samples, len(df_nofire_sample)),  random_state = random_seed)

        # Add values to list, which is later transform to df
        list_nofire.append(df_nofire_sample)
        # Append selected values to set to avoid double sampling
        sampled_set.update(df_nofire_sample['composite_key'])

    df_out = pd.DataFrame(pd.concat(list_nofire))
    df_out = df_out[['date', 'grid_id', 'fire_lbl']]
    df_out = df_out.add_suffix('_dv')
    return df_out

def sample_fire_nofire_combined(df_sampled_fire: pd.DataFrame, df_sampled_nofire: pd.DataFrame) -> pd.DataFrame:
    """
    Function that combines the fire and no fire sampled data into a single data frame
    It also generates the composite matching key to pull the previous day from the main dataset
    This is computed by taking the observation_date - 1 day, and combining with grid_id

    Args:
        df_sampled_fire   (df): DF containing the sampled observed fires data points
        df_sampled_nofire (df): DF containing the sampled observed no fires data points

    Returns:
        df (Df) Data frame containing all the fire and no fire observations

    Note:
        Included columns are:
            `[date_dv, grid_id_dv, fire_lbl_dv, bridge_composite_key_dv]`
    """
    df = pd.concat([df_sampled_fire, df_sampled_nofire], ignore_index = True)
    df["bridge_composite_key_dv"] = df["grid_id_dv"].astype(str) + (df["date_dv"]-pd.DateOffset(days=1)).dt.strftime("%Y%m%d")
    return df

def sampling_pipeline(df_preprocessed: gpd.GeoDataFrame, 
                      nofire_proximity_window_days: int, 
                      nofire_total_samples: int,
                      random_seed: int):
    """
    Pipeline function to sample the data. For every fire label in the input data set, it selects integer `nofire_total_samples` of corresponding no fire values. Generates the `Y` values or `predicted` values 
    
    Generates a `bridge_composite_key_dv` which is based on the `grid_id` + `observation date` - `1 day` to then join with the `preprocessed` dataframe for the `predictor` values

    The pipeline also generates the following reporting objects:
        - A histogram showing how many observations per `year-month` with each bar showing `fire`/`nofire` by color for the `Y` variable
        - A heatmap showing which grids are included in the `Y` variable, where color intensity represents how many times a grid was sampled. The plots is an temporal aggregation of the data
        - Basic descriptive stats of the sampled values

    Args:
        df_preprocessed (df): GeoDataFrame containing all the preprocesed data with fire/nofire labels along with all the supporting data and variables
        nofire_proximity_window_days (int): Number of allowed days (+/-) from anchor date (date of fire observation)
        nofire_total_samples (int): Total number of no fire values to sample 
        random_seed (int): value to be used as the random seed in the sampling procedure

    Returns:
        df_out (df): Data frame where each row contains the predictor (X) variables at `t` time and on the same row, the predicted variables at `t+1`  

    """
    df_fire    = sample_fire_obs(df_preprocessed)
    
    df_nofire  = sample_nofire_obs(df_preproc                   = df_preprocessed,
                                   df_fire                      = df_fire,
                                   nofire_proximity_window_days = nofire_proximity_window_days,
                                   nofire_total_samples         = nofire_total_samples,
                                   random_seed                  = random_seed)
    df_sampled = sample_fire_nofire_combined(df_fire, df_nofire)
    df_out     = df_sampled.merge(df_preprocessed, 
                                  left_on  = 'bridge_composite_key_dv',
                                  right_on = 'composite_key', 
                                  how      = 'left')
    df_out     = df_out.dropna(subset=["fwi_max"])
    return df_out

def hist_sampled_variables(df_sampled: pd.DataFrame, title: str) -> Figure:
    """
    Function to plot and save a histogram containing the distribution of the sampled values 

    Args:
       - df_sampled (df): Dataframe containing both fire and nofire sampled values
       - run_id (str): The identifier of the particular coderun 
       - title (str): Title to be used in the plot

    Returns:
        Figure 
    """
    df_toplot = df_sampled.copy()
    # Create year-month column
    df_toplot['year_month'] = df_toplot['date_dv'].dt.to_period('M')
    # Count observations per month split by fire label
    monthly_counts = (df_toplot
                      .groupby(['year_month', 'fire_lbl_dv'])
                      .size()
                      .unstack(fill_value=0)
                      .sort_index())
    # Make sure both columns exist
    monthly_counts = monthly_counts.reindex(columns=[False, True], fill_value=0)
    # Convert PeriodIndex to string for plotting
    months = monthly_counts.index.astype(str)
    # Create plot object
    fig, ax = plt.subplots(figsize=(12,6))
    ax.bar(months, monthly_counts[False], label='No Fire', color='#005580')
    ax.bar(months, monthly_counts[True],  label='Fire',    color='#C9495E', bottom=monthly_counts[False])

    ax.set_xticklabels(months, rotation=45)
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Observations")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig

def heatmap_grid_sampling(df_sampled: pd.DataFrame, df_uk_grid: gpd.GeoDataFrame, uk_shp, title: str):
    """
    Function to produce a heatmap of the count of grid sampling across the UK
    It allows to see if any particular regions are oversampled, and if any regions were ignored

    It takes the sampled data, groups by `grid_id_dv` and gets the count of how many times each grid has been sampled in the whole df
    It joins with the complete UK grid df, and fills any missing `grid_ids` with `0`

    Args:
        - df_sampled (df): Dataframe containing all the sampled (fire/nofire) values 
        - df_uk_grid (GeoDF): GeoPandas dataframe containing grid_id + geometry for UK
        - uk_shp (shp): Shape file of the UK
        - title (str): Title of the plot 

    Returns:
        Figure

    """
    df_count = (df_sampled
                .groupby('grid_id_dv')
                .size()
                .reset_index(name="sample_count"))

    gdf_plot = df_uk_grid.merge(df_count, 
                                left_on  = 'grid_id', 
                                right_on = 'grid_id_dv', 
                                how      = 'left')
    gdf_plot['sample_count'] = gdf_plot['sample_count'].fillna(0)

    # Image
    fig, ax = plt.subplots(figsize=(8, 10))
    # UK background
    uk_shp.plot(ax=ax, color="white", edgecolor="black", linewidth = 0.2)

    # Grid overlay
    gdf_plot.plot(column="sample_count",
                ax=ax,
                cmap="YlOrRd",
                norm=colors.LogNorm(vmin=1, vmax=gdf_plot['sample_count'].max()),
                legend=True,)

    ax.set_title(title)
    # subtitle
    fig.suptitle("Aggregate Log-scaled sample counts per grid for the whole time period",
                fontsize=8,
                y=0.92)
    ax.set_axis_off()
    plt.tight_layout()
    return fig

def sampling_reporting_pipeline(df_plot: pd.DataFrame, df_uk_grid: gpd.GeoDataFrame, uk_sp_file_name: str, crs: str, run_id: str):
    """
    Function pipeline to generate some basic graphs and stats on the sampling procedure to show basic information on sampled data
    Saves the plots into outputs folder, user is notified via the console of specific save location
    and prints basic proportion of Y values sample

    Args:
       - df_plot (df): Dataframe containing both fire and nofire sampled values
       - df_uk_grid (GeoDF): GeoPandas dataframe containing grid_id + geometry for UK
       - uk_sp_file_name (str): Name of shapefile for the plot
       - run_id (str): The identifier of the particular coderun 
       - crs (str): A string containing the EPSG value to set the CRS

    Returns:
        None
    """
    # ShapeFile
    uk_sp_file      = f'data/UKGrid/{uk_sp_file_name}'
    uk              = gpd.read_file(uk_sp_file)
    uk              = uk.to_crs(crs=crs)
    # Generate reporting objects & titles
    title_hist      = "Monthly Observation Counts (Fire vs No Fire) [Predicted Values]"
    date_min        = df_plot['date_dv'].min()
    date_max        = df_plot['date_dv'].max()    
    title_heatmap   = f"HeatMap of Sampled Grids [Predicted Values]\n[{date_min.strftime('%Y-%m-%d')} {date_max.strftime('%Y-%m-%d')}]\n"
    # Create images
    sampled_hist    = hist_sampled_variables(df_sampled = df_plot, title = title_hist)
    sampled_heatmap = heatmap_grid_sampling(df_plot, df_uk_grid, uk, title_heatmap)
    # Save images
    u.save_plots(sampled_hist,    title_hist,    run_id)
    u.save_plots(sampled_heatmap, title_heatmap, run_id)
    print(f"Proportion of Sampled values:")
    print(df_plot['fire_lbl_dv'].value_counts(normalize=True))