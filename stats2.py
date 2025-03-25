import math

import pandas as pd
import streamlit as st



@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data

def bowladjstats(df,start_date,end_date):
    filtered_data2 = df[(df['year'] >= start_date) & (df['year'] <= end_date)]
    df_match_totals = filtered_data2.groupby(['Bowler','BowlType','year']).agg(
        Matches = ('Matches','sum'),
        Inn=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wkts', 'sum'),
    ).reset_index()

    df_match_totals2 = filtered_data2.groupby(['BowlType','year']).agg(
        Matches = ('Matches','sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wkts', 'sum'),
    ).reset_index()

    bowling = pd.merge(df_match_totals, df_match_totals2, on=['BowlType','year'], suffixes=('', '_grouped'))

    bowling['matches_diff'] = bowling['Matches_grouped'] - bowling['Matches']
    bowling['run_diff'] = bowling['Runs_grouped'] - bowling['Runs']
    bowling['ball_diff'] = bowling['Balls_grouped'] - bowling['Balls']
    bowling['wickets_diff'] = bowling['Wickets_grouped'] - bowling['Wickets']


    # bowling = bowling[bowling['year'].isin(years_of_interest)]
    # bowling = bowling[bowling['Bowler'].isin(['R Ashwin','RA Jadeja'])]
    bowling2 = bowling.groupby(['Bowler','BowlType',]).agg(
        Matches = ('Matches','sum'),
        Inn=('Inn', 'sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wickets', 'sum'),
        matches_diff = ('matches_diff','sum'),
        run_diff = ('run_diff','sum'),
        ball_diff = ('ball_diff','sum'),
        wickets_diff = ('wickets_diff','sum'),
    ).reset_index()
    # batting2 = batting2[batting2['New Batter'].isin(batters3000)]
    bowling2['Ave'] = bowling2['Runs']/bowling2['Wickets']
    bowling2['Econ'] = bowling2['Runs']/bowling2['Balls']*6
    bowling2['SR'] = bowling2['Balls']/bowling2['Wickets']
    # bowling2['BPM'] = bowling2['Balls']/bowling2['Mat']
    bowling2['Mean Ave'] = bowling2['run_diff']/bowling2['wickets_diff']
    bowling2['Mean Econ'] = bowling2['run_diff']/bowling2['ball_diff']*6
    bowling2['Mean SR'] = bowling2['ball_diff']/bowling2['wickets_diff']

    bowling2['Era Ave Factor'] = bowling2['Mean Ave']/bowling2['Ave']
    bowling2['Era Econ Factor'] = bowling2['Mean Econ']/bowling2['Econ']
    bowling2['Era SR Factor'] = bowling2['Mean SR']/bowling2['SR']

    years_of_interest = list(range(2016, 2026))

    df_match_totals3 = df[df['year'].isin(years_of_interest)]
    # # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    df_match_totals3 = df_match_totals3.groupby(['BowlType']).agg(
        PresentMatches = ('Matches','sum'),
        PresentRuns=('Runs', 'sum'),
        PresentWickets=('Wkts', 'sum'),
        PresentBalls=('Balls', 'sum'),
    ).reset_index()
    #
    bowling3 = pd.merge(bowling2, df_match_totals3, on=['BowlType'], suffixes=('', '_grouped'))
    bowling3['PresentAve'] = bowling3['PresentRuns']/bowling3['PresentWickets']
    bowling3['PresentSR'] = bowling3['PresentBalls']/bowling3['PresentWickets']
    bowling3['PresentEcon'] = bowling3['PresentRuns']/bowling3['PresentBalls']*6
    bowling3['AdjAve'] = bowling3['PresentAve']/bowling3['Era Ave Factor']
    bowling3['AdjSR'] = bowling3['PresentSR']/bowling3['Era SR Factor']
    bowling3['AdjEcon'] = bowling3['PresentEcon']/bowling3['Era Econ Factor']
    bowling3['AdjWPM'] = (bowling3['Balls']/bowling3['Matches'])/bowling3['AdjSR']
    bowling3 = bowling3.drop(columns = ['matches_diff','run_diff','ball_diff','wickets_diff','Mean Ave','Mean Econ','Mean SR','PresentMatches','PresentRuns','PresentBalls','PresentWickets','PresentAve','PresentSR','PresentEcon',])
    return bowling3


def main():
    st.title('Adjusted ODI Stats')
    choice0 = st.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])
    if choice0 == 'Batting':
        data = load_data('OdiEraFactor2.csv')

        # data2 = data.groupby('New Batter')[['Runs']].sum().reset_index()
        # run = max((data2['Runs']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        # choice3 = st.multiselect('Home or Away:', ['Home', 'Away'])
        # choice5 = st.multiselect('Team:', data['Team'].unique())
        #    Filtering data based on the user's Date selection


        start_runs, end_runs = st.slider('Select Minimum Runs:', min_value=1, max_value=18426, value=(1, 18426))

        if choice2 == 'Individual':
            players = data['Batter'].unique()
            player = st.multiselect("Select Players:", players)
            # name = st.selectbox('Choose the Player From the list', data['striker'].unique())

        # A button to trigger the analysis
        if st.button('Analyse'):
            # Call a hypothetical function to analyze data

            results = data[
                (data['Runs'] >= start_runs) & (data['Runs'] <= end_runs)]

            if choice2 == 'Individual':
                temp = []
                for i in player:
                    if i in results['Batter'].unique():
                        temp.append(i)
                    else:
                        st.subheader(f'{i} not in this list')
                results = results[results['Batter'].isin(temp)]
                results = results.rename(columns={'Batter': 'Batsman'})

                st.dataframe(results[['Batsman','Inns', 'Runs', 'Balls', 'Outs','Fifties','Centuries','Ave','SR', 'Adjusted Ave','Adjusted Sr']].round(2))
            else:
                results = results.rename(columns={'Batter': 'Batsman'})

                results = results.sort_values(by=['Runs'], ascending=False)
                st.dataframe(results[['Batsman','Inns', 'Runs', 'Balls', 'Outs','Fifties','Centuries','Ave','SR', 'Adjusted Ave','Adjusted Sr']].round(2))
    else:
        filtered_data2 = load_data('odibowlinnsbyinnslist2.csv')
        # Create a select box
        filtered_data2['Start Date'] = pd.to_datetime(filtered_data2['Start Date'], errors='coerce')
        # start_date = st.date_input('Start date', data['Start Date'].min())
        # end_date = st.date_input('End date', data['Start Date'].max())
        # #
        # # # Filtering data based on the user's date selection
        # if start_date > end_date:
        #     st.error('Error: End date must be greater than start date.')
        #
        # filtered_data2 = data[
        #     (data['Start Date'] >= pd.to_datetime(start_date)) & (data['Start Date'] <= pd.to_datetime(end_date))]
        #
        start_date,end_date = st.slider('Select Year:', min_value=1971, max_value=2025, value=(1971, 2025))
        filtered_data2['year'] = pd.to_datetime(filtered_data2['Start Date'], format='mixed').dt.year

        #
        choice2 = st.multiselect('Pace or Spin:', ['Pace', 'Spin'])
        choice3 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        if choice2:
            filtered_data2 = filtered_data2[filtered_data2['BowlType'].isin(choice2)]
        if choice3 == 'Individual':
            players = filtered_data2['Bowler'].unique()
            player = st.multiselect("Select Players:", players)
        start_wickets, end_wickets = st.slider('Select Minimum Wickets:', min_value=1, max_value=535, value=(1, 535))
        if st.button('Analyse'):
            # Call a hypothetical function to analyze data

            results = bowladjstats(filtered_data2,start_date,end_date)
            results = results[
                (results['Wickets'] >= start_wickets) & (results['Wickets'] <= end_wickets)]

            if choice3 == 'Individual':
                temp = []
                for i in player:
                    if i in results['Bowler'].unique():
                        temp.append(i)
                    else:
                        st.subheader(f'{i} not in this list')
                results = results[results['Bowler'].isin(temp)]

                st.dataframe(results.round(2))
            else:

                results = results.sort_values(by=['Wickets'], ascending=False)
                st.dataframe(results.round(2))


# Run the main function
if __name__ == '__main__':
    main()
