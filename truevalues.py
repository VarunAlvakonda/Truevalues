# import numpy as np
# import pandas as pd
# import streamlit as st
# from scipy.optimize import curve_fit
#
# # place = 'Venue_x'
# place = 'Country'
# type = 'PhaseofSeason'
# type = 'BowlCat'
# type = 'entryphase'
#
# def cubic_poly(w, a, b, c, d):
#     return a * w**3 + b * w**2 + c * w + d
#
# def truemetrics(truevalues):
#     truevalues['Ave'] = truevalues['Runs Scored'] / truevalues['Out']
#     truevalues['SR'] = (truevalues['Runs Scored'] / truevalues['BF'] * 100)
#     truevalues.loc[truevalues['Out']==0,'Ave']= truevalues['Runs Scored']
#     truevalues['Expected Ave'] = truevalues['Expected Runs'] / truevalues['Expected Outs']
#     truevalues['Expected SR'] = (truevalues['Expected Runs'] / truevalues['BF'] * 100)
#
#     # Calculate 'True Ave' and 'True SR' for the final results
#     truevalues['True Ave'] = (truevalues['Ave'] - truevalues['Expected Ave'])
#     truevalues['True SR'] = (truevalues['SR'] - truevalues['Expected SR'])
#
#     truevalues['Out Ratio'] = (truevalues['Expected Outs'] / truevalues['Out'])
#     # truevalues['Impact/Inns'] = (truevalues['Impact'] / truevalues['I'])
#     return truevalues
#
# def calculate_entry_point_all_years(data):
#     # Vectorized approach
#     first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter']).copy()
#
#     # Vectorized conversion - much faster than apply
#     over_vals = first_appearance['Over'].values
#     first_appearance['total_deliveries'] = (over_vals.astype(int) * 6 +
#                                             ((over_vals - over_vals.astype(int)) * 10).astype(int))
#
#     # Vectorized average calculation
#     avg_entry_point_deliveries = first_appearance.groupby('Batter')['total_deliveries'].median().reset_index()
#
#     # Vectorized conversion back to overs
#     deliveries = avg_entry_point_deliveries['total_deliveries'].values
#     avg_entry_point_deliveries['average_over'] = np.round((deliveries // 6) + (deliveries % 6) / 10, 1)
#
#     return avg_entry_point_deliveries[['Batsman','Batter', 'average_over']], first_appearance
#
# def calculate_first_appearance(data):
#     # Optimized version
#     first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter']).copy()
#
#     # Vectorized conversion
#     over_vals = first_appearance['Over'].values
#     first_appearance['total_deliveries'] = (over_vals.astype(int) * 6 +
#                                             ((over_vals - over_vals.astype(int)) * 10).astype(int))
#
#     avg_entry_point_deliveries = first_appearance.groupby(['Batsman','Batter', 'year'])['total_deliveries'].median().reset_index()
#
#     # Vectorized conversion back
#     deliveries = avg_entry_point_deliveries['total_deliveries'].values
#     avg_entry_point_deliveries['average_over'] = np.round((deliveries // 6) + (deliveries % 6) / 10, 1)
#
#     return avg_entry_point_deliveries[['Batsman','Batter', 'average_over']]
#
# def analyze_data_for_year2(data):
#     year_data = data.copy()
#     first_appearance_data = calculate_first_appearance(year_data)
#
#     if 'analysis_results' in locals() or 'analysis_results' in globals():
#         analysis_results = pd.merge(year_data, first_appearance_data, on=['Batter'], how='left')
#     else:
#         analysis_results = first_appearance_data
#
#     return analysis_results
#
# def analyze_data_for_year3(year2, data2):
#     # Early filtering
#     combineddata = data2[(data2['TeamInns'] < 3) & (data2['year'] == year2)]
#
#     # Optimized innings calculation
#     inns = combineddata.groupby(['Batsman','Batter', 'MatchNum'])[['Runs']].sum().reset_index()
#     inns['I'] = 1
#     inns2 = inns.groupby(['Batsman','Batter'])[['I']].sum().reset_index()
#     inns2.columns = ['Batsman','Player', 'I']
#     inns['CI'] = inns.groupby(['Batter'])[['I']].cumsum()
#
#     # Vectorized entry point analysis
#     # analysis_results = analyze_data_for_year2(combineddata)
#     # analysis_results.columns = ['Player', 'Median Entry Point']
#
#     # Optimized dismissal data processing
#     valid = ['X','WX']
#     dismissed_mask = combineddata['Notes'].isin(valid)
#     dismissed_data = combineddata[dismissed_mask]
#     dismissed_data['Out'] = 1
#
#     # More efficient merge
#     merge_cols = ['MatchNum','TeamInns', 'Batsman','Batter', 'Notes','over']
#     combineddata = pd.merge(
#         combineddata,
#         dismissed_data[merge_cols + ['Out']],
#         on=merge_cols,
#         how='left'
#     ).fillna({'Out': 0})
#
#     # Vectorized groupby operations
#     groupby_cols_player = ['Batsman','Batter', 'TeamInns', place, 'over']
#     groupby_cols_over = ['TeamInns', place,'over']
#
#     player_outs = dismissed_data.groupby(groupby_cols_player)[['Out']].sum().reset_index()
#     player_outs.columns = ['Batsman','Player', 'TeamInns', place, 'Over', 'Out']
#
#     over_outs = dismissed_data.groupby(groupby_cols_over)[['Out']].sum().reset_index()
#     over_outs.columns = ['TeamInns', place, 'Over', 'Outs']
#
#     player_runs = combineddata.groupby(groupby_cols_player)[['Runs', 'B','Impact']].sum().reset_index()
#     player_runs.columns = ['Batsman','Player', 'TeamInns', place, 'Over', 'Runs Scored', 'BF','Impact']
#
#     over_runs = combineddata.groupby(groupby_cols_over)[['Runs', 'B']].sum().reset_index()
#     over_runs.columns = ['TeamInns', place, 'Over', 'Runs', 'B']
#
#     # Sequential merges (more memory efficient)
#     combined_df = pd.merge(player_runs, player_outs, on=['Batsman','Player', 'TeamInns', place, 'Over'], how='left')
#     combined_df2 = pd.merge(over_runs, over_outs, on=['TeamInns', place, 'Over'], how='left')
#     combined_df3 = pd.merge(combined_df, combined_df2, on=['TeamInns', place, 'Over'], how='left')
#
#     # Vectorized null handling and calculations
#     combined_df3 = combined_df3.fillna({'Outs': 0, 'Out': 0})
#
#     # Vectorized arithmetic operations
#     combined_df3['Over_Runs'] = combined_df3['Runs'] - combined_df3['Runs Scored']
#     combined_df3['Over_B'] = combined_df3['B'] - combined_df3['BF']
#     combined_df3['Over_Outs'] = combined_df3['Outs'] - combined_df3['Out']
#
#     # Avoid division by zero with vectorized operations
#     combined_df3['BSR'] = np.divide(combined_df3['Over_Runs'], combined_df3['Over_B'],
#                                     out=np.zeros_like(combined_df3['Over_Runs']),
#                                     where=combined_df3['Over_B']!=0)
#     combined_df3['OPB'] = np.divide(combined_df3['Over_Outs'], combined_df3['Over_B'],
#                                     out=np.zeros_like(combined_df3['Over_Outs']),
#                                     where=combined_df3['Over_B']!=0)
#
#     # Vectorized expected calculations
#     combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
#     combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']
#
#     # Vectorized phase calculations
#     ball_bins2 = [0, 6,11, 16, 20]
#     ball_labels2 = ['1 to 6', '7 to 11','12 to 16', '17 to 20']
#     combined_df3['phase'] = pd.cut(combined_df3['Over'], bins=ball_bins2,
#                                    labels=ball_labels2, include_lowest=True, right=True)
#
#     # Optimized aggregation
#     agg_cols = ['Runs Scored', 'BF', 'Out','Expected Runs', 'Expected Outs','Impact']
#     truevalues = combined_df3.groupby(['Player','Batsman'], observed=True)[agg_cols].sum().reset_index()
#
#     final_results = truemetrics(truevalues)
#
#     # Efficient final merges
#     players_years = combineddata[['Batsman','Batter','year']].drop_duplicates()
#     players_years.columns = ['Batsman','Player','Year']
#
#     final_results2 = pd.merge(inns2, final_results, on=['Batsman','Player'], how='left')
#     final_results3 = pd.merge(players_years, final_results2, on=['Batsman','Player'], how='left')
#     # final_results4 = pd.merge(final_results3, analysis_results, on='Batsman','Player', how='left')
#
#     return final_results3.round(2)
#
# def truemetricsbowling(truevalues):
#     # Avoid division by zero with vectorized operations
#     truevalues['Econ'] = np.divide(truevalues['RC'], truevalues['BF'],
#                                    out=np.zeros_like(truevalues['RC']),
#                                    where=truevalues['BF']!=0) * 6
#     truevalues['SR'] = np.divide(truevalues['BF'], truevalues['Out'],
#                                  out=np.zeros_like(truevalues['BF']),
#                                  where=truevalues['Out']!=0)
#     truevalues['Expected Econ'] = np.divide(truevalues['Expected Runs'], truevalues['BF'],
#                                             out=np.zeros_like(truevalues['Expected Runs']),
#                                             where=truevalues['BF']!=0) * 6
#     truevalues['Expected SR'] = np.divide(truevalues['BF'], truevalues['Expected Outs'],
#                                           out=np.zeros_like(truevalues['BF']),
#                                           where=truevalues['Expected Outs']!=0)
#
#     truevalues['True Econ'] = truevalues['Expected Econ'] - truevalues['Econ']
#     truevalues['True Wickets'] = truevalues['Out'] - truevalues['Expected Outs']
#     truevalues['True W/ 4 overs'] = np.divide(truevalues['True Wickets'], (truevalues['BF'] / 24),
#                                               out=np.zeros_like(truevalues['True Wickets']),
#                                               where=truevalues['BF']!=0)
#     truevalues['True W/ 10 overs'] = np.divide(truevalues['True Wickets'], (truevalues['BF'] / 60),
#                                               out=np.zeros_like(truevalues['True Wickets']),
#                                               where=truevalues['BF']!=0)
#     # truevalues['Impact/Inns'] = np.divide(truevalues['Impact'], (truevalues['Inns']),
#     #                                       out=np.zeros_like(truevalues['Impact']),
#     #                                       where=truevalues['Inns']!=0)
#     return truevalues
#
# def analyze_data_for_year6(year2, data2):
#     print(f"Processing year {year2} (bowling analyze_6)...")
#
#     # Early filtering
#     combineddata = data2[(data2['TeamInns'] < 3) & (data2['year'] == year2)]
#
#     # Optimized innings calculation
#     inns = combineddata.groupby(['Bowlers','Bowler','MatchNum'], observed=True)[['Runs']].sum().reset_index()
#     inns['I'] = 1
#     inns2 = inns.groupby(['Bowlers','Bowler'], observed=True)[['I']].sum().reset_index()
#     inns2.columns = ['Player','BowlNum','I']
#     inns['CI'] = inns.groupby(['Bowlers'], observed=True)[['I']].cumsum()
#
#     # Vectorized entry point analysis
#     # analysis_results = analyze_data_for_year2(combineddata)
#     # analysis_results.columns = ['Player', 'Median Entry Point']
#
#     # Optimized dismissal data processing
#     valid = ['X' ,'XC','XT' , 'XU','XSUTC', 'NX' ,'LX' ,'NXT', 'XZ','XP','PX','WX']
#     dismissed_mask = (combineddata['Notes'].isin(valid) &
#                       (combineddata['BowlDis'] == 'Y') &
#                       (combineddata['LongDis'] != 'run out'))
#     dismissed_data = combineddata[dismissed_mask]
#     dismissed_data['Out'] = 1
#
#     # More efficient merge
#     merge_cols = ['MatchNum','TeamInns',place,'Bowlers','Bowler', 'Notes','over']
#     combineddata = pd.merge(
#         combineddata,
#         dismissed_data[merge_cols + ['Out']],
#         on=merge_cols,
#         how='left'
#     ).fillna({'Out': 0})
#
#     combineddata = combineddata.drop_duplicates()
#
#     # Vectorized groupby operations
#     player_outs = dismissed_data.groupby(['Bowlers','Bowler', place,'over'], observed=True)[['Out']].sum().reset_index()
#     player_outs.columns = ['Player','BowlNum', place,'Over', 'Out']
#
#     over_outs = dismissed_data.groupby([place,'over'], observed=True)[['Out']].sum().reset_index()
#     over_outs.columns = [place,'Over', 'Outs']
#
#     player_runs = combineddata.groupby(['Bowlers','Bowler', place,'over'], observed=True)[['RC', 'B','Impact']].sum().reset_index()
#     player_runs.columns = ['Player','BowlNum',place, 'Over', 'RC', 'BF','Impact']
#
#     over_runs = combineddata.groupby([place,'over'], observed=True)[['RC', 'B']].sum().reset_index()
#     over_runs.columns = [place,'Over', 'Runs', 'B']
#
#     # Sequential merges
#     combined_df = pd.merge(player_runs, player_outs, on=['Player','BowlNum', place,'Over'], how='left')
#     combined_df2 = pd.merge(over_runs, over_outs, on=[place,'Over'], how='left')
#     combined_df3 = pd.merge(combined_df, combined_df2, on=[place,'Over'], how='left')
#
#     # Vectorized null handling and calculations
#     combined_df3 = combined_df3.fillna({'Outs': 0, 'Out': 0})
#
#     # Vectorized arithmetic operations
#     combined_df3['Over_Runs'] = combined_df3['Runs'] - combined_df3['RC']
#     combined_df3['Over_B'] = combined_df3['B'] - combined_df3['BF']
#     combined_df3['Over_Outs'] = combined_df3['Outs'] - combined_df3['Out']
#
#     # Safe division operations
#     combined_df3['BSR'] = np.divide(combined_df3['Over_Runs'], combined_df3['Over_B'],
#                                     out=np.zeros_like(combined_df3['Over_Runs']),
#                                     where=combined_df3['Over_B']!=0)
#     combined_df3['OPB'] = np.divide(combined_df3['Over_Outs'], combined_df3['Over_B'],
#                                     out=np.zeros_like(combined_df3['Over_Outs']),
#                                     where=combined_df3['Over_B']!=0)
#
#     # Vectorized expected calculations
#     combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
#     combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']
#
#     # Vectorized phase calculations
#     ball_bins2 = [0, 6,11, 16, 20]
#     ball_labels2 = ['1 to 6', '7 to 11','12 to 16', '17 to 20']
#     combined_df3['phase'] = pd.cut(combined_df3['Over'], bins=ball_bins2,
#                                    labels=ball_labels2, include_lowest=True, right=True)
#
#     # Optimized aggregation
#     agg_cols = ['RC', 'BF', 'Out','Expected Runs', 'Expected Outs','Impact']
#     truevalues = combined_df3.groupby(['Player','BowlNum',], observed=True)[agg_cols].sum().reset_index()
#
#     final_results = truemetricsbowling(truevalues)
#
#     # Efficient final merges
#     players_years = combineddata[['Bowlers','Bowler', 'BowlCat','year']].drop_duplicates()
#     players_years.columns = ['Player','BowlNum','Type','Year']
#
#     final_results2 = pd.merge(inns2, final_results, on=['Player','BowlNum',], how='left')
#     final_results3 = pd.merge(players_years, final_results2, on=['Player','BowlNum',], how='left')
#     # final_results4 = pd.merge(final_results3, analysis_results, on='Player', how='left')
#     # final_results3['Year'] = year2
#
#     return final_results3.round(2)
#
# @st.cache_data
# def load_data2(filename):
#
#     return pd.read_csv(filename)  # Changed to parquet
#
# # Vectorized DL model application
# def apply_dl_vectorized(df, balls_col, wickets_param, alpha_p, beta_p):
#     """Apply DL model vectorized - wickets_param can be column name (str) or constant (int)"""
#     balls = df[balls_col].values
#
#     if isinstance(wickets_param, str):
#         # It's a column name
#         wickets = df[wickets_param].values
#     else:
#         # It's a constant value (like 0)
#         wickets = np.full(len(balls), wickets_param)
#
#     alpha = cubic_poly(wickets, *alpha_p)
#     beta = cubic_poly(wickets, *beta_p)
#
#     return alpha * (1 - np.exp(-balls / beta))
#
# # Load the data with optimizations
# @st.cache_data
# def load_data(filename):
#     data = pd.read_parquet(filename)
#     return data
#
# # The main app function
# def main():
#     st.sidebar.title('True Values')
#
#     format_choice = st.sidebar.selectbox('Select Format:', ['T20s', 'ODI','WT20s','WODI'])
#     if format_choice == 'T20s':
#         # Load data with caching
#         data = load_data('T20DataT20Leagues_optimized.parquet')  # Changed to parquet
#     elif format_choice == 'ODI':
#         data = load_data('ODIData_optimized.parquet')  # Changed to parquet
#     elif format_choice == 'WT20s':
#         data = load_data('WT20DataT20Leagues_optimized.parquet')
#     else:
#         data = load_data('WODIData_optimized.parquet')
#     # data = load_data('T20DataT20Leagues_optimized.parquet')
#     selected_leagues = st.sidebar.multiselect('Choose Competitions:', data['CompName'].unique())
#
#     global place
#     if format_choice == 'ODI':
#         place = 'Country'
#     elif format_choice == 'T20s' and selected_leagues and 'Twenty20 International' not in selected_leagues:
#         place = 'Venue_x'
#     else:
#         place = 'Country'  # Default for WT20s and WODI
#
#     if selected_leagues:
#         data = data[data['CompName'].isin(selected_leagues)]
#
#     choice0 = st.sidebar.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])
#
#
#     # Selectors for user input
#     options = ['Overall Stats', 'Season By Season']
#     choice = st.sidebar.selectbox('Select your option:', options)
#     choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
#
#     # User inputs for date range
#     # start_date = st.sidebar.date_input('Start date', data['Date'].min())
#     # end_date = st.sidebar.date_input('End date', data['Date'].max())
#     valid_dates = data['Date'].dropna()
#     # valid_dates = data
#     import datetime
#     if not valid_dates.empty:
#         min_dt = valid_dates.min().date()
#         max_dt = valid_dates.max().date()
#     else:
#         min_dt = datetime.date(2000, 1, 1)
#         max_dt = datetime.date(2030, 1, 1)
#
#     start_date = st.sidebar.date_input("Start date", min_value=min_dt, max_value=max_dt, value=min_dt)
#     end_date = st.sidebar.date_input("End date", min_value=min_dt, max_value=max_dt, value=max_dt)
#
#     # Filtering data based on the user's date selection
#     if start_date > end_date:
#         st.sidebar.error('Error: End date must be greater than start date.')
#         return
#
#
#     # Vectorized filtering
#     filtered_data2 = data[
#         (data['Date'] >= pd.to_datetime(start_date)) &
#         (data['Date'] <= pd.to_datetime(end_date))
#         ]
#
#     if choice2 == 'Individual':
#         if choice0 == 'Batting':
#             players = data['Batter'].unique()
#         else:
#             players = data['Bowlers'].unique()
#         player = st.sidebar.multiselect("Select Players:", players)
#     choice3 = st.sidebar.multiselect('Pace or Spin:', ['Pace', 'Spin'])
#     if choice3:
#         filtered_data2 = filtered_data2[filtered_data2['BowlCat'].isin(choice3)]
#
#     choice4 = st.sidebar.multiselect('Select Innings:', [1, 2])
#     if choice4:
#         filtered_data2 = filtered_data2[filtered_data2['TeamInns'].isin(choice4)]
#
#     max_over = max((filtered_data2['over']).astype(int))
#     start_over, end_over = st.sidebar.slider('Select Overs Range:', min_value=1, max_value=max_over, value=(1, max_over))
#     filtered_data2 = filtered_data2[(filtered_data2['over'] >= start_over) & (filtered_data2['over'] <= end_over)]
#
#
#     all_data = []
#
#     # balls = max((filtered_data2['BatterBalls']).astype(int))
#     # start_balls, end_balls = st.sidebar.slider('Select Balls Faced By Batter in Innings:', min_value=1, max_value=balls, value=(1, balls))
#     #
#     # filtered_data2 = filtered_data2[(filtered_data2['BatterBalls'] >= start_balls) & (filtered_data2['BatterBalls'] <= end_balls)]
#
#     # Process years with better progress indication
#     unique_years = sorted(filtered_data2['year'].unique())
#     # Process years with better progress indication
#     unique_years = sorted(filtered_data2['year'].unique())
#
#     # Use form to keep sliders persistent
#     with st.sidebar.form("results_form"):
#         show_results = st.form_submit_button('Show Results')
#
#         # Initialize variables to store processed data
#         if show_results:
#             all_data = []
#
#             for i, year in enumerate(unique_years):
#                 if choice0 == 'Batting':
#                     results = analyze_data_for_year3(year, filtered_data2)
#                 else:
#                     results = analyze_data_for_year6(year, filtered_data2)
#                 all_data.append(results)
#
#             combined_data = pd.concat(all_data, ignore_index=True)
#
#             if choice0 == 'Batting':
#                 # Optimized final aggregation
#                 agg_cols = ['I', 'Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs','Impact']
#                 truevalues = combined_data.groupby(['Player','Batsman'])[agg_cols].sum().reset_index()
#                 final_results = truemetrics(truevalues)
#                 final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
#             else:
#                 agg_cols = ['I', 'RC', 'BF', 'Out', 'Expected Runs', 'Expected Outs','Impact']
#                 truevalues = combined_data.groupby(['Player','BowlNum','Type'], observed=True)[agg_cols].sum().reset_index()
#                 final_results = truemetricsbowling(truevalues)
#                 final_results = final_results.sort_values(by=['Out'], ascending=False)
#
#             if choice == 'Overall Stats':
#                 if choice2 == 'Individual':
#                     # Efficient player filtering
#                     valid_players = set(final_results['Player'].unique())
#                     temp = [p for p in player if p in valid_players]
#
#                     # Show invalid players
#                     invalid_players = [p for p in player if p not in valid_players]
#                     for invalid_player in invalid_players:
#                         st.sidebar.write(f'{invalid_player} not in this list')
#
#                     if temp:
#                         final_results = final_results[final_results['Player'].isin(temp)]
#
#                 if choice0 == 'Batting':
#                     final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
#                     drop_cols = ['Expected Runs', 'Expected Outs','Out Ratio','Expected Ave','Expected SR']
#                     final_results = final_results.drop(columns=drop_cols)
#
#                     # Get max values for sliders
#                     run = max((final_results['Runs Scored']).astype(int))
#                     balls = max((final_results['BF']).astype(int))
#
#                     # Sliders inside form - will persist
#                     start_runs, end_runs = st.slider('Select Minimum Runs Scored:',
#                                                      min_value=0, max_value=run, value=(1, run))
#                     start_balls, end_balls = st.slider('Select Minimum BF:',
#                                                        min_value=1, max_value=balls, value=(1, balls))
#
#                     # Apply filters
#                     final_results = final_results[(final_results['Runs Scored'] >= start_runs) & (final_results['Runs Scored'] <= end_runs)]
#                     final_results = final_results[(final_results['BF'] >= start_balls) & (final_results['BF'] <= end_balls)]
#                     final_results['Impact/Inns'] = final_results['Impact']/final_results['I']
#
#                 else:
#                     final_results = final_results.sort_values(by=['Out'], ascending=False)
#                     final_results = final_results.drop(columns=['Expected Runs','Expected Outs','Expected Econ','Expected SR'])
#
#                     # Get max values for sliders
#                     outs = max((final_results['Out']).astype(int))
#                     balls = max((final_results['BF']).astype(int))
#
#                     # Sliders inside form - will persist
#                     start_runs, end_runs = st.slider('Select Wickets:',
#                                                      min_value=0, max_value=outs, value=(1, outs))
#                     start_balls, end_balls = st.slider('Select Minimum BF:',
#                                                        min_value=1, max_value=balls, value=(1, balls))
#
#                     # Apply filters
#                     final_results = final_results[(final_results['Out'] >= start_runs) & (final_results['Out'] <= end_runs)]
#                     final_results = final_results[(final_results['BF'] >= start_balls) & (final_results['BF'] <= end_balls)]
#                     final_results['Impact/Inns'] = final_results['Impact']/final_results['I']
#
#             elif choice == 'Season By Season':
#                 if choice2 == 'Individual':
#                     # Efficient player filtering
#                     valid_players = set(combined_data['Player'].unique())
#                     temp = [p for p in player if p in valid_players]
#
#                     # Show invalid players
#                     invalid_players = [p for p in player if p not in valid_players]
#                     for invalid_player in invalid_players:
#                         st.sidebar.write(f'{invalid_player} not in this list')
#
#                     if temp:
#                         combined_data = combined_data[combined_data['Player'].isin(temp)]
#
#                 if choice0 == 'Batting':
#                     combined_data = combined_data.sort_values(by=['Year'], ascending=False)
#                     drop_cols = ['Expected Runs', 'Expected Outs','Out Ratio','Expected Ave','Expected SR']
#                     combined_data = combined_data.drop(columns=drop_cols)
#
#                     # Get max values for sliders
#                     run = max((combined_data['Runs Scored']).astype(int))
#                     balls = max((combined_data['BF']).astype(int))
#
#                     # Sliders inside form - will persist
#                     start_runs, end_runs = st.slider('Select Minimum Runs Scored:',
#                                                      min_value=0, max_value=run, value=(1, run))
#                     start_balls, end_balls = st.slider('Select Minimum BF:',
#                                                        min_value=1, max_value=balls, value=(1, balls))
#
#                     # Apply filters
#                     combined_data = combined_data[(combined_data['Runs Scored'] >= start_runs) & (combined_data['Runs Scored'] <= end_runs)]
#                     combined_data = combined_data[(combined_data['BF'] >= start_balls) & (combined_data['BF'] <= end_balls)]
#                     combined_data['Impact/Inns'] = combined_data['Impact']/combined_data['I']
#
#                 else:
#                     combined_data = combined_data.sort_values(by=['Year'], ascending=False)
#                     combined_data = combined_data.drop(columns=['Expected Runs','Expected Outs','Expected Econ'])
#
#                     # Get max values for sliders
#                     outs = max((combined_data['Out']).astype(int))
#                     balls = max((combined_data['BF']).astype(int))
#
#                     # Sliders inside form - will persist
#                     start_runs, end_runs = st.slider('Select Wickets:',
#                                                      min_value=0, max_value=outs, value=(1, outs))
#                     start_balls, end_balls = st.slider('Select Minimum BF:',
#                                                        min_value=1, max_value=balls, value=(1, balls))
#
#                     # Apply filters
#                     combined_data = combined_data[(combined_data['Out'] >= start_runs) & (combined_data['Out'] <= end_runs)]
#                     combined_data = combined_data[(combined_data['BF'] >= start_balls) & (combined_data['BF'] <= end_balls)]
#                     combined_data['Impact/Inns'] = combined_data['Impact']/combined_data['I']
#
#     # Display results outside the form
#     if show_results:
#         if choice == 'Overall Stats':
#             st.dataframe(final_results.round(2))
#         elif choice == 'Season By Season':
#             st.dataframe(combined_data.round(2))
#
# # Run the main function
# if __name__ == '__main__':
#     main()

import numpy as np
import polars as pl
import streamlit as st
from scipy.optimize import curve_fit

# Global variables
place = 'Venue_x'
place = 'Country'
type_col = 'PhaseofSeason'

def cubic_poly(w, a, b, c, d):
    return a * w**3 + b * w**2 + c * w + d

def truemetrics(truevalues):
    """Calculate true metrics for batting with proper handling of division by zero"""
    truevalues = truevalues.with_columns([
        # Average calculation - handle zero outs
        pl.when(pl.col('Out') == 0)
        .then(pl.col('Runs Scored'))
        .otherwise(pl.col('Runs Scored') / pl.col('Out'))
        .alias('Ave'),

        # Strike Rate
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise((pl.col('Runs Scored') / pl.col('BF')) * 100)
        .alias('SR'),

        # Expected Average
        pl.when(pl.col('Expected Outs') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Expected Runs') / pl.col('Expected Outs'))
        .alias('Expected Ave'),

        # Expected Strike Rate
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise((pl.col('Expected Runs') / pl.col('BF')) * 100)
        .alias('Expected SR')
    ])

    # Calculate True metrics
    truevalues = truevalues.with_columns([
        (pl.col('Ave') - pl.col('Expected Ave')).alias('True Ave'),
        (pl.col('SR') - pl.col('Expected SR')).alias('True SR'),

        # Out Ratio - handle zero outs
        pl.when(pl.col('Out') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Expected Outs') / pl.col('Out'))
        .alias('Out Ratio')
    ])

    return truevalues

def truemetricsbowling(truevalues):
    """Calculate true metrics for bowling with proper handling of division by zero"""
    truevalues = truevalues.with_columns([
        # Economy rate
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise((pl.col('RC') / pl.col('BF')) * 6)
        .alias('Econ'),

        # Strike Rate
        pl.when(pl.col('Out') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('BF') / pl.col('Out'))
        .alias('SR'),

        # Expected Economy
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise((pl.col('Expected Runs') / pl.col('BF')) * 6)
        .alias('Expected Econ'),

        # Expected Strike Rate
        pl.when(pl.col('Expected Outs') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('BF') / pl.col('Expected Outs'))
        .alias('Expected SR')
    ])

    # Calculate True metrics
    truevalues = truevalues.with_columns([
        (pl.col('Expected Econ') - pl.col('Econ')).alias('True Econ'),
        (pl.col('Out') - pl.col('Expected Outs')).alias('True Wickets'),

        # True W/ 4 overs
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('True Wickets') / (pl.col('BF') / 24))
        .alias('True W/ 4 overs'),

        # True W/ 10 overs
        pl.when(pl.col('BF') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('True Wickets') / (pl.col('BF') / 60))
        .alias('True W/ 10 overs')
    ])

    return truevalues

def calculate_entry_point_all_years(data):
    """Calculate entry point statistics using vectorized operations"""
    # Get first appearance per match
    first_appearance = data.unique(subset=['MatchNum', 'TeamInns', 'Batter'], keep='first')

    # Vectorized conversion to total deliveries
    first_appearance = first_appearance.with_columns([
        ((pl.col('Over').cast(pl.Int64) * 6) +
         ((pl.col('Over') - pl.col('Over').cast(pl.Int64)) * 10).cast(pl.Int64))
        .alias('total_deliveries')
    ])

    # Calculate median entry point
    avg_entry_point_deliveries = (
        first_appearance
        .group_by(['Batsman', 'Batter'])
        .agg(pl.col('total_deliveries').median())
    )

    # Convert back to overs
    avg_entry_point_deliveries = avg_entry_point_deliveries.with_columns([
        ((pl.col('total_deliveries') // 6) +
         (pl.col('total_deliveries') % 6) / 10)
        .round(1)
        .alias('average_over')
    ])

    return avg_entry_point_deliveries.select(['Batsman', 'Batter', 'average_over']), first_appearance

def calculate_first_appearance(data):
    """Calculate first appearance for each year"""
    first_appearance = data.unique(subset=['MatchNum', 'TeamInns', 'Batter'], keep='first')

    # Vectorized conversion
    first_appearance = first_appearance.with_columns([
        ((pl.col('Over').cast(pl.Int64) * 6) +
         ((pl.col('Over') - pl.col('Over').cast(pl.Int64)) * 10).cast(pl.Int64))
        .alias('total_deliveries')
    ])

    avg_entry_point_deliveries = (
        first_appearance
        .group_by(['Batsman', 'Batter', 'year'])
        .agg(pl.col('total_deliveries').median())
    )

    # Convert back to overs
    avg_entry_point_deliveries = avg_entry_point_deliveries.with_columns([
        ((pl.col('total_deliveries') // 6) +
         (pl.col('total_deliveries') % 6) / 10)
        .round(1)
        .alias('average_over')
    ])

    return avg_entry_point_deliveries.select(['Batsman', 'Batter', 'average_over'])

def analyze_data_for_year2(data):
    """Wrapper for first appearance calculation"""
    year_data = data.clone()
    first_appearance_data = calculate_first_appearance(year_data)
    return first_appearance_data

def analyze_data_for_year3(year2, data2):
    """Analyze batting data for a specific year - Polars version"""
    print(f"Processing year {year2} (batting analyze_3)...")

    # Early filtering
    combineddata = data2.filter(
        (pl.col('TeamInns') < 3) & (pl.col('year') == year2)
    )

    # Calculate innings
    inns = (
        combineddata
        .group_by(['Batsman', 'Batter', 'MatchNum'])
        .agg(pl.col('Runs').sum())
        .with_columns(pl.lit(1).alias('I'))
    )

    inns2 = (
        inns
        .group_by(['Batsman', 'Batter'])
        .agg(pl.col('I').sum())
        .select([
            pl.col('Batsman'),
            pl.col('Batter').alias('Player'),
            pl.col('I')
        ])
    )

    # Cumulative innings
    inns = inns.with_columns(
        pl.col('I').cum_sum().over('Batter').alias('CI')
    )

    # Dismissal data
    valid = ['X', 'WX']
    dismissed_data = combineddata.filter(pl.col('Notes').is_in(valid))
    dismissed_data = dismissed_data.with_columns(pl.lit(1).alias('Out'))

    # Merge dismissal data
    merge_cols = ['MatchNum', 'TeamInns', 'Batsman', 'Batter', 'Notes', 'over']
    combineddata = combineddata.join(
        dismissed_data.select(merge_cols + ['Out']),
        on=merge_cols,
        how='left'
    ).with_columns(
        pl.col('Out').fill_null(0)
    )

    # Player-level aggregations
    groupby_cols_player = ['Batsman', 'Batter', 'TeamInns', place, 'over']

    player_outs = (
        dismissed_data
        .group_by(groupby_cols_player)
        .agg(pl.col('Out').sum())
        .select([
            pl.col('Batsman'),
            pl.col('Batter').alias('Player'),
            pl.col('TeamInns'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Out')
        ])
    )

    player_runs = (
        combineddata
        .group_by(groupby_cols_player)
        .agg([
            pl.col('Runs').sum().alias('Runs Scored'),
            pl.col('B').sum().alias('BF'),
            pl.col('Impact').sum()
        ])
        .select([
            pl.col('Batsman'),
            pl.col('Batter').alias('Player'),
            pl.col('TeamInns'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Runs Scored'),
            pl.col('BF'),
            pl.col('Impact')
        ])
    )

    # Over-level aggregations
    groupby_cols_over = ['TeamInns', place, 'over']

    over_outs = (
        dismissed_data
        .group_by(groupby_cols_over)
        .agg(pl.col('Out').sum().alias('Outs'))
        .select([
            pl.col('TeamInns'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Outs')
        ])
    )

    over_runs = (
        combineddata
        .group_by(groupby_cols_over)
        .agg([
            pl.col('Runs').sum(),
            pl.col('B').sum()
        ])
        .select([
            pl.col('TeamInns'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Runs'),
            pl.col('B')
        ])
    )

    # Combine player and over data
    combined_df = player_runs.join(
        player_outs,
        on=['Batsman', 'Player', 'TeamInns', place, 'Over'],
        how='left'
    )

    combined_df2 = over_runs.join(
        over_outs,
        on=['TeamInns', place, 'Over'],
        how='left'
    )

    combined_df3 = combined_df.join(
        combined_df2,
        on=['TeamInns', place, 'Over'],
        how='left'
    )

    # Fill nulls
    combined_df3 = combined_df3.with_columns([
        pl.col('Outs').fill_null(0),
        pl.col('Out').fill_null(0)
    ])

    # Calculate over statistics
    combined_df3 = combined_df3.with_columns([
        (pl.col('Runs') - pl.col('Runs Scored')).alias('Over_Runs'),
        (pl.col('B') - pl.col('BF')).alias('Over_B'),
        (pl.col('Outs') - pl.col('Out')).alias('Over_Outs')
    ])

    # Calculate rates with division by zero handling
    combined_df3 = combined_df3.with_columns([
        pl.when(pl.col('Over_B') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Over_Runs') / pl.col('Over_B'))
        .alias('BSR'),

        pl.when(pl.col('Over_B') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Over_Outs') / pl.col('Over_B'))
        .alias('OPB')
    ])

    # Calculate expected values
    combined_df3 = combined_df3.with_columns([
        (pl.col('BF') * pl.col('BSR')).alias('Expected Runs'),
        (pl.col('BF') * pl.col('OPB')).alias('Expected Outs')
    ])

    # Add phase using conditional logic
    combined_df3 = combined_df3.with_columns(
        pl.when(pl.col('Over') <= 6)
        .then(pl.lit('1 to 6'))
        .when(pl.col('Over') <= 11)
        .then(pl.lit('7 to 11'))
        .when(pl.col('Over') <= 16)
        .then(pl.lit('12 to 16'))
        .otherwise(pl.lit('17 to 20'))
        .alias('phase')
    )

    # Aggregate by player
    agg_cols = ['Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs', 'Impact']
    truevalues = (
        combined_df3
        .group_by(['Player', 'Batsman'])
        .agg([pl.col(col).sum() for col in agg_cols])
    )

    # Calculate metrics
    final_results = truemetrics(truevalues)

    # Add year
    players_years = (
        combineddata
        .select(['Batsman', 'Batter', 'year'])
        .unique()
        .select([
            pl.col('Batsman'),
            pl.col('Batter').alias('Player'),
            pl.col('year').alias('Year')
        ])
    )

    # Merge results
    final_results2 = inns2.join(
        final_results,
        on=['Batsman', 'Player'],
        how='left'
    )

    final_results3 = players_years.join(
        final_results2,
        on=['Batsman', 'Player'],
        how='left'
    )

    # Round numeric columns
    numeric_cols = final_results3.select(pl.col(pl.Float64)).columns
    final_results3 = final_results3.with_columns([
        pl.col(col).round(2) for col in numeric_cols
    ])

    return final_results3

def analyze_data_for_year6(year2, data2):
    """Analyze bowling data for a specific year - Polars version"""
    print(f"Processing year {year2} (bowling analyze_6)...")

    # Early filtering
    combineddata = data2.filter(
        (pl.col('TeamInns') < 3) & (pl.col('year') == year2)
    )

    # Calculate innings
    inns = (
        combineddata
        .group_by(['Bowlers', 'Bowler', 'MatchNum'])
        .agg(pl.col('Runs').sum())
        .with_columns(pl.lit(1).alias('I'))
    )

    inns2 = (
        inns
        .group_by(['Bowlers', 'Bowler'])
        .agg(pl.col('I').sum())
        .select([
            pl.col('Bowlers').alias('Player'),
            pl.col('Bowler').alias('BowlNum'),
            pl.col('I')
        ])
    )

    # Cumulative innings
    inns = inns.with_columns(
        pl.col('I').cum_sum().over('Bowlers').alias('CI')
    )

    # Dismissal data
    valid = ['X', 'XC', 'XT', 'XU', 'XSUTC', 'NX', 'LX', 'NXT', 'XZ', 'XP', 'PX', 'WX']
    dismissed_data = combineddata.filter(
        (pl.col('Notes').is_in(valid)) &
        (pl.col('BowlDis') == 'Y') &
        (pl.col('LongDis') != 'run out')
    )
    dismissed_data = dismissed_data.with_columns(pl.lit(1).alias('Out'))

    # Merge dismissal data
    merge_cols = ['MatchNum', 'TeamInns', place, 'Bowlers', 'Bowler', 'Notes', 'over']
    combineddata = combineddata.join(
        dismissed_data.select(merge_cols + ['Out']),
        on=merge_cols,
        how='left'
    ).with_columns(
        pl.col('Out').fill_null(0)
    )

    # Remove duplicates
    combineddata = combineddata.unique()

    # Player-level aggregations
    player_outs = (
        dismissed_data
        .group_by(['Bowlers', 'Bowler', place, 'over'])
        .agg(pl.col('Out').sum())
        .select([
            pl.col('Bowlers').alias('Player'),
            pl.col('Bowler').alias('BowlNum'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Out')
        ])
    )

    player_runs = (
        combineddata
        .group_by(['Bowlers', 'Bowler', place, 'over'])
        .agg([
            pl.col('RC').sum(),
            pl.col('B').sum().alias('BF'),
            pl.col('Impact').sum()
        ])
        .select([
            pl.col('Bowlers').alias('Player'),
            pl.col('Bowler').alias('BowlNum'),
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('RC'),
            pl.col('BF'),
            pl.col('Impact')
        ])
    )

    # Over-level aggregations
    over_outs = (
        dismissed_data
        .group_by([place, 'over'])
        .agg(pl.col('Out').sum().alias('Outs'))
        .select([
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Outs')
        ])
    )

    over_runs = (
        combineddata
        .group_by([place, 'over'])
        .agg([
            pl.col('RC').sum().alias('Runs'),
            pl.col('B').sum()
        ])
        .select([
            pl.col(place),
            pl.col('over').alias('Over'),
            pl.col('Runs'),
            pl.col('B')
        ])
    )

    # Combine data
    combined_df = player_runs.join(
        player_outs,
        on=['Player', 'BowlNum', place, 'Over'],
        how='left'
    )

    combined_df2 = over_runs.join(
        over_outs,
        on=[place, 'Over'],
        how='left'
    )

    combined_df3 = combined_df.join(
        combined_df2,
        on=[place, 'Over'],
        how='left'
    )

    # Fill nulls
    combined_df3 = combined_df3.with_columns([
        pl.col('Outs').fill_null(0),
        pl.col('Out').fill_null(0)
    ])

    # Calculate over statistics
    combined_df3 = combined_df3.with_columns([
        (pl.col('Runs') - pl.col('RC')).alias('Over_Runs'),
        (pl.col('B') - pl.col('BF')).alias('Over_B'),
        (pl.col('Outs') - pl.col('Out')).alias('Over_Outs')
    ])

    # Calculate rates with division by zero handling
    combined_df3 = combined_df3.with_columns([
        pl.when(pl.col('Over_B') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Over_Runs') / pl.col('Over_B'))
        .alias('BSR'),

        pl.when(pl.col('Over_B') == 0)
        .then(pl.lit(0.0))
        .otherwise(pl.col('Over_Outs') / pl.col('Over_B'))
        .alias('OPB')
    ])

    # Calculate expected values
    combined_df3 = combined_df3.with_columns([
        (pl.col('BF') * pl.col('BSR')).alias('Expected Runs'),
        (pl.col('BF') * pl.col('OPB')).alias('Expected Outs')
    ])

    # Add phase using conditional logic
    combined_df3 = combined_df3.with_columns(
        pl.when(pl.col('Over') <= 6)
        .then(pl.lit('1 to 6'))
        .when(pl.col('Over') <= 11)
        .then(pl.lit('7 to 11'))
        .when(pl.col('Over') <= 16)
        .then(pl.lit('12 to 16'))
        .otherwise(pl.lit('17 to 20'))
        .alias('phase')
    )

    # Aggregate by player
    agg_cols = ['RC', 'BF', 'Out', 'Expected Runs', 'Expected Outs', 'Impact']
    truevalues = (
        combined_df3
        .group_by(['Player', 'BowlNum'])
        .agg([pl.col(col).sum() for col in agg_cols])
    )

    # Calculate metrics
    final_results = truemetricsbowling(truevalues)

    # Add year and type
    players_years = (
        combineddata
        .select(['Bowlers', 'Bowler', 'BowlCat', 'year'])
        .unique()
        .select([
            pl.col('Bowlers').alias('Player'),
            pl.col('Bowler').alias('BowlNum'),
            pl.col('BowlCat').alias('Type'),
            pl.col('year').alias('Year')
        ])
    )

    # Merge results
    final_results2 = inns2.join(
        final_results,
        on=['Player', 'BowlNum'],
        how='left'
    )

    final_results3 = players_years.join(
        final_results2,
        on=['Player', 'BowlNum'],
        how='left'
    )

    # Round numeric columns
    numeric_cols = final_results3.select(pl.col(pl.Float64)).columns
    final_results3 = final_results3.with_columns([
        pl.col(col).round(2) for col in numeric_cols
    ])

    return final_results3

@st.cache_data
def load_data2(filename):
    """Load CSV data into Polars DataFrame"""
    return pl.read_csv(filename)

@st.cache_data
def load_data(filename):
    """Load parquet data into Polars DataFrame"""
    return pl.read_parquet(filename)

def apply_dl_vectorized(df, balls_col, wickets_param, alpha_p, beta_p):
    """Apply DL model vectorized - wickets_param can be column name (str) or constant (int)"""
    balls = df[balls_col].to_numpy()

    if isinstance(wickets_param, str):
        wickets = df[wickets_param].to_numpy()
    else:
        wickets = np.full(len(balls), wickets_param)

    alpha = cubic_poly(wickets, *alpha_p)
    beta = cubic_poly(wickets, *beta_p)

    return alpha * (1 - np.exp(-balls / beta))

def main():
    st.sidebar.title('True Values')

    format_choice = st.sidebar.selectbox('Select Format:', ['T20s', 'ODI', 'WT20s', 'WODI'])

    if format_choice == 'T20s':
        data = load_data('T20DataT20Leagues_optimized.parquet')
    elif format_choice == 'ODI':
        data = load_data('ODIData_optimized.parquet')
    elif format_choice == 'WT20s':
        data = load_data('WT20DataT20Leagues_optimized.parquet')
    else:
        data = load_data('WODIData_optimized.parquet')

    # Get unique competitions - convert to list for Streamlit
    selected_leagues = st.sidebar.multiselect(
        'Choose Competitions:',
        data['CompName'].unique(maintain_order=True).to_list()
    )

    global place
    if format_choice == 'ODI':
        place = 'Country'
    elif format_choice == 'T20s' and selected_leagues and 'Twenty20 International' not in selected_leagues:
        place = 'Venue_x'
    else:
        place = 'Country'

    if selected_leagues:
        data = data.filter(pl.col('CompName').is_in(selected_leagues))

    choice0 = st.sidebar.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])

    options = ['Overall Stats', 'Season By Season']
    choice = st.sidebar.selectbox('Select your option:', options)
    choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])

    # Get valid dates
    valid_dates = data.select(pl.col('Date').drop_nulls())

    import datetime
    if valid_dates.height > 0:
        min_dt = valid_dates['Date'].min().date()
        max_dt = valid_dates['Date'].max().date()
    else:
        min_dt = datetime.date(2000, 1, 1)
        max_dt = datetime.date(2030, 1, 1)

    start_date = st.sidebar.date_input("Start date", min_value=min_dt, max_value=max_dt, value=min_dt)
    end_date = st.sidebar.date_input("End date", min_value=min_dt, max_value=max_dt, value=max_dt)

    if start_date > end_date:
        st.sidebar.error('Error: End date must be greater than start date.')
        return

    # Convert dates to datetime for filtering
    start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
    end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

    # Vectorized filtering
    filtered_data2 = data.filter(
        (pl.col('Date') >= start_datetime) &
        (pl.col('Date') <= end_datetime)
    )

    if choice2 == 'Individual':
        if choice0 == 'Batting':
            players = filtered_data2['Batter'].unique().to_list()
        else:
            players = filtered_data2['Bowlers'].unique().to_list()
        player = st.sidebar.multiselect("Select Players:", players)

    choice3 = st.sidebar.multiselect('Pace or Spin:', ['Pace', 'Spin'])
    if choice3:
        filtered_data2 = filtered_data2.filter(pl.col('BowlCat').is_in(choice3))

    choice4 = st.sidebar.multiselect('Select Innings:', [1, 2])
    if choice4:
        filtered_data2 = filtered_data2.filter(pl.col('TeamInns').is_in(choice4))

    max_over = int(filtered_data2['over'].cast(pl.Int64).max())
    start_over, end_over = st.sidebar.slider(
        'Select Overs Range:',
        min_value=1,
        max_value=max_over,
        value=(1, max_over)
    )
    filtered_data2 = filtered_data2.filter(
        (pl.col('over') >= start_over) & (pl.col('over') <= end_over)
    )

    # Get unique years - convert to list
    unique_years = sorted(filtered_data2['year'].unique().to_list())

    # Use form to keep sliders persistent
    with st.sidebar.form("results_form"):
        show_results = st.form_submit_button('Show Results')

        if show_results:
            all_data = []

            for i, year in enumerate(unique_years):
                if choice0 == 'Batting':
                    results = analyze_data_for_year3(year, filtered_data2)
                else:
                    results = analyze_data_for_year6(year, filtered_data2)
                all_data.append(results)

            # Concatenate all results
            combined_data = pl.concat(all_data)

            if choice0 == 'Batting':
                # Aggregate
                agg_cols = ['I', 'Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs', 'Impact']
                truevalues = (
                    combined_data
                    .group_by(['Player', 'Batsman'])
                    .agg([pl.col(col).sum() for col in agg_cols])
                )
                final_results = truemetrics(truevalues)
                final_results = final_results.sort('Runs Scored', descending=True)
            else:
                agg_cols = ['I', 'RC', 'BF', 'Out', 'Expected Runs', 'Expected Outs', 'Impact']
                truevalues = (
                    combined_data
                    .group_by(['Player', 'BowlNum', 'Type'])
                    .agg([pl.col(col).sum() for col in agg_cols])
                )
                final_results = truemetricsbowling(truevalues)
                final_results = final_results.sort('Out', descending=True)

            if choice == 'Overall Stats':
                if choice2 == 'Individual':
                    # Filter by selected players
                    valid_players = set(final_results['Player'].unique().to_list())
                    temp = [p for p in player if p in valid_players]

                    invalid_players = [p for p in player if p not in valid_players]
                    for invalid_player in invalid_players:
                        st.sidebar.write(f'{invalid_player} not in this list')

                    if temp:
                        final_results = final_results.filter(pl.col('Player').is_in(temp))

                if choice0 == 'Batting':
                    final_results = final_results.sort('Runs Scored', descending=True)
                    drop_cols = ['Expected Runs', 'Expected Outs', 'Out Ratio', 'Expected Ave', 'Expected SR']
                    final_results = final_results.drop(drop_cols)

                    # Get max values for sliders
                    run = int(final_results['Runs Scored'].cast(pl.Int64).max())
                    balls = int(final_results['BF'].cast(pl.Int64).max())

                    start_runs, end_runs = st.slider(
                        'Select Minimum Runs Scored:',
                        min_value=0, max_value=run, value=(1, run)
                    )
                    start_balls, end_balls = st.slider(
                        'Select Minimum BF:',
                        min_value=1, max_value=balls, value=(1, balls)
                    )

                    # Apply filters
                    final_results = final_results.filter(
                        (pl.col('Runs Scored') >= start_runs) &
                        (pl.col('Runs Scored') <= end_runs) &
                        (pl.col('BF') >= start_balls) &
                        (pl.col('BF') <= end_balls)
                    )

                    final_results = final_results.with_columns(
                        (pl.col('Impact') / pl.col('I')).alias('Impact/Inns')
                    )
                else:
                    final_results = final_results.sort('Out', descending=True)
                    final_results = final_results.drop(['Expected Runs', 'Expected Outs', 'Expected Econ', 'Expected SR'])

                    # Get max values for sliders
                    outs = int(final_results['Out'].cast(pl.Int64).max())
                    balls = int(final_results['BF'].cast(pl.Int64).max())

                    start_runs, end_runs = st.slider(
                        'Select Wickets:',
                        min_value=0, max_value=outs, value=(1, outs)
                    )
                    start_balls, end_balls = st.slider(
                        'Select Minimum BF:',
                        min_value=1, max_value=balls, value=(1, balls)
                    )

                    # Apply filters
                    final_results = final_results.filter(
                        (pl.col('Out') >= start_runs) &
                        (pl.col('Out') <= end_runs) &
                        (pl.col('BF') >= start_balls) &
                        (pl.col('BF') <= end_balls)
                    )

                    final_results = final_results.with_columns(
                        (pl.col('Impact') / pl.col('I')).alias('Impact/Inns')
                    )

            elif choice == 'Season By Season':
                if choice2 == 'Individual':
                    valid_players = set(combined_data['Player'].unique().to_list())
                    temp = [p for p in player if p in valid_players]

                    invalid_players = [p for p in player if p not in valid_players]
                    for invalid_player in invalid_players:
                        st.sidebar.write(f'{invalid_player} not in this list')

                    if temp:
                        combined_data = combined_data.filter(pl.col('Player').is_in(temp))

                if choice0 == 'Batting':
                    combined_data = combined_data.sort('Year', descending=True)
                    drop_cols = ['Expected Runs', 'Expected Outs', 'Out Ratio', 'Expected Ave', 'Expected SR']
                    combined_data = combined_data.drop(drop_cols)

                    # Get max values for sliders
                    run = int(combined_data['Runs Scored'].cast(pl.Int64).max())
                    balls = int(combined_data['BF'].cast(pl.Int64).max())

                    start_runs, end_runs = st.slider(
                        'Select Minimum Runs Scored:',
                        min_value=0, max_value=run, value=(1, run)
                    )
                    start_balls, end_balls = st.slider(
                        'Select Minimum BF:',
                        min_value=1, max_value=balls, value=(1, balls)
                    )

                    # Apply filters
                    combined_data = combined_data.filter(
                        (pl.col('Runs Scored') >= start_runs) &
                        (pl.col('Runs Scored') <= end_runs) &
                        (pl.col('BF') >= start_balls) &
                        (pl.col('BF') <= end_balls)
                    )

                    combined_data = combined_data.with_columns(
                        (pl.col('Impact') / pl.col('I')).alias('Impact/Inns')
                    )
                else:
                    combined_data = combined_data.sort('Year', descending=True)
                    combined_data = combined_data.drop(['Expected Runs', 'Expected Outs', 'Expected Econ'])

                    # Get max values for sliders
                    outs = int(combined_data['Out'].cast(pl.Int64).max())
                    balls = int(combined_data['BF'].cast(pl.Int64).max())

                    start_runs, end_runs = st.slider(
                        'Select Wickets:',
                        min_value=0, max_value=outs, value=(1, outs)
                    )
                    start_balls, end_balls = st.slider(
                        'Select Minimum BF:',
                        min_value=1, max_value=balls, value=(1, balls)
                    )

                    # Apply filters
                    combined_data = combined_data.filter(
                        (pl.col('Out') >= start_runs) &
                        (pl.col('Out') <= end_runs) &
                        (pl.col('BF') >= start_balls) &
                        (pl.col('BF') <= end_balls)
                    )

                    combined_data = combined_data.with_columns(
                        (pl.col('Impact') / pl.col('I')).alias('Impact/Inns')
                    )

    # Display results outside the form
    if show_results:
        if choice == 'Overall Stats':
            # Round numeric columns before display
            numeric_cols = final_results.select(pl.col(pl.Float64)).columns
            final_results = final_results.with_columns([
                pl.col(col).round(2) for col in numeric_cols
            ])
            # Convert to pandas for Streamlit display (Streamlit works well with both)
            st.dataframe(final_results.to_pandas())
        elif choice == 'Season By Season':
            # Round numeric columns before display
            numeric_cols = combined_data.select(pl.col(pl.Float64)).columns
            combined_data = combined_data.with_columns([
                pl.col(col).round(2) for col in numeric_cols
            ])
            st.dataframe(combined_data.to_pandas())

if __name__ == '__main__':
    main()