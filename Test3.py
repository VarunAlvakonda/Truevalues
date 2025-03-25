from math import pi

import pandas as pd
import glob
import streamlit as st
import plotly.express as px
from matplotlib import pyplot as plt
import plotly.graph_objects as go  # Ensure this is the correct import


def truemetrics(truevalues):
    truevalues['Ave'] = truevalues['Runs Scored'] / truevalues['Out']
    truevalues['SR'] = (truevalues['Runs Scored'] / truevalues['BF'] * 100)

    truevalues['Expected Ave'] = truevalues['Expected Runs'] / truevalues['Expected Outs']
    truevalues['Expected SR'] = (truevalues['Expected Runs'] / truevalues['BF'] * 100)

    # Calculate 'True Ave' and 'True SR' for the final results
    truevalues['True Ave'] = (truevalues['Ave'] - truevalues['Expected Ave'])
    truevalues['True SR'] = (truevalues['SR'] - truevalues['Expected SR'])

    truevalues['Out Ratio'] = (truevalues['Expected Outs'] / truevalues['Out'])

    return truevalues


def truemetrics2(truevalues):
    ball_bins = [0, 6, 11, 16, 20]
    ball_labels = ['1 to 6', '7 to 11', '12 to 16', '17 to 20']
    truevalues['phase'] = pd.cut(truevalues['Over'], bins=ball_bins, labels=ball_labels, include_lowest=True,
                                 right=True)
    truevalues2 = truevalues.groupby(['Player', 'phase'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3 = truevalues.groupby(['phase'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3.columns = ['phase', 'Mean Runs', 'Mean BF', 'Mean Outs']
    truevalues4 = pd.merge(truevalues2, truevalues3, on=['phase'], how='left')
    truevalues4['SR'] = truevalues4['Runs Scored'] / truevalues4['BF'] * 100
    truevalues4['Mean SR'] = truevalues4['Mean Runs'] / truevalues4['Mean BF'] * 100
    return truevalues4


def truemetrics3(truevalues):
    truevalues2 = truevalues.groupby(['Player', 'phase'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3 = truevalues.groupby(['phase'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3.columns = ['phase', 'Mean Runs', 'Mean BF', 'Mean Outs']
    truevalues4 = pd.merge(truevalues2, truevalues3, on=['phase'], how='left')
    truevalues4['SR'] = truevalues4['Runs Scored'] / truevalues4['BF'] * 100
    truevalues4['Mean SR'] = truevalues4['Mean Runs'] / truevalues4['Mean BF'] * 100
    return truevalues4


def calculate_entry_point_all_years(data):
    # Identifying the first instance each batter faces a delivery in each match

    first_appearance = data.drop_duplicates(subset=['match_id', 'innings', 'striker'])
    first_appearance = first_appearance.copy()

    # Converting overs and deliveries into a total delivery count
    first_appearance.loc[:, 'total_deliveries'] = first_appearance['ball'].apply(
        lambda x: int(x) * 6 + int((x - int(x)) * 10))
    # Calculating the average entry point for each batter in total deliveries
    avg_entry_point_deliveries = first_appearance.groupby('striker')['total_deliveries'].median().reset_index()

    # Converting the average entry point from total deliveries to overs and balls and rounding to 1 decimal place
    avg_entry_point_deliveries['average_over'] = avg_entry_point_deliveries['total_deliveries'].apply(
        lambda x: round((x // 6) + (x % 6) / 10, 1))

    return avg_entry_point_deliveries[['striker', 'average_over']], first_appearance


def calculate_first_appearance(data):
    # Identifying the first instance each batter faces a delivery in each match
    first_appearance = data.drop_duplicates(subset=['match_id', 'innings', 'striker'])
    # Converting overs and deliveries into a total delivery count
    first_appearance.loc[:, 'total_deliveries'] = first_appearance['ball'].apply(
        lambda x: int(x) * 6 + int((x - int(x)) * 10))

    # Calculating the average entry point for each batter in total deliveries
    avg_entry_point_deliveries = first_appearance.groupby(['striker', 'year', 'batting_team'])[
        'total_deliveries'].median().reset_index()

    # Converting the average entry point from total deliveries to overs and balls
    avg_entry_point_deliveries['average_over'] = (
        avg_entry_point_deliveries['total_deliveries'].apply(lambda x: (x // 6) + (x % 6) / 10)).round(1)

    return avg_entry_point_deliveries[['striker', 'average_over']]


def analyze_data_for_year2(data):
    # Filter the data for the specified year
    year_data = data.copy()

    # Calculate the first appearance of each batter in each match for the year
    first_appearance_data = calculate_first_appearance(year_data)

    # Calculate the average entry point for each batter

    # Assuming other analysis results are in a DataFrame named 'analysis_results'
    if 'analysis_results' in locals() or 'analysis_results' in globals():
        # Merge the average entry point data with other analysis results
        analysis_results = pd.merge(year_data, first_appearance_data, on=['striker'],
                                    how='left')
    else:
        # Use average entry point data as the primary analysis result
        analysis_results = first_appearance_data

    return analysis_results


def analyze_data_for_year3(year2, data2):
    combineddata2 = data2[data2['innings'] < 3].copy()
    combineddata = combineddata2[combineddata2['year'] == year2].copy()
    inns = combineddata.groupby(['striker', 'match_id'])[['runs_off_bat']].sum().reset_index()
    inns['I'] = 1
    inns2 = inns.groupby(['striker'])[['I']].sum().reset_index()
    inns2.columns = ['Player', 'I']
    inns3 = inns.copy()
    inns['CI'] = inns.groupby(['striker'], as_index=False)[['I']].cumsum()
    analysis_results = analyze_data_for_year2(combineddata)
    analysis_results.columns = ['Player', 'Median Entry Point']

    # Filter out rows where a player was dismissed
    dismissed_data = combineddata[combineddata['player_dismissed'].notnull()]
    dismissed_data = dismissed_data[dismissed_data['wicket_type'] != 'retired hurt']
    dismissed_data['Out'] = 1

    combineddata2 = pd.merge(combineddata, dismissed_data[['match_id', 'innings', 'player_dismissed', 'over', 'Out']],
                             on=['match_id', 'innings', 'player_dismissed', 'over'], how='left')
    combineddata2['Out'].fillna(0, inplace=True)
    combineddata = combineddata2.copy()

    player_outs = dismissed_data.groupby(['player_dismissed', 'venue', 'over'])[['Out']].sum().reset_index()
    player_outs.columns = ['Player', 'Venue', 'Over', 'Out']

    over_outs = dismissed_data.groupby(['venue', 'over'])[['Out']].sum().reset_index()
    over_outs.columns = ['Venue', 'Over', 'Outs']

    temp = combineddata.copy()
    temp['Runs'] = temp.groupby(['striker', 'match_id', 'innings'], as_index=False)['runs_off_bat'].cumsum()
    temp['Balls'] = temp.groupby(['striker', 'match_id', 'innings'], as_index=False)['B'].cumsum()
    temp['Wickets'] = temp.groupby(['striker', 'match_id', 'innings'], as_index=False)['Out'].cumsum()

    temp.to_csv('asdkasda.csv')

    temp2 = temp[['match_id', 'innings', 'striker', 'over', 'Runs', 'Balls']]
    temp2 = temp2.drop_duplicates()
    temp2.round(2).to_csv(f'ballbyball{year2}.csv')
    temp2['count'] = 1
    temp2.loc[temp2['Balls'] == 0, 'count'] = 0
    temp3 = temp2.groupby(['striker', 'Balls'])[['Runs', 'count']].sum().reset_index()
    temp3['Ave Runs'] = temp3['Runs'] / temp3['count']
    temp3['SR'] = temp3['Ave Runs'] / temp3['Balls'] * 100
    temp3.round(2).to_csv(f'averagesr{year2}.csv')

    # Creating a pivot table with Balls as the index and players as columns
    pivot_table = temp3.pivot_table(values='Ave Runs', index='Balls', columns='striker')

    # Saving the pivot table to a CSV file
    pivot_table.round(2).to_csv(f'player_runs_by_balls{year2}.csv')

    # Create a pivot table with Balls as the index and strikers as columns with their average runs
    pivot_table = temp3.pivot_table(values='SR', index='Balls', columns='striker')

    # Saving the strike rates to a CSV file
    pivot_table.round(2).to_csv(f'strike_rate_by_balls{year2}.csv')

    # Group by player and aggregate the runs scored
    player_runs = combineddata.groupby(['striker', 'venue', 'over'])[['runs_off_bat', 'B']].sum().reset_index()
    # Rename the columns for clarity
    player_runs.columns = ['Player', 'Venue', 'Over', 'Runs Scored', 'BF']

    # Display the merged DataFrame
    over_runs = combineddata.groupby(['venue', 'over'])[['runs_off_bat', 'B']].sum().reset_index()
    over_runs.columns = ['Venue', 'Over', 'Runs', 'B']
    # Merge the two DataFrames on the 'Player' column

    combined_df = pd.merge(player_runs, player_outs, on=['Player', 'Venue', 'Over'], how='left')
    # Merge the two DataFrames on the 'Player' column
    combined_df2 = pd.merge(over_runs, over_outs, on=['Venue', 'Over'], how='left')
    # Calculate BSR and OPB for each ball at each venue

    combined_df3 = pd.merge(combined_df, combined_df2, on=['Venue', 'Over'], how='left')
    combined_df3['Outs'].fillna(0, inplace=True)
    combined_df3['Out'].fillna(0, inplace=True)

    combined_df3['Over_Runs'] = combined_df3['Runs'] - combined_df3['Runs Scored']
    combined_df3['Over_B'] = combined_df3['B'] - combined_df3['BF']
    combined_df3['Over_Outs'] = combined_df3['Outs'] - combined_df3['Out']

    combined_df3['BSR'] = combined_df3['Over_Runs'] / combined_df3['Over_B']
    combined_df3['OPB'] = combined_df3['Over_Outs'] / combined_df3['Over_B']

    combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
    combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']

    truevalues = combined_df3.groupby(['Player'])[
        ['Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs']].sum()

    final_results = truemetrics(truevalues)

    players_years = combineddata[['striker', 'batting_team', 'year']].drop_duplicates()
    players_years.columns = ['Player', 'Team', 'Year']
    final_results2 = pd.merge(inns2, final_results, on='Player', how='left')
    final_results3 = pd.merge(players_years, final_results2, on='Player', how='left')
    final_results4 = pd.merge(final_results3, analysis_results, on='Player', how='left')
    print(combined_df3.columns)
    truevalues = truemetrics2(combined_df3)
    return final_results4


def analyze_data_for_year4(year2, data2):
    combineddata2 = data2[data2['innings'] < 3].copy()
    combineddata = combineddata2[combineddata2['year'] == year2].copy()
    inns = combineddata.groupby(['striker', 'match_id', 'phase'])[['runs_off_bat']].sum().reset_index()
    inns['I'] = 1
    inns2 = inns.groupby(['striker', 'phase'])[['I']].sum().reset_index()
    inns2.columns = ['Player', 'phase', 'I']
    inns3 = inns.copy()
    inns['CI'] = inns.groupby(['striker'], as_index=False)[['I']].cumsum()

    # Filter out rows where a player was dismissed
    dismissed_data = combineddata[combineddata['player_dismissed'].notnull()]
    dismissed_data = dismissed_data[dismissed_data['wicket_type'] != 'retired hurt']
    dismissed_data['Out'] = 1

    combineddata2 = pd.merge(combineddata, dismissed_data[['match_id', 'innings', 'player_dismissed', 'over', 'Out']],
                             on=['match_id', 'innings', 'player_dismissed', 'over'], how='left')
    combineddata2['Out'].fillna(0, inplace=True)
    combineddata = combineddata2.copy()

    player_outs = dismissed_data.groupby(['player_dismissed', 'venue', 'over', 'phase'])[['Out']].sum().reset_index()
    player_outs.columns = ['Player', 'Venue', 'Over', 'phase', 'Out']

    over_outs = dismissed_data.groupby(['venue', 'over', 'phase'])[['Out']].sum().reset_index()
    over_outs.columns = ['Venue', 'Over', 'phase', 'Outs']

    # Group by player and aggregate the runs scored
    player_runs = combineddata.groupby(['striker', 'venue', 'over', 'phase'])[['runs_off_bat', 'B']].sum().reset_index()
    # Rename the columns for clarity
    player_runs.columns = ['Player', 'Venue', 'Over', 'phase', 'Runs Scored', 'BF']

    # Display the merged DataFrame
    over_runs = combineddata.groupby(['venue', 'over', 'phase'])[['runs_off_bat', 'B']].sum().reset_index()
    over_runs.columns = ['Venue', 'Over', 'phase', 'Runs', 'B']
    # Merge the two DataFrames on the 'Player' column

    combined_df = pd.merge(player_runs, player_outs, on=['Player', 'Venue', 'Over', 'phase'], how='left')
    # Merge the two DataFrames on the 'Player' column
    combined_df2 = pd.merge(over_runs, over_outs, on=['Venue', 'Over', 'phase'], how='left')
    # Calculate BSR and OPB for each ball at each venue
    combined_df2['BSR'] = combined_df2['Runs'] / combined_df2['B']
    combined_df2['OPB'] = combined_df2['Outs'] / combined_df2['B']

    combined_df3 = pd.merge(combined_df, combined_df2, on=['Venue', 'Over', 'phase'], how='left')
    combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
    combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']

    truevalues = combined_df3.groupby(['Player', 'phase'])[
        ['Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs']].sum()

    final_results = truemetrics(truevalues)

    players_years = combineddata[['striker', 'batting_team', 'year', 'phase']].drop_duplicates()
    players_years.columns = ['Player', 'Team', 'Year', 'phase']
    final_results2 = pd.merge(inns2, final_results, on=['Player', 'phase'], how='left')
    final_results3 = pd.merge(players_years, final_results2, on=['Player', 'phase'], how='left')
    return final_results3.round(2)


def battingpositions(combineddata):
    # Initialize a column for the batting position in the original DataFrame
    grouped_data = combineddata.groupby(['match_id', 'batting_team'])
    combineddata['batting_position'] = 0

    # Iterate over each group (unique match_id and batting_team)
    for (match_id, team), group in grouped_data:
        # Initialize a dictionary to track positions
        position_counter = {}
        # Get the first row of the group to identify initial striker and non-striker
        first_row = group.iloc[0]
        initial_striker = first_row['striker']
        initial_non_striker = first_row['non_striker']

        # Assign position 1 to the initial striker and 2 to the initial non-striker
        position_counter[initial_striker] = 1
        position_counter[initial_non_striker] = 2

        # Iterate through each row of the group to assign positions
        for index, row in group.iterrows():
            striker = row['striker']
            if striker not in position_counter:
                # Assign the next position number to new strikers
                position_counter[striker] = len(position_counter) + 1
            # Update the DataFrame with the batting position
            combineddata.at[index, 'batting_position'] = position_counter[striker]
    return combineddata


# Load the data
@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)

    data['B'] = 1

    # Set 'B' to 0 for deliveries that are wides
    # Assuming 'wides' column exists and is non-zero for wide balls
    data.loc[data['wides'] > 0, 'B'] = 0

    data['wides'].fillna(0, inplace=True)
    data['noballs'].fillna(0, inplace=True)

    data['RC'] = data['wides'] + data['noballs'] + data['runs_off_bat']

    # Extract the year from the 'start_date' column

    data['year'] = pd.to_datetime(data['start_date'], format='mixed').dt.year
    years = data['year'].unique()

    # Remove any potential duplicate rows
    data = data.drop_duplicates()

    data['ball2'] = pd.to_numeric(data['ball'], errors='coerce')
    data['over'] = data['ball2'] // 1 + 1

    data['Date'] = pd.to_datetime(data['start_date'], format='%Y-%m-%d')

    return data


# The main app function

def main():
    st.title('Batting True Values')

    # Load and concatenate data for all selected leagues
    league_files = {
        'IPL': 'ipl.csv',
    }

    selected_leagues = st.selectbox('Choose leagues:', list(league_files.keys()))

    data = load_data(league_files[selected_leagues])
    years = data['year'].unique()
    dates = data['Date'].unique()
    data2 = data.groupby('striker')[['runs_off_bat', 'B']].sum().reset_index()
    run = max((data2['runs_off_bat']).astype(int))
    ball = max((data2['B']).astype(int))

    # Selectors for user input
    options = ['Overall Stats', 'Season By Season']

    # Create a select box
    choice = st.selectbox('Select your option:', options)
    choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])

    # selected_options = st.multiselect('Choose options:', pos)
    # start_year, end_year = st.slider('Select Years Range:', min_value=min(years), max_value=max(years), value=(min(years), max(years)))

    # User inputs for Date range
    start_date = st.date_input('Start Date', data['Date'].min())
    end_date = st.date_input('End Date', data['Date'].max())

    # Filtering data based on the user's Date selection
    if start_date > end_date:
        st.error('Error: End Date must be greater than start Date.')

    start_over, end_over = st.slider('Select Overs Range:', min_value=1, max_value=20, value=(1, 20))
    start_runs, end_runs = st.slider('Select Minimum Runs:', min_value=1, max_value=run, value=(1, run))
    start_runs1, end_runs1 = st.slider('Select Minimum BF:', min_value=1, max_value=ball, value=(1, ball))
    filtered_data = data[(data['over'] >= start_over) & (data['over'] <= end_over)]
    print(filtered_data.columns)
    # filtered_data2 = filtered_data[(filtered_data['year'] >= start_year) & (filtered_data['year'] <= end_year)]
    filtered_data2 = filtered_data[
        (filtered_data['Date'] >= pd.to_datetime(start_date)) & (filtered_data['Date'] <= pd.to_datetime(end_date))]

    if selected_leagues == 'T20I':
        batting = st.multiselect("Select Teams:", filtered_data2['batting_team'].unique())
        if batting:
            filtered_data2 = filtered_data2[filtered_data2['batting_team'].isin(batting)].copy()
            filtered_data2 = filtered_data2[filtered_data2['bowling_team'].isin(batting)].copy()
    if choice2 == 'Individual':
        players = data['striker'].unique()
        player = st.multiselect("Select Players:", players)
        # name = st.selectbox('Choose the Player From the list', data['striker'].unique())
    inns = [1, 2]
    inn = st.multiselect("Select innings:", inns)
    if inn:
        filtered_data2 = filtered_data2[filtered_data2['innings'].isin(inn)].copy()
    x = filtered_data2
    # A button to trigger the analysis
    if st.button('Analyse'):
        # Call a hypothetical function to analyze data
        all_data = []

        # Analyze data and save results for each year
        for year in filtered_data2['year'].unique():
            results = analyze_data_for_year3(year, filtered_data2)
            all_data.append(results)

        combined_data = pd.concat(all_data, ignore_index=True)
        most_frequent_team = combined_data.groupby('Player')['Team'].agg(lambda x: x.mode().iat[0]).reset_index()

        truevalues = combined_data.groupby(['Player'])[
            ['I', 'Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs']].sum()
        final_results = truemetrics(truevalues)

        final_results2 = pd.merge(final_results, most_frequent_team, on='Player', how='left')

        final_results3, f = calculate_entry_point_all_years(x)
        final_results3.columns = ['Player', 'Median Entry Point']

        final_results4 = pd.merge(final_results3, final_results2, on='Player', how='left').reset_index()
        final_results4 = final_results4.sort_values(by=['Runs Scored'], ascending=False)
        final_results4 = final_results4[
            ['Player', 'Median Entry Point', 'I', 'Runs Scored', 'BF', 'Out', 'Ave', 'SR', 'Expected Ave',
             'Expected SR', 'True Ave', 'True SR', 'Team', ]]
        final_results4 = final_results4[
            (final_results4['Runs Scored'] >= start_runs) & (final_results4['Runs Scored'] <= end_runs)]
        final_results4 = final_results4[(final_results4['BF'] >= start_runs1) & (final_results4['BF'] <= end_runs1)]
        if choice == 'Overall Stats':
            # Display the results
            if choice2 == 'Individual':
                temp = []
                for i in player:
                    if i in final_results4['Player'].unique():
                        temp.append(i)
                    else:
                        st.subheader(f'{i} not in this list')
                final_results4 = final_results4[final_results4['Player'].isin(temp)]
                st.dataframe(final_results4.round(2))
            else:
                final_results4 = final_results4.sort_values(by=['Runs Scored'], ascending=False)
                st.dataframe(final_results4.round(2))

        elif choice == 'Season By Season':
            combined_data = combined_data[
                (combined_data['Runs Scored'] >= start_runs) & (combined_data['Runs Scored'] <= end_runs)]
            combined_data = combined_data[(combined_data['BF'] >= start_runs1) & (combined_data['BF'] <= end_runs1)]
            if choice2 == 'Individual':
                temp = []
                for i in player:
                    if i in combined_data['Player'].unique():
                        temp.append(i)
                    else:
                        st.subheader(f'{i} not in this list')
                combined_data = combined_data[combined_data['Player'].isin(temp)]
                combined_data = combined_data.sort_values(by=['Runs Scored'], ascending=False)
                st.dataframe(combined_data.round(2))
            else:
                combined_data = combined_data.sort_values(by=['Runs Scored'], ascending=False)
                st.dataframe(combined_data.round(2))
                combined_data['Player2'] = combined_data['Player'] + ' , ' + combined_data['Year'].astype(str)


# # The main app function
# def main():
#     st.set_page_config(layout="wide")
#
#     data = load_data('all_matches.csv')
#     years = data['year'].unique()
#     dates = data['Date'].unique()
#
#     # Select player on the top-left
#     players = data['striker'].unique()
#     player = st.sidebar.selectbox("Select Player:", players)
#
#     # After player is chosen, show date selection
#     st.sidebar.subheader("Date Selection")
#     start_date = st.sidebar.date_input('Start Date', data['Date'].min())
#     end_date = st.sidebar.date_input('End Date', data['Date'].max())
#
#     # Filter data based on player selection and date range
#     player_data = data[data['striker'] == player]
#     filtered_data = data[(data['Date'] >= pd.to_datetime(start_date)) & (data['Date'] <= pd.to_datetime(end_date))]
#     start_over, end_over = st.sidebar.slider('Select Overs Range:', min_value=1, max_value=20, value=(1, 20))
#     filtered_data = filtered_data[(filtered_data['over'] >= start_over) & (filtered_data['over'] <= end_over)]
#     # Initialize a list to store year-by-year data
#     all_yearly_data = []
#
#     # Year-by-Year Breakdown
#     for year in filtered_data['year'].unique():
#         year_data = filtered_data[filtered_data['year'] == year]
#
#         # Apply `truemetrics` function directly on the yearly data
#         year_results = analyze_data_for_year3(year,filtered_data)
#         player_data = year_results[year_results['Player'] == player]
#
#         # Append the year data for calculating overall stats later
#         all_yearly_data.append(player_data)
#
#
#
#     # Once year-by-year stats are handled, calculate overall stats by summing up the yearly results
#     st.subheader(f"Year Stats for {player}")
#
#     # Combine all yearly data into one DataFrame
#     combined_data = pd.concat(all_yearly_data, ignore_index=True)
#
#     # Apply `truemetrics` on the combined yearly data to calculate overall stats
#     overall_results = truemetrics(combined_data)
#     overall_results = overall_results.applymap(lambda x: '{:.2f}'.format(x) if isinstance(x, (float, int)) else x)
#
#     filtered_data = filtered_data[filtered_data['striker'] == player]
#     dismissed_data = filtered_data[filtered_data['player_dismissed'].notnull()]
#     dismissed_data = dismissed_data[dismissed_data['wicket_type'] != 'retired hurt']
#     dismissed_data['Out'] = 1
#     dismissed_data = dismissed_data.groupby(['striker','wicket_type'])[['Out']].sum().reset_index()
#
#     # Step 3: Format all numeric columns to 2 decimal places
#     overall_results = overall_results.applymap(lambda x: '{:.2f}'.format(x) if isinstance(x, (float, int)) else x)
#     overall_results['Year'] = pd.to_numeric(overall_results['Year'], errors='coerce').fillna(0).astype(int)
#     overall_results['Year'] = overall_results['Year'].astype(str)
#
#     # Step 4: Select required columns and ensure `Year` is properly formatted as an integer
#     overall_results = overall_results[['Year', 'Player', 'Runs Scored', 'BF', 'Out', 'Ave', 'SR', 'True Ave', 'True SR']]
#
#     overall_results = overall_results.reset_index(drop=True)
#
#     # Display the overall results without the index
#     st.dataframe(overall_results)
#
#
#
#     player_data = dismissed_data
#
#     # Convert 'Out' to percentage of the total dismissals for the player
#     total_outs = player_data['Out'].sum()
#     player_data['Out_Percentage'] = (player_data['Out'] / total_outs * 100).map('{:.2f}'.format)
#
#     # Create a bar chart using Plotly
#     fig = px.bar(player_data, x='wicket_type', y='Out', text='Out_Percentage',
#                  title=f'Dismissal Types for {player} (in %)',
#                  labels={'wicket_type': 'Wicket Type', 'Out': 'Number of Dismissals'})
#
#     # Update hover text to show percentages with 2 decimal places
#     fig.update_traces(hovertemplate='%{x}: %{text}%<extra></extra>', textposition='auto')
#
#     # Display the bar chart in Streamlit
#     st.plotly_chart(fig)

if __name__ == '__main__':
    main()