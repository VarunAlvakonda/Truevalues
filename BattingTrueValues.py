import pandas as pd
import streamlit as st

place = 'Venue_x'
type = 'PhaseofSeason'
# place = 'Country'
type = 'BowlCat'
type = 'entryphase'

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

    return truevalues


def truemetrics2(truevalues):
    truevalues2 = truevalues.groupby(['Player', 'Over'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3 = truevalues.groupby(['Over'])[['Runs Scored', 'BF', 'Out']].sum().reset_index()
    truevalues3.columns= ['Over','Mean Runs','Mean BF','Mean Outs']
    truevalues4 = pd.merge(truevalues2, truevalues3,on=['Over'], how='left')
    truevalues4['SR'] =  truevalues4['Runs Scored']/ truevalues4['BF'] * 100
    truevalues4['Mean SR'] =  truevalues4['Mean Runs']/ truevalues4['Mean BF'] * 100
    return truevalues4

def calculate_entry_point_all_years(data):
    # Identifying the first instance each batter faces a delivery in each match

    first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter'])
    first_appearance = first_appearance.copy()

    # Converting overs and deliveries into a total delivery count
    first_appearance.loc[:, 'total_deliveries'] = first_appearance['Over'].apply(
        lambda x: int(x) * 6 + int((x - int(x)) * 10))
    # Calculating the average entry point for each batter in total deliveries
    avg_entry_point_deliveries = first_appearance.groupby('Batter')['total_deliveries'].median().reset_index()

    # Converting the average entry point from total deliveries to overs and Overs and rounding to 1 decimal place
    avg_entry_point_deliveries['average_over'] = avg_entry_point_deliveries['total_deliveries'].apply(
        lambda x: round((x // 6) + (x % 6) / 10, 1))

    return avg_entry_point_deliveries[['Batter', 'average_over']], first_appearance


def calculate_first_appearance(data):
    # Identifying the first instance each batter faces a delivery in each match
    first_appearance = data.drop_duplicates(subset=['MatchNum', 'TeamInns', 'Batter'])
    # Converting overs and deliveries into a total delivery count
    first_appearance.loc[:, 'total_deliveries'] = first_appearance['Over'].apply(
        lambda x: int(x) * 6 + int((x - int(x)) * 10))

    # Calculating the average entry point for each batter in total deliveries
    avg_entry_point_deliveries = first_appearance.groupby(['Batter', 'year'])[
        'total_deliveries'].median().reset_index()

    # Converting the average entry point from total deliveries to overs and Overs
    avg_entry_point_deliveries['average_over'] = (
        avg_entry_point_deliveries['total_deliveries'].apply(lambda x: (x // 6) + (x % 6) / 10)).round(1)

    return avg_entry_point_deliveries[['Batter', 'average_over']]

def analyze_data_for_year2(data):
    # Filter the data for the specified year
    year_data = data.copy()

    # Calculate the first appearance of each batter in each match for the year
    first_appearance_data = calculate_first_appearance(year_data)

    # Calculate the average entry point for each batter

    # Assuming other analysis results are in a DataFrame named 'analysis_results'
    if 'analysis_results' in locals() or 'analysis_results' in globals():
        # Merge the average entry point data with other analysis results
        analysis_results = pd.merge(year_data, first_appearance_data, on=['Batter'],
                                    how='left')
    else:
        # Use average entry point data as the primary analysis result
        analysis_results = first_appearance_data

    return analysis_results


@st.cache_data
def analyze_data_for_year3(year2, data2):
    combineddata2 = data2[data2['TeamInns'] < 3].copy()
    combineddata = combineddata2[combineddata2['year'] == year2].copy()
    inns = combineddata.groupby(['Batter', 'MatchNum'])[['Runs']].sum().reset_index()
    inns['I'] = 1
    inns2 = inns.groupby(['Batter'])[['I']].sum().reset_index()
    inns2.columns = ['Player', 'I']
    inns3 = inns.copy()
    inns['CI'] = inns.groupby(['Batter'],as_index=False)[['I']].cumsum()
    analysis_results = analyze_data_for_year2(combineddata)
    analysis_results.columns = ['Player', 'Median Entry Point']

    valid = ['X','WX']
    # Filter out rows where a player was dismissed
    dismissed_data= combineddata[combineddata['Notes'].isin(valid)]
    dismissed_data['Out'] = 1

    combineddata2 = pd.merge(combineddata, dismissed_data[['MatchNum','TeamInns', 'Batter', 'Notes','over', 'Out']],
                             on=['MatchNum', 'TeamInns', 'Batter', 'Notes','over'], how='left')
    combineddata2['Out'].fillna(0, inplace=True)
    combineddata = combineddata2.copy()

    player_outs = dismissed_data.groupby(['Batter', 'TeamInns', place, 'over'])[['Out']].sum().reset_index()
    player_outs.columns = ['Player', 'TeamInns', place, 'Over', 'Out']

    over_outs = dismissed_data.groupby([ 'TeamInns', place,'over'])[['Out',]].sum().reset_index()
    over_outs.columns = ['TeamInns', place, 'Over', 'Outs',]

    # Group by player and aggregate the runs scored
    player_runs = combineddata.groupby(['Batter', 'TeamInns', place, 'over'])[['Runs', 'B',]].sum().reset_index()
    # Rename the columns for clarity
    player_runs.columns = ['Player', 'TeamInns', place, 'Over', 'Runs Scored', 'BF']

    # Display the merged DataFrame
    over_runs = combineddata.groupby(['TeamInns', place, 'over'])[['Runs', 'B']].sum().reset_index()
    over_runs.columns = ['TeamInns', place, 'Over', 'Runs', 'B']
    # Merge the two DataFrames on the 'Player' column

    combined_df = pd.merge(player_runs, player_outs, on=['Player', 'TeamInns', place, 'Over'], how='left')
    # Merge the two DataFrames on the 'Player' column
    combined_df2 = pd.merge(over_runs, over_outs, on=['TeamInns', place, 'Over'], how='left')

    combined_df3 = pd.merge(combined_df, combined_df2, on=['TeamInns', place, 'Over'], how='left')
    print(combined_df3.columns)
    combined_df3['Outs'].fillna(0, inplace=True)
    combined_df3['Out'].fillna(0, inplace=True)

    combined_df3['Over_Runs'] =combined_df3['Runs'] - combined_df3['Runs Scored']
    combined_df3['Over_B'] =combined_df3['B'] - combined_df3['BF']
    combined_df3['Over_Outs'] =combined_df3['Outs'] - combined_df3['Out']

    combined_df3['BSR'] = combined_df3['Over_Runs'] / combined_df3['Over_B']
    combined_df3['OPB'] = combined_df3['Over_Outs'] / combined_df3['Over_B']

    combined_df3['Expected Runs'] = combined_df3['BF'] * combined_df3['BSR']
    combined_df3['Expected Outs'] = combined_df3['BF'] * combined_df3['OPB']

    ball_bins2 = [0, 6,11, 16, 20]
    ball_labels2 = ['1 to 6', '7 to 11','12 to 16', '17 to 20']
    ball_labels = ['1 to 10', '11 to 25', '26 to 40','41 to 50']
    ball_bins = [0, 10,25, 40,50]
    combined_df3['phase'] = pd.cut(combined_df3['Over'], bins=ball_bins2, labels=ball_labels2, include_lowest=True,
                                   right=True)

    truevalues = combined_df3.groupby(['Player',], observed=True)[
        ['Runs Scored', 'BF', 'Out','Expected Runs', 'Expected Outs']].sum().reset_index()

    final_results = truemetrics(truevalues)

    players_years = combineddata[['Batter','BattingTeam','year']].drop_duplicates()
    players_years.columns = ['Player','Team','Year']
    final_results2 = pd.merge(inns2, final_results, on='Player', how='left')
    final_results3 = pd.merge(players_years, final_results2, on='Player', how='left')
    final_results4 = pd.merge(final_results3, analysis_results, on='Player', how='left')

    return final_results4.round(2)



# Load the data
@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    # Set 'B' to 0 for deliveries that are wides
    data['B'] = 1

    # Set 'B' to 0 for deliveries that are wides
    # Assuming 'wides' column exists and is non-zero for wide balls
    data.loc[data['Notes'] == 'W', 'B'] = 0

    data['RC'] = data['Runs'] + data['Extras']
    data['TotalRuns'] = data['Runs'] + data['Extras']

    # Extract the year from the 'start_date' column

    data['year'] = pd.to_datetime(data['StartDate'], format='mixed').dt.year
    data['Date'] = pd.to_datetime(data['StartDate'], format='mixed')

    years = data['year'].unique()

    # Remove any potential duplicate rows
    data = data.drop_duplicates()

    data['ball2'] = pd.to_numeric(data['Over'], errors='coerce')
    data['over'] = data['ball2'] // 1 + 1

    rpace = ['RF', 'RFM', 'RM', 'RMF']
    lpace = ['LF', 'LF/LM', 'LFM', 'LM', 'LMF']
    roff = ['OB', 'RM/OB', 'S']
    loff = ['SLA']
    rleg = ['LB']
    lleg = ['SLW']

    data['Types'] = 'L'
    data.loc[data['BowlType'].isin(rpace), 'Types'] = 'Right Arm Pace'
    data.loc[data['BowlType'].isin(lpace), 'Types'] = 'Left Arm Pace'
    data.loc[data['BowlType'].isin(roff), 'Types'] = 'Right Arm Finger Spin'
    data.loc[data['BowlType'].isin(loff), 'Types'] = 'Left Arm Finger Spin'
    data.loc[data['BowlType'].isin(rleg), 'Types'] = 'Right Arm Wrist Spin'
    data.loc[data['BowlType'].isin(lleg), 'Types'] = 'Left Arm Wrist Spin'
    data['BowlCat'] = data['BowlCat'].replace({'F': 'Pace', 'S': 'Spin'})

    # combined_data['TeamBalls'] = combined_data['B']
    runsbymatch = data.groupby(['MatchNum','TeamInns'])[['TotalRuns']].sum().reset_index()
    runsbymatch = runsbymatch[runsbymatch['TeamInns']==1]
    runsbymatch['TeamInns'] = 1
    runsbymatch = runsbymatch.rename(columns={'TotalRuns':'TargetRuns'})
    runsbymatch = runsbymatch.drop(columns=['TeamInns'])
    combined_data2 = data[data['TeamInns']==2]
    combined_data2 = pd.merge(combined_data2,runsbymatch, how='left',on = ['MatchNum',])
    data = pd.concat([data[data['TeamInns']==1], combined_data2], ignore_index=True)

    data['TeamRuns'] = data.groupby(['MatchNum', 'TeamInns'], as_index=False)['TotalRuns'].cumsum()
    data['Wkts'] = 0
    data.loc[data['HowOut'].notnull(),'Wkts'] = 1
    data['TeamWicket'] = data.groupby(['MatchNum', 'TeamInns'], as_index=False)['Wkts'].cumsum()
    data['TeamBalls'] = data.groupby(['MatchNum', 'TeamInns'], as_index=False)['B'].cumsum()
    data['MatchBatRuns'] = data.groupby(['Batter','MatchNum', 'TeamInns'], as_index=False)['Runs'].cumsum()
    data['BatterBalls'] = data.groupby(['Batter','MatchNum', 'TeamInns'], as_index=False)['B'].cumsum()
    data['MatchBowlRC'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'], as_index=False)['RC'].cumsum()
    data['MatchBowlBalls'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'], as_index=False)['B'].cumsum()
    data['MatchBowlWkt'] = data.groupby(['Bowlers','MatchNum', 'TeamInns'], as_index=False)['Wkts'].cumsum()
    data['BallsRemaining'] = (120 - data['TeamBalls'])
    return data


# The main app function

def main():
    st.title('True Values')

    allt20s = load_data('T20Leagues.csv')

    selected_leagues = st.multiselect('Choose leagues:', allt20s['CompName'].unique())

    if selected_leagues:
        data = allt20s[allt20s['CompName'].isin(selected_leagues)]
        # selected_leagues = st.selectbox('Choose leagues:', list(league_files.keys()))
        # data = load_data(league_files[selected_leagues])


        # Selectors for user input
        options = ['Overall Stats', 'Season By Season']
        # Create a select box
        choice = st.selectbox('Select your option:', options)
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        # choice3 = st.selectbox('Each bowling type or Pace vs Spin:', ['Each bowling type', 'Pace vs Spin'])
        # dic = {'Pace vs Spin': 'BowlCat', 'Each bowling type': 'Types'}
        # cat = dic[choice3]
        # User inputs for date range
        start_date = st.date_input('Start date', data['Date'].min())
        end_date = st.date_input('End date', data['Date'].max())

        # Filtering data based on the user's date selection
        if start_date > end_date:
            st.error('Error: End date must be greater than start date.')

        # start_year, end_year = st.slider('Select Years Range:', min_value=min(years), max_value=max(years),
        #                                  value=(min(years), max(years)))
        start_over, end_over = st.slider('Select Overs Range:', min_value=1, max_value=20, value=(1, 20))
        filtered_data = data[(data['over'] >= start_over) & (data['over'] <= end_over)]
        filtered_data2 = filtered_data[(filtered_data['Date'] >= pd.to_datetime(start_date)) & (filtered_data['Date'] <= pd.to_datetime(end_date))]
        # filtered_data2 = filtered_data[(filtered_data['year'] >= start_year) & (filtered_data['year'] <= end_year)]
        if choice2 == 'Individual':
            players = data['Batter'].unique()
            player = st.multiselect("Select Players:", players)
            # name = st.selectbox('Choose the Player From the list', data['striker'].unique())
        # cats = st.multiselect('Choose Specifics: ', filtered_data2[cat].unique())
        # if cats:
        #     filtered_data2 = filtered_data2[filtered_data2[cat].isin(cats)]

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

            truevalues = combined_data.groupby(['Player',])[
                ['I', 'Runs Scored', 'BF', 'Out', 'Expected Runs', 'Expected Outs']].sum().reset_index()
            final_results = truemetrics(truevalues)

            final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
            if choice == 'Overall Stats':
                if choice2 == 'Individual':
                    temp = []
                    for i in player:
                        if i in final_results['Player'].unique():
                            temp.append(i)
                        else:
                            st.subheader(f'{i} not in this list')
                    final_results = final_results[final_results['Player'].isin(temp)]


                final_results = final_results.sort_values(by=['Runs Scored'], ascending=False)
                st.dataframe(final_results.round(2))
            elif choice == 'Season By Season':
                if choice2 == 'Individual':
                    temp = []

                    for i in player:
                        if i in combined_data['Player'].unique():
                            temp.append(i)
                        else:
                            st.subheader(f'{i} not in this list')
                    combined_data = combined_data[combined_data['Player'].isin(temp)]
                combined_data = combined_data.sort_values(by=['Runs Scored'], ascending=False)
                st.dataframe(combined_data)



# Run the main function
if __name__ == '__main__':
    main()
