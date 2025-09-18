import numpy as np
import pandas as pd
import streamlit as st
from scipy.optimize import curve_fit

place = 'Venue_x'
place = 'Country'
type = 'PhaseofSeason'
type = 'BowlCat'
type = 'entryphase'

def cubic_poly(w, a, b, c, d):
    return a * w**3 + b * w**2 + c * w + d

def truemetrics(truevalues):
    truevalues['Ave'] = truevalues['Runs Scored'] / truevalues['Out']
    truevalues['SR'] = (truevalues['Runs Scored'] / truevalues['BF'] * 100)
    truevalues.loc[truevalues['Out']==0,'Ave']= truevalues['Runs Scored']
    truevalues['Expected Ave'] = truevalues['Expected Runs'] / truevalues['Expected Outs']
    truevalues['Expected SR'] = (truevalues['Expected Runs'] / truevalues['BF'] * 100)

    # Calculate 'True Ave' and 'True SR' for the final results
    truevalues['True Ave'] = (truevalues['Ave'] - truevalues['Expected Ave'])
    truevalues['True SR'] = (truevalues['SR'] - truevalues['Expected SR'])

    truevalues['Out Ratio'] = (truevalues['Expected Outs'] / truevalues['Out'])
    # truevalues['Impact/Inns'] = (truevalues['Impact'] / truevalues['I'])
    return truevalues

def calculate_entry_point_all_years(data):
    # Vectorized approach
    first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter']).copy()

    # Vectorized conversion - much faster than apply
    over_vals = first_appearance['Over'].values
    first_appearance['total_deliveries'] = (over_vals.astype(int) * 6 +
                                            ((over_vals - over_vals.astype(int)) * 10).astype(int))

    # Vectorized average calculation
    avg_entry_point_deliveries = first_appearance.groupby('Batter')['total_deliveries'].median().reset_index()

    # Vectorized conversion back to overs
    deliveries = avg_entry_point_deliveries['total_deliveries'].values
    avg_entry_point_deliveries['average_over'] = np.round((deliveries // 6) + (deliveries % 6) / 10, 1)

    return avg_entry_point_deliveries[['Batsman','Batter', 'average_over']], first_appearance

def calculate_first_appearance(data):
    # Optimized version
    first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter']).copy()

    # Vectorized conversion
    over_vals = first_appearance['Over'].values
    first_appearance['total_deliveries'] = (over_vals.astype(int) * 6 +
                                            ((over_vals - over_vals.astype(int)) * 10).astype(int))

    avg_entry_point_deliveries = first_appearance.groupby(['Batsman','Batter', 'year'])['total_deliveries'].median().reset_index()

    # Vectorized conversion back
    deliveries = avg_entry_point_deliveries['total_deliveries'].values
    avg_entry_point_deliveries['average_over'] = np.round((deliveries // 6) + (deliveries % 6) / 10, 1)

    return avg_entry_point_deliveries[['Batsman','Batter', 'average_over']]

def analyze_data_for_year2(data):
    year_data = data.copy()
    first_appearance_data = calculate_first_appearance(year_data)

    if 'analysis_results' in locals() or 'analysis_results' in globals():
        analysis_results = pd.merge(year_data, first_appearance_data, on=['Batter'], how='left')
    else:
        analysis_results = first_appearance_data

    return analysis_results

@st.cache_data
def analyze_data_for_year3(year2, data2):
    # Early filtering
    combineddata = data2[(data2['TeamInns'] < 3) & (data2['year'] == year2)]

    # Optimized innings calculation
    inns = combineddata.groupby(['Batsman','Batter', 'MatchNum'])[['Runs']].sum().reset_index()
    inns['I'] = 1
    inns2 = inns.groupby(['Batsman','Batter'])[['I']].sum().reset_index()
    inns2.columns = ['Batsman','Player', 'I']
    inns['CI'] = inns.groupby(['Batter'])[['I']].cumsum()

    # Vectorized entry point analysis
    # analysis_results = analyze_data_for_year2(combineddata)
    # analysis_results.columns = ['Player', 'Median Entry Point']

    # Optimized dismissal data processing
    valid = ['X','WX']
    dismissed_mask = combineddata['Notes'].isin(valid)
    dismissed_data = combineddata[dismissed_mask]
    dismissed_data['Out'] = 1

    # More efficient merge
    merge_cols = ['MatchNum','TeamInns', 'Batsman','Batter', 'Notes','over']
    combineddata = pd.merge(
        combineddata,
        dismissed_data[merge_cols + ['Out']],
        on=merge_cols,
        how='left'
    ).fillna({'Out': 0})

    # Vectorized groupby operations
    groupby_cols_player = ['Batsman','Batter', 'TeamInns', place, 'over']
    groupby_cols_over = ['TeamInns', place,'over']

    player_outs = dismissed_data.groupby(groupby_cols_player)[['Out']].sum().reset_index()
    player_outs.columns = ['Batsman','Player', 'TeamInns', place, 'Over', 'Out']

    over_outs = dismissed_data.groupby(groupby_cols_over)[['Out']].sum().reset_index()
    over_outs.columns = ['TeamInns', place, 'Over', 'Outs']

    player_runs = combineddata.groupby(groupby_cols_player)[['Runs', 'B','Impact']].sum().reset_index()
    player_runs.columns = ['Batsman','Player', 'TeamInns', place, 'Over', 'Runs Scored', 'BF','Impact']

    over_runs = combineddata.groupby(groupby_cols_over)[['Runs', 'B']].sum().reset_index()
    over_runs.columns = ['TeamInns', place, 'Over', 'Runs', 'B']

    # Sequential merges (more memory efficient)
    combined_df = pd.merge(player_runs, player_outs, on=['Batsman','Player', 'TeamInns', place, 'Over'], how='left')
    combined_df2 = pd.merge(over_runs, over_outs, on=['TeamInns', place, 'Over'], how='left')
    combined_df3 = pd.merge(combined_df, combined_df2, on=['TeamInns', place, 'Over'], how='left')

    # Vectorized null handling and calculations
    combined_df3 = combined_df3.fillna({'Outs': 0, 'Out': 0})

    # Vectorized arithmetic operations
    combined_df3['Over_Runs'] = combined_df3['Runs'] - combined_df3['Runs Scored']
    combined_df3['Over_B'] = combined_df3['B'] - combined_df3['BF']
    combined_df3['Over_Outs'] = combined_df3['Outs'] - combined_df3['Out']

    # Avoid division by zero with vectorized operations
    combined_df3['BSR'] = np.divide(combined_df3['Over_Runs'], combined_df3['Over_B'],
                                    out=np.zeros_like(combined_df3['Over_Runs']),
                                    where=combined_df3['Over_B']!=0)
    combined_df3['OPB'] = np.divide(combined_df3['Over_Outs'], combined_df3['Over_B'],
                                    out=np.zeros_like(combined_df3['Over_Outs']),
                                    where=combined_df3['Over_B']!=0)

    # Vectorized expected calculations
    combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
    combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']

    # Vectorized phase calculations
    ball_bins2 = [0, 6,11, 16, 20]
    ball_labels2 = ['1 to 6', '7 to 11','12 to 16', '17 to 20']
    combined_df3['phase'] = pd.cut(combined_df3['Over'], bins=ball_bins2,
                                   labels=ball_labels2, include_lowest=True, right=True)

    # Optimized aggregation
    agg_cols = ['Runs Scored', 'BF', 'Out','Expected Runs', 'Expected Outs','Impact']
    truevalues = combined_df3.groupby(['Player','Batsman'], observed=True)[agg_cols].sum().reset_index()

    final_results = truemetrics(truevalues)

    # Efficient final merges
    players_years = combineddata[['Batsman','Batter','year']].drop_duplicates()
    players_years.columns = ['Batsman','Player','Year']

    final_results2 = pd.merge(inns2, final_results, on=['Batsman','Player'], how='left')
    final_results3 = pd.merge(players_years, final_results2, on=['Batsman','Player'], how='left')
    # final_results4 = pd.merge(final_results3, analysis_results, on='Batsman','Player', how='left')

    return final_results3.round(2)

def truemetricsbowling(truevalues):
    # Avoid division by zero with vectorized operations
    truevalues['Econ'] = np.divide(truevalues['RC'], truevalues['BF'],
                                   out=np.zeros_like(truevalues['RC']),
                                   where=truevalues['BF']!=0) * 6
    truevalues['SR'] = np.divide(truevalues['BF'], truevalues['Out'],
                                 out=np.zeros_like(truevalues['BF']),
                                 where=truevalues['Out']!=0)
    truevalues['Expected Econ'] = np.divide(truevalues['Expected Runs'], truevalues['BF'],
                                            out=np.zeros_like(truevalues['Expected Runs']),
                                            where=truevalues['BF']!=0) * 6
    truevalues['Expected SR'] = np.divide(truevalues['BF'], truevalues['Expected Outs'],
                                          out=np.zeros_like(truevalues['BF']),
                                          where=truevalues['Expected Outs']!=0)

    truevalues['True Econ'] = truevalues['Expected Econ'] - truevalues['Econ']
    truevalues['True Wickets'] = truevalues['Out'] - truevalues['Expected Outs']
    truevalues['True W/ 4 overs'] = np.divide(truevalues['True Wickets'], (truevalues['BF'] / 24),
                                              out=np.zeros_like(truevalues['True Wickets']),
                                              where=truevalues['BF']!=0)
    # truevalues['Impact/Inns'] = (truevalues['Impact'] / truevalues['I'])
    return truevalues

def analyze_data_for_year6(year2, data2):
    print(f"Processing year {year2} (bowling analyze_6)...")

    # Early filtering
    combineddata = data2[(data2['TeamInns'] < 3) & (data2['year'] == year2)]

    # Optimized innings calculation
    inns = combineddata.groupby(['Bowlers','MatchNum'], observed=True)[['Runs']].sum().reset_index()
    inns['I'] = 1
    inns2 = inns.groupby(['Bowlers'], observed=True)[['I']].sum().reset_index()
    inns2.columns = ['Player','I']
    inns['CI'] = inns.groupby(['Bowlers'], observed=True)[['I']].cumsum()

    # Vectorized entry point analysis
    # analysis_results = analyze_data_for_year2(combineddata)
    # analysis_results.columns = ['Player', 'Median Entry Point']

    # Optimized dismissal data processing
    valid = ['X' ,'XC','XT' , 'XU','XSUTC', 'NX' ,'LX' ,'NXT', 'XZ','XP','PX','WX']
    dismissed_mask = (combineddata['Notes'].isin(valid) &
                      (combineddata['BowlDis'] == 'Y') &
                      (combineddata['LongDis'] != 'run out'))
    dismissed_data = combineddata[dismissed_mask]
    dismissed_data['Out'] = 1

    # More efficient merge
    merge_cols = ['MatchNum','TeamInns',place,'Bowlers', 'Notes','over']
    combineddata = pd.merge(
        combineddata,
        dismissed_data[merge_cols + ['Out']],
        on=merge_cols,
        how='left'
    ).fillna({'Out': 0})

    combineddata = combineddata.drop_duplicates()

    # Vectorized groupby operations
    player_outs = dismissed_data.groupby(['Bowlers', place,'over'], observed=True)[['Out']].sum().reset_index()
    player_outs.columns = ['Player', place,'Over', 'Out']

    over_outs = dismissed_data.groupby([place,'over'], observed=True)[['Out']].sum().reset_index()
    over_outs.columns = [place,'Over', 'Outs']

    player_runs = combineddata.groupby(['Bowlers', place,'over'], observed=True)[['RC', 'B','Impact']].sum().reset_index()
    player_runs.columns = ['Player', place, 'Over', 'RC', 'BF','Impact']

    over_runs = combineddata.groupby([place,'over'], observed=True)[['RC', 'B']].sum().reset_index()
    over_runs.columns = [place,'Over', 'Runs', 'B']

    # Sequential merges
    combined_df = pd.merge(player_runs, player_outs, on=['Player', place,'Over'], how='left')
    combined_df2 = pd.merge(over_runs, over_outs, on=[place,'Over'], how='left')
    combined_df3 = pd.merge(combined_df, combined_df2, on=[place,'Over'], how='left')

    # Vectorized null handling and calculations
    combined_df3 = combined_df3.fillna({'Outs': 0, 'Out': 0})

    # Vectorized arithmetic operations
    combined_df3['Over_Runs'] = combined_df3['Runs'] - combined_df3['RC']
    combined_df3['Over_B'] = combined_df3['B'] - combined_df3['BF']
    combined_df3['Over_Outs'] = combined_df3['Outs'] - combined_df3['Out']

    # Safe division operations
    combined_df3['BSR'] = np.divide(combined_df3['Over_Runs'], combined_df3['Over_B'],
                                    out=np.zeros_like(combined_df3['Over_Runs']),
                                    where=combined_df3['Over_B']!=0)
    combined_df3['OPB'] = np.divide(combined_df3['Over_Outs'], combined_df3['Over_B'],
                                    out=np.zeros_like(combined_df3['Over_Outs']),
                                    where=combined_df3['Over_B']!=0)

    # Vectorized expected calculations
    combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
    combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']

    # Vectorized phase calculations
    ball_bins2 = [0, 6,11, 16, 20]
    ball_labels2 = ['1 to 6', '7 to 11','12 to 16', '17 to 20']
    combined_df3['phase'] = pd.cut(combined_df3['Over'], bins=ball_bins2,
                                   labels=ball_labels2, include_lowest=True, right=True)

    # Optimized aggregation
    agg_cols = ['RC', 'BF', 'Out','Expected Runs', 'Expected Outs','Impact']
    truevalues = combined_df3.groupby(['Player'], observed=True)[agg_cols].sum().reset_index()

    final_results = truemetricsbowling(truevalues)

    # Efficient final merges
    players_years = combineddata[['Bowlers', 'BowlCat','year']].drop_duplicates()
    players_years.columns = ['Player','Type','Year']

    final_results2 = pd.merge(inns2, final_results, on=['Player'], how='left')
    final_results3 = pd.merge(players_years, final_results2, on=['Player'], how='left')
    # final_results4 = pd.merge(final_results3, analysis_results, on='Player', how='left')
    # final_results3['Year'] = year2

    return final_results3.round(2)

@st.cache_data
def load_data2(filename):

    return pd.read_csv(filename)  # Changed to parquet

# Vectorized DL model application
def apply_dl_vectorized(df, balls_col, wickets_param, alpha_p, beta_p):
    """Apply DL model vectorized - wickets_param can be column name (str) or constant (int)"""
    balls = df[balls_col].values

    if isinstance(wickets_param, str):
        # It's a column name
        wickets = df[wickets_param].values
    else:
        # It's a constant value (like 0)
        wickets = np.full(len(balls), wickets_param)

    alpha = cubic_poly(wickets, *alpha_p)
    beta = cubic_poly(wickets, *beta_p)

    return alpha * (1 - np.exp(-balls / beta))

# Load the data with optimizations
@st.cache_data
def load_data(filename):
    print("Loading data from parquet...")
    data = pd.read_parquet(filename)
    print(data.columns)
    # # Vectorized operations
    # data['B'] = np.where(data['Notes'] == 'W', 0, 1)
    # data['RC'] = data['Runs'] + data['Extras']
    # data['TotalRuns'] = data['Runs'] + data['Extras']
    #
    # # Vectorized date operations
    # data['Date'] = pd.to_datetime(data['StartDate'], format='mixed')
    # data['year'] = data['Date'].dt.year
    #
    # # Remove duplicates early
    # data = data.drop_duplicates()
    #
    # # Vectorized over calculations
    # data['ball2'] = pd.to_numeric(data['Over'], errors='coerce')
    # data['over'] = data['ball2'] // 1 + 1
    #
    # # Bowling type classification using dictionary mapping (faster than multiple isin calls)
    # bowling_map = {
    #     'RF': 'Right Arm Pace', 'RFM': 'Right Arm Pace', 'RM': 'Right Arm Pace', 'RMF': 'Right Arm Pace',
    #     'LF': 'Left Arm Pace', 'LF/LM': 'Left Arm Pace', 'LFM': 'Left Arm Pace', 'LM': 'Left Arm Pace', 'LMF': 'Left Arm Pace',
    #     'OB': 'Right Arm Finger Spin', 'RM/OB': 'Right Arm Finger Spin', 'S': 'Right Arm Finger Spin',
    #     'SLA': 'Left Arm Finger Spin',
    #     'LB': 'Right Arm Wrist Spin',
    #     'SLW': 'Left Arm Wrist Spin'
    # }
    # data['Types'] = data['BowlType'].map(bowling_map).fillna('L')
    #
    # # Simplified BowlCat mapping
    # data['BowlCat'] = data['BowlCat'].replace({'F': 'Pace', 'S': 'Spin'})

    # # Target runs calculation (optimized)
    # print("Calculating target runs...")
    # runsbymatch = data.groupby(['MatchNum','TeamInns'])[['TotalRuns']].sum().reset_index()
    # runsbymatch = runsbymatch[runsbymatch['TeamInns']==1]
    # runsbymatch = runsbymatch.rename(columns={'TotalRuns':'TargetRuns'})
    # runsbymatch = runsbymatch.drop(columns=['TeamInns'])
    #
    # combined_data2 = data[data['TeamInns']==2]
    # combined_data2 = pd.merge(combined_data2, runsbymatch, how='left', on=['MatchNum'])
    # data = pd.concat([data[data['TeamInns']==1], combined_data2], ignore_index=True)
    #
    # # Load DL parameter files
    # print("Loading DL parameters...")
    # dl_params_df = pd.read_csv('dl_model_parameters.csv', low_memory=False)
    # dl_params_df2 = pd.read_csv('dl_model_parameters_ipl_2008_2013.csv', low_memory=False)
    # dl_params_df3 = pd.read_csv('dl_model_parameters_ipl_2014_2017.csv', low_memory=False)
    # dl_params_df4 = pd.read_csv('dl_model_parameters_ipl_2018_2021.csv', low_memory=False)
    #
    # def params(dl_params_df):
    #     alpha_params, _ = curve_fit(cubic_poly, dl_params_df["Wickets"], dl_params_df["Alpha"])
    #     beta_params, _ = curve_fit(cubic_poly, dl_params_df["Wickets"], dl_params_df["Beta"])
    #     return alpha_params, beta_params
    #
    # def dl_model(u, w, alpha_params, beta_params):
    #     alpha = cubic_poly(w, *alpha_params)
    #     beta = cubic_poly(w, *beta_params)
    #     return alpha * (1 - np.exp(-u / beta))
    #
    # # Cumulative calculations (optimized groupby operations)
    # print("Computing cumulative statistics...")
    # data['TeamRuns'] = data.groupby(['MatchNum', 'TeamInns'])['TotalRuns'].cumsum()
    #
    # # Wickets calculation
    # data['Wkts'] = data['HowOut'].notnull().astype(int)
    # data['TeamWicket'] = data.groupby(['MatchNum', 'TeamInns'])['Wkts'].cumsum()
    #
    # # Other cumulative stats
    # data['TeamBalls'] = data.groupby(['MatchNum', 'TeamInns'])['B'].cumsum()
    # data['MatchBatRuns'] = data.groupby(['Batter','MatchNum', 'TeamInns'])['Runs'].cumsum()
    # data['BatterBalls'] = data.groupby(['Batter','MatchNum', 'TeamInns'])['B'].cumsum()
    # data['MatchBowlRC'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'])['RC'].cumsum()
    # data['MatchBowlBalls'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'])['B'].cumsum()
    # data['MatchBowlWkt'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'])['Wkts'].cumsum()
    #
    # data['BallsRemaining'] = 120 - data['TeamBalls']
    #
    # # Apply DL models for different time periods (vectorized)
    # print("Applying DL models...")
    #
    # # Initialize columns
    # data["PredictedRemainingRuns_Smoothed"] = 0.0
    # data["ParInitial"] = 0.0
    #
    # # Default parameters
    # alpha_params, beta_params = params(dl_params_df)
    # mask_default = ~data['year'].isin(range(2008, 2022))
    # if mask_default.any():
    #     data.loc[mask_default, "PredictedRemainingRuns_Smoothed"] = apply_dl_vectorized(
    #         data.loc[mask_default], 'BallsRemaining', 'TeamWicket', alpha_params, beta_params)
    #     data.loc[mask_default, "ParInitial"] = apply_dl_vectorized(
    #         data.loc[mask_default], 'TeamBalls', 0, alpha_params, beta_params) * 0 + dl_model(120, 0, alpha_params, beta_params)
    #
    # # 2008-2013 parameters
    # alpha_params2, beta_params2 = params(dl_params_df2)
    # mask_2008_2013 = data['year'].isin(range(2008, 2014))
    # if mask_2008_2013.any():
    #     data.loc[mask_2008_2013, "PredictedRemainingRuns_Smoothed"] = apply_dl_vectorized(
    #         data.loc[mask_2008_2013], 'BallsRemaining', 'TeamWicket', alpha_params2, beta_params2)
    #     data.loc[mask_2008_2013, "ParInitial"] = dl_model(120, 0, alpha_params2, beta_params2)
    #
    # # 2014-2017 parameters
    # alpha_params3, beta_params3 = params(dl_params_df3)
    # mask_2014_2017 = data['year'].isin(range(2014, 2018))
    # if mask_2014_2017.any():
    #     data.loc[mask_2014_2017, "PredictedRemainingRuns_Smoothed"] = apply_dl_vectorized(
    #         data.loc[mask_2014_2017], 'BallsRemaining', 'TeamWicket', alpha_params3, beta_params3)
    #     data.loc[mask_2014_2017, "ParInitial"] = dl_model(120, 0, alpha_params3, beta_params3)
    #
    # # 2018-2021 parameters
    # alpha_params4, beta_params4 = params(dl_params_df4)
    # mask_2018_2021 = data['year'].isin(range(2018, 2022))
    # if mask_2018_2021.any():
    #     data.loc[mask_2018_2021, "PredictedRemainingRuns_Smoothed"] = apply_dl_vectorized(
    #         data.loc[mask_2018_2021], 'BallsRemaining', 'TeamWicket', alpha_params4, beta_params4)
    #     data.loc[mask_2018_2021, "ParInitial"] = dl_model(120, 0, alpha_params4, beta_params4)
    #
    # # Calculate derived metrics
    # print("Computing impact...")
    # data['TotalPredictedScore'] = data["PredictedRemainingRuns_Smoothed"] + data["TeamRuns"]
    #
    # # Impact calculation
    # data["Impact"] = data.groupby(["MatchNum", "TeamInns"])["TotalPredictedScore"].diff()
    #
    # # First ball impact
    # first_ball_mask = data.groupby(["MatchNum", "TeamInns"]).head(1).index
    # data.loc[first_ball_mask, "Impact"] = (
    #         data.loc[first_ball_mask, "TotalPredictedScore"] -
    #         data.loc[first_ball_mask, "ParInitial"]
    # )

    print("Data loading complete!")
    return data

# The main app function
def main():
    st.sidebar.title('True Values')

    format_choice = st.sidebar.selectbox('Select Format:', ['T20s', 'ODI'])
    if format_choice == 'T20s':
        # Load data with caching
        data = load_data('T20DataT20Leagues_optimized.parquet')  # Changed to parquet
    else:
        data = load_data('ODIData_optimized.parquet')  # Changed to parquet

    # data = load_data('T20DataT20Leagues_optimized.parquet')
    selected_leagues = st.sidebar.multiselect('Choose leagues:', data['CompName'].unique())


    if selected_leagues:
        data = data[data['CompName'].isin(selected_leagues)]

    choice0 = st.sidebar.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])


    # Selectors for user input
    options = ['Overall Stats', 'Season By Season']
    choice = st.sidebar.selectbox('Select your option:', options)
    choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])

    # User inputs for date range
    # start_date = st.sidebar.date_input('Start date', data['Date'].min())
    # end_date = st.sidebar.date_input('End date', data['Date'].max())
    valid_dates = data['Date'].dropna()
    # valid_dates = data
    import datetime
    if not valid_dates.empty:
        min_dt = valid_dates.min().date()
        max_dt = valid_dates.max().date()
    else:
        min_dt = datetime.date(2000, 1, 1)
        max_dt = datetime.date(2030, 1, 1)

    start_date = st.sidebar.date_input("Start date", min_value=min_dt, max_value=max_dt, value=min_dt)
    end_date = st.sidebar.date_input("End date", min_value=min_dt, max_value=max_dt, value=max_dt)

    # Filtering data based on the user's date selection
    if start_date > end_date:
        st.sidebar.error('Error: End date must be greater than start date.')
        return


    # Vectorized filtering
    filtered_data2 = data[
        (data['Date'] >= pd.to_datetime(start_date)) &
        (data['Date'] <= pd.to_datetime(end_date))
        ]

    if choice2 == 'Individual':
        if choice0 == 'Batting':
            players = data['Batter'].unique()
        else:
            players = data['Bowlers'].unique()
        player = st.sidebar.multiselect("Select Players:", players)
    choice3 = st.sidebar.multiselect('Pace or Spin:', ['Pace', 'Spin'])
    if choice3:
        filtered_data2 = filtered_data2[filtered_data2['BowlCat'].isin(choice3)]

    choice4 = st.sidebar.multiselect('Select Innings:', [1, 2])
    if choice4:
        filtered_data2 = filtered_data2[filtered_data2['TeamInns'].isin(choice4)]

    max_over = max((filtered_data2['over']).astype(int))
    start_over, end_over = st.sidebar.slider('Select Overs Range:', min_value=1, max_value=max_over, value=(1, max_over))
    filtered_data2 = filtered_data2[(filtered_data2['over'] >= start_over) & (filtered_data2['over'] <= end_over)]


    all_data = []

    # balls = max((filtered_data2['BatterBalls']).astype(int))
    # start_balls, end_balls = st.sidebar.slider('Select Balls Faced By Batter in Innings:', min_value=1, max_value=balls, value=(1, balls))
    #
    # filtered_data2 = filtered_data2[(filtered_data2['BatterBalls'] >= start_balls) & (filtered_data2['BatterBalls'] <= end_balls)]

    # Process years with better progress indication
    unique_years = sorted(filtered_data2['year'].unique())

    for i, year in enumerate(unique_years):
        if choice0 == 'Batting':
            results = analyze_data_for_year3(year, filtered_data2)
        else:
            results = analyze_data_for_year6(year, filtered_data2)
        all_data.append(results)

    combined_data = pd.concat(all_data, ignore_index=True)

    if choice0 == 'Batting':
        # Optimized final aggregation
        agg_cols = ['I', 'Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs','Impact']
        truevalues = combined_data.groupby(['Player','Batsman'])[agg_cols].sum().reset_index()
        final_results = truemetrics(truevalues)
        final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
    else:
        agg_cols = ['I', 'RC', 'BF', 'Out', 'Expected Runs', 'Expected Outs','Impact']
        truevalues = combined_data.groupby(['Player','Type'], observed=True)[agg_cols].sum().reset_index()
        final_results = truemetricsbowling(truevalues)
        final_results = final_results.sort_values(by=['Out'], ascending=False)


    if choice == 'Overall Stats':
        if choice2 == 'Individual':
            # Efficient player filtering
            valid_players = set(final_results['Player'].unique())
            temp = [p for p in player if p in valid_players]

            # Show invalid players
            invalid_players = [p for p in player if p not in valid_players]
            for invalid_player in invalid_players:
                st.sidebar.subheader(f'{invalid_player} not in this list')

            if temp:
                final_results = final_results[final_results['Player'].isin(temp)]

        if choice0 == 'Batting':
            final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
            drop_cols = ['Expected Runs', 'Expected Outs','Out Ratio','Expected Ave','Expected SR']
            final_results = final_results.drop(columns=drop_cols)
            # Clean up columns for output
            run = max((final_results['Runs Scored']).astype(int))

            start_runs, end_runs = st.sidebar.slider('Select Minimum Runs Scored:', min_value=0, max_value=run, value=(1, run))
            final_results = final_results[(final_results['Runs Scored'] >= start_runs) & (final_results['Runs Scored'] <= end_runs)]
            balls = max((final_results['BF']).astype(int))
            start_balls, end_balls = st.sidebar.slider('Select Minimum BF:', min_value=1, max_value=balls, value=(1, balls))

            final_results = final_results[(final_results['BF'] >= start_balls) & (final_results['BF'] <= end_balls)]
            st.dataframe(final_results.round(2))
        else:
            final_results = final_results.sort_values(by=['Out'], ascending=False)
            final_results = final_results.drop(columns=['Expected Runs','Expected Outs','Expected Econ','Expected SR',])

            # Clean up columns for output
            outs = max((final_results['Out']).astype(int))

            start_runs, end_runs = st.sidebar.slider('Select Wickets:', min_value=0, max_value=outs, value=(1, outs))
            final_results = final_results[(final_results['Out'] >= start_runs) & (final_results['Out'] <= end_runs)]

            balls = max((final_results['BF']).astype(int))
            start_balls, end_balls = st.sidebar.slider('Select Minimum BF:', min_value=1, max_value=balls, value=(1, balls))

            final_results = final_results[(final_results['BF'] >= start_balls) & (final_results['BF'] <= end_balls)]
            st.dataframe(final_results.round(2))

    elif choice == 'Season By Season':
        if choice2 == 'Individual':
            # Efficient player filtering
            valid_players = set(combined_data['Player'].unique())
            temp = [p for p in player if p in valid_players]

            # Show invalid players
            invalid_players = [p for p in player if p not in valid_players]
            for invalid_player in invalid_players:
                st.sidebar.subheader(f'{invalid_player} not in this list')

            if temp:
                combined_data = combined_data[combined_data['Player'].isin(temp)]

        if choice0 == 'Batting':
            combined_data = combined_data.sort_values(by=['Runs Scored'], ascending=False)
            drop_cols = ['Expected Runs', 'Expected Outs','Out Ratio','Expected Ave','Expected SR']
            combined_data = combined_data.drop(columns=drop_cols)
            # Clean up columns for output
            run = max((combined_data['Runs Scored']).astype(int))

            start_runs, end_runs = st.sidebar.slider('Select Minimum Runs Scored:', min_value=0, max_value=run, value=(1, run))
            combined_data = combined_data[(combined_data['Runs Scored'] >= start_runs) & (combined_data['Runs Scored'] <= end_runs)]
            balls = max((combined_data['BF']).astype(int))
            start_balls, end_balls = st.sidebar.slider('Select Minimum BF:', min_value=1, max_value=balls, value=(1, balls))

            combined_data = combined_data[(combined_data['BF'] >= start_balls) & (combined_data['BF'] <= end_balls)]
            st.dataframe(combined_data.round(2))
        else:
            combined_data = combined_data.sort_values(by=['Out'], ascending=False)
            combined_data = combined_data.drop(columns=['Expected Runs','Expected Outs','Expected Econ'])

            # Clean up columns for output
            outs = max((combined_data['Out']).astype(int))

            start_runs, end_runs = st.sidebar.slider('Select Wickets:', min_value=0, max_value=outs, value=(1, outs))
            combined_data = combined_data[(combined_data['Out'] >= start_runs) & (combined_data['Out'] <= end_runs)]

            balls = max((combined_data['BF']).astype(int))
            start_balls, end_balls = st.sidebar.slider('Select Minimum BF:', min_value=1, max_value=balls, value=(1, balls))

            combined_data = combined_data[(combined_data['BF'] >= start_balls) & (combined_data['BF'] <= end_balls)]
            st.dataframe(combined_data.round(2))

# Run the main function
if __name__ == '__main__':
    main()