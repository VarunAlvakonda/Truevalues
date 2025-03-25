import math

import pandas as pd
import streamlit as st

def matchfactor(data):

    final_results4 = data[data['Wickets at Entry'] >= 0]
    final_results4 = data

# final_results4 = final_results4[final_results4['Wickets at Entry'] <= 4]
    # final_results4 = final_results4[final_results4['New Batter'].isin(players)]
    final_results4['I'] = 1
    final_results4 = final_results4[~final_results4['Team'].isin(['ICC'])]

    # Define the years of interest
    years_of_interest = list(range(2018, 2025))

    # final_results4 = final_results4[final_results4['year'].isin(years_of_interest)]
    # final_results4 = final_results4[final_results4['Result']=='won']

    df_match_totals = final_results4.groupby(['New Batter', 'Team','Start Date','Host Country']).agg(
        Inns=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Outs=('Out', 'sum'),
        Balls=('BF', 'sum'),
    ).reset_index()

    # final_results4 = final_results2[final_results2['Wickets at Entry'] >= 0]
    # # final_results4 = final_results4[final_results4['New Batter'].isin(players)]
    final_results4 = final_results4[final_results4['Wickets at Entry'] <= 4]


    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    df_match_totals2 = final_results4.groupby(['Start Date','Host Country',]).agg(
        Runs=('Runs', 'sum'),
        Outs=('Out', 'sum'),
        Balls=('BF', 'sum'),
    ).reset_index()

    batting = pd.merge(df_match_totals, df_match_totals2, on=['Start Date','Host Country',], suffixes=('', '_grouped'))

    batting['run_diff'] = batting['Runs_grouped'] - batting['Runs']
    batting['out_diff'] = batting['Outs_grouped'] - batting['Outs']
    batting['ball_diff'] = batting['Balls_grouped'] - batting['Balls']

    batting['mean_ave'] = (batting['run_diff']) / (batting['out_diff'])
    batting['mean_sr'] = (batting['run_diff']) / (batting['ball_diff']) * 100

    # batting = batting[batting['Host Country'].isin(['England','South Africa','New Zealand','Australia'])]
    # batting = batting[batting['Team'].isin(['IND','BAN','SL','PAK'])]

    # batting.to_csv('toughruns.csv',index=False)
    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    final_results5 = batting.groupby(['New Batter','Team',])[
        ['Inns', 'Runs', 'Balls', 'Outs', 'Runs_grouped', 'Outs_grouped', 'run_diff', 'out_diff',
         'ball_diff']].sum().reset_index()

    final_results5['ave'] = (final_results5['Runs']) / (final_results5['Outs'])
    final_results5['sr'] = (final_results5['Runs']) / (final_results5['Balls']) * 100

    final_results5['mean_ave'] = (final_results5['run_diff']) / (final_results5['out_diff'])
    final_results5['mean_sr'] = (final_results5['run_diff']) / (final_results5['ball_diff']) * 100

    final_results5['Match Factor'] = (final_results5['ave']) / (final_results5['mean_ave'])
    final_results5['SR Ratio'] = (final_results5['sr']) / (final_results5['mean_sr'])

    # final_results5 = final_results5[final_results5['New Batter'].isin(names)]
    return final_results5[['New Batter','Team','Inns', 'Runs', 'Balls', 'Outs','ave','mean_ave','Match Factor',]].round(2)

def bowlmatchfactor(bowling):

    bowling2 = bowling.groupby(['Bowler','BowlType',]).agg(
        Mat=('Matches', 'sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wickets', 'sum'),
        run_diff = ('run_diff','sum'),
        ball_diff = ('ball_diff','sum'),
        wickets_diff = ('wickets_diff','sum'),
    ).reset_index()
    most_frequent_team = bowling.groupby(['Bowler','BowlType'])['Team'].agg(lambda x: x.mode().iat[0]).reset_index()
    bowling2 = pd.merge(bowling2, most_frequent_team, on=['Bowler','BowlType'], suffixes=('', '_grouped'))
    bowling2['Ave'] = bowling2['Runs']/bowling2['Wickets']
    bowling2['SR'] = bowling2['Balls']/bowling2['Wickets']
    bowling2['BPM'] = bowling2['Balls']/bowling2['Mat']
    bowling2['Mean Ave'] = bowling2['run_diff']/bowling2['wickets_diff']
    bowling2['Mean SR'] = bowling2['ball_diff']/bowling2['wickets_diff']
    bowling2['Match Factor'] = bowling2['Mean Ave']/bowling2['Ave']
    bowling2['SR Factor'] = bowling2['Mean SR']/bowling2['SR']
    return bowling2[['Bowler','BowlType','Team','Mat','Runs','Balls','Wickets','Ave','SR','BPM','Match Factor','SR Factor',]].round(2)



@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data

def main():
    st.title('Match Factor')
    choice0 = st.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])
    if choice0 == 'Batting':
        data = load_data('entrypoints.csv')

        data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')

        start_date = st.date_input('Start date', data['Start Date'].min())
        end_date = st.date_input('End date', data['Start Date'].max())

        # Filtering data based on the user's date selection
        if start_date > end_date:
            st.error('Error: End date must be greater than start date.')

        data2 = data.groupby('New Batter')[['Runs']].sum().reset_index()
        run = max((data2['Runs']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice = st.selectbox('Select your option:', options)
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        # choice3 = st.multiselect('Home or Away:', ['Home', 'Away'])
        choice4 = st.multiselect('Host Country:', data['Host Country'].unique())
        # choice5 = st.multiselect('Team:', data['Team'].unique())
    #    Filtering data based on the user's Date selection
        if start_date > end_date:
            st.error('Error: End Date must be greater than start Date.')

        start_runs, end_runs = st.slider('Select Minimum Runs:', min_value=1, max_value=run, value=(1, run))
        filtered_data = data
        filtered_data2 = filtered_data[
            (filtered_data['Start Date'] >= pd.to_datetime(start_date)) & (filtered_data['Start Date'] <= pd.to_datetime(end_date))]
        filtered_data2['year'] = pd.to_datetime(filtered_data2['Start Date'], format='mixed').dt.year

        if choice2 == 'Individual':
            players = filtered_data2['New Batter'].unique()
            player = st.multiselect("Select Players:", players)
            # name = st.selectbox('Choose the Player From the list', data['striker'].unique())
        # if choice3:
        #     filtered_data2 = filtered_data2[filtered_data2['HomeorAway'].isin(choice3)].copy()
        if choice4:
            filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)].copy()
        # if choice5:
        #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)].copy()
        inns = [1, 2,3,4]
        inn = st.multiselect("Select innings:", inns)
        if inn:
            filtered_data2 = filtered_data2[filtered_data2['Inns'].isin(inn)].copy()
        x = filtered_data2
        # A button to trigger the analysis

        if st.button('Analyse'):
            # Call a hypothetical function to analyze data

            results = matchfactor(filtered_data2)
            results = results[
                (results['Runs'] >= start_runs) & (results['Runs'] <= end_runs)]
            if choice == 'Overall':
                # Display the results
                if choice2 == 'Individual':
                    temp = []
                    for i in player:
                        if i in results['New Batter'].unique():
                            temp.append(i)
                        else:
                            st.subheader(f'{i} not in this list')
                    results = results[results['New Batter'].isin(temp)]
                    results = results.rename(columns={'New Batter': 'Batsman'})

                    st.dataframe(results.round(2))
                else:
                    results = results.rename(columns={'New Batter': 'Batsman'})

                    results = results.sort_values(by=['Runs'], ascending=False)
                    st.dataframe(results.round(2))
    else:
        data = load_data('toughwickets2.csv')
        data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')

        start_date = st.date_input('Start date', data['Start Date'].min())
        end_date = st.date_input('End date', data['Start Date'].max())

        # Filtering data based on the user's date selection
        if start_date > end_date:
            st.error('Error: End date must be greater than start date.')

        data2 = data.groupby('Bowler')[['Wickets']].sum().reset_index()
        run = max((data2['Wickets']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice = st.selectbox('Select your option:', options)
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        choice3 = st.multiselect('Pace or Spin:', ['Pace', 'Spin'])
        choice4 = st.multiselect('Host Country:', data['Host Country'].unique())
        # choice5 = st.multiselect('Team:', data['Team'].unique())
    #    Filtering data based on the user's Date selection
        if start_date > end_date:
            st.error('Error: End Date must be greater than start Date.')

        start_runs, end_runs = st.slider('Select Minimum Wickets:', min_value=1, max_value=run, value=(1, run))
        filtered_data = data
        filtered_data2 = filtered_data[
            (filtered_data['Start Date'] >= pd.to_datetime(start_date)) & (filtered_data['Start Date'] <= pd.to_datetime(end_date))]
        filtered_data2['year'] = pd.to_datetime(filtered_data2['Start Date'], format='mixed').dt.year

        if choice2 == 'Individual':
            players = filtered_data2['Bowler'].unique()
            player = st.multiselect("Select Players:", players)
            # name = st.selectbox('Choose the Player From the list', data['striker'].unique())
        if choice3:
            filtered_data2 = filtered_data2[filtered_data2['BowlType'].isin(choice3)].copy()
        if choice4:
            filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)].copy()
        # if choice5:
        #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)].copy()
        inns = [1, 2,3,4]
        inn = st.multiselect("Select innings:", inns)
        if inn:
            filtered_data2 = filtered_data2[filtered_data2['Inn'].isin(inn)].copy()
        x = filtered_data2
        # A button to trigger the analysis

        if st.button('Analyse'):
            # Call a hypothetical function to analyze data

            results = bowlmatchfactor(filtered_data2)
            results = results[
                (results['Wickets'] >= start_runs) & (results['Wickets'] <= end_runs)]
            if choice == 'Overall':
                # Display the results
                if choice2 == 'Individual':
                    temp = []
                    for i in player:
                        if i in results['Bowler'].unique():
                            temp.append(i)
                        else:
                            st.subheader(f'{i} not in this list')
                    results = results[results['Bowler'].isin(temp)]
                    results = results.rename(columns={'Bowler': 'Bowler'})

                    st.dataframe(results.round(2))
                else:
                    results = results.rename(columns={'Bowler': 'Bowler'})

                    results = results.sort_values(by=['Wickets'], ascending=False)
                    st.dataframe(results.round(2))



# Run the main function
if __name__ == '__main__':
    main()
