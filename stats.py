import math

import pandas as pd
import streamlit as st

def matchfactor(data,criteria,Position,typeoffactor):

    final_results4 = data[data['Batting Position'] >= 0]
    final_results4 = data

# final_results4 = final_results4[final_results4['Wickets at Entry'] <= 4]
    # final_results4 = final_results4[final_results4['New Batter'].isin(players)]
    final_results4['I'] = 1
    final_results4 = final_results4[~final_results4['Team'].isin(['ICC'])]

    # Define the years of interest
    years_of_interest = list(range(2018, 2025))

    # final_results4 = final_results4[final_results4['year'].isin(years_of_interest)]
    # final_results4 = final_results4[final_results4['Result']=='won']
    final_results4['Fifties'] = 0
    final_results4['Centuries'] = 0
    final_results4.loc[(final_results4['Runs'] >= 50) & (final_results4['Runs'] <= 99), 'Fifties'] = 1
    final_results4.loc[(final_results4['Runs'] >= 100), 'Centuries'] = 1
    final_results4.loc[(final_results4['BF'] > 0), 'RunswithBalls'] = final_results4['Runs']
    choice4 = st.multiselect('Keeper:', ['Yes'])
    final_results5 = final_results4
    if choice4:
        final_results5 = final_results5[final_results5['IsKeeper']=='Yes']
    choice4 = st.multiselect('Opposition:', data['Opposition'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Opposition'].isin(choice4)]
    choice4 = st.multiselect('Batting Position:', [1,2,3,4,5,6,7,8,9,10,11,12])
    if choice4:
        final_results5 = final_results5[final_results5['Batting Position'].isin(choice4)]

    df_match_totals = final_results5.groupby(['New Batter', 'Team','Start Date','Host Country','Opposition','year','HomeorAway']).agg(
        Inns=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Outs=('Out', 'sum'),
        Balls=('BF', 'sum'),
        Fifties = ('Fifties','sum'),
        Centuries = ('Centuries','sum'),
        RunswithBalls = ('RunswithBalls','sum')
    ).reset_index()

    # final_results4 = final_results2[final_results2['Wickets at Entry'] >= 0]
    # # final_results4 = final_results4[final_results4['New Batter'].isin(players)]
    final_results4 = final_results4[final_results4['Batting Position'] <= Position]

    if typeoffactor == 'Team and Opposition':
        # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
        df_match_totals2 = final_results4.groupby(['Start Date','Host Country','year']).agg(
            Runs=('Runs', 'sum'),
            Outs=('Out', 'sum'),
            Balls=('BF', 'sum'),
            Fifties = ('Fifties','sum'),
            Centuries = ('Centuries','sum'),
            RunswithBalls = ('RunswithBalls','sum')
        ).reset_index()

        batting = pd.merge(df_match_totals, df_match_totals2, on=['Start Date','Host Country','year',], suffixes=('', '_grouped'))
    else:
        df_match_totals2 = final_results4.groupby(['Team','Start Date','Host Country','year',]).agg(
            Runs=('Runs', 'sum'),
            Outs=('Out', 'sum'),
            Balls=('BF', 'sum'),
            Fifties = ('Fifties','sum'),
            Centuries = ('Centuries','sum'),
            RunswithBalls = ('RunswithBalls','sum')
        ).reset_index()


        batting = pd.merge(df_match_totals, df_match_totals2, on=['Team','Start Date','Host Country','year'], suffixes=('', '_grouped'))

    batting['cen_diff'] = batting['Centuries_grouped'] - batting['Centuries']
    batting['FiftiesPlus_diff'] = batting['Fifties_grouped']+batting['Centuries_grouped'] - batting['Fifties'] - batting['Centuries']
    batting['run_diff'] = batting['Runs_grouped'] - batting['Runs']
    batting['runswithballs_diff'] = batting['RunswithBalls_grouped'] - batting['RunswithBalls']
    batting['out_diff'] = batting['Outs_grouped'] - batting['Outs']
    batting['ball_diff'] = batting['Balls_grouped'] - batting['Balls']

    batting['mean_ave'] = (batting['run_diff']) / (batting['out_diff'])
    batting['mean_sr'] = (batting['runswithballs_diff']) / (batting['ball_diff']) * 100
    # run = max((batting['mean_ave']).astype(int))
    start_runs = 35
    if criteria == ['New Batter','Team',f'Top{Position}Average']:
        start_runs = st.slider('Select Average Threshold:', max_value=200)
    batting.loc[batting['mean_ave'] <= start_runs, f'Top{Position}Average'] = f'<={start_runs}'
    batting.loc[batting['mean_ave'] > start_runs, f'Top{Position}Average'] = f'>{start_runs}'
    # if criteria == ['New Batter','Team','EntryPoints']:
    #     batting = batting[batting['year']>=1999]
    #     start_runs = st.slider('Select Entry Over (from 1999):', max_value=500)
    # batting.loc[batting['EntryBalls'] <= start_runs, 'EntryPoints'] = f'<={start_runs}'
    # batting.loc[batting['EntryBalls'] > start_runs, 'EntryPoints'] = f'>{start_runs}'
    batting.loc[batting['cen_diff'] == start_runs, 'CenturiesScored'] = '0 Centuries'
    batting.loc[batting['FiftiesPlus_diff'] == start_runs, 'FiftyPlusScored'] = '0 FiftyPluses'
    # batting = batting[batting['Host Country'].isin(['England','South Africa','New Zealand','Australia'])]
    # batting = batting[batting['Team'].isin(['IND','BAN','SL','PAK'])]

    # batting.to_csv('toughruns.csv',index=False)
    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    if criteria == ['New Batter','Team','Overall']:
        final_results5 = batting.groupby(['New Batter','Team',])[
            ['Inns', 'Runs', 'Balls', 'Outs','Centuries','Fifties','RunswithBalls', 'Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff',
             'ball_diff','runswithballs_diff']].sum().reset_index()
    else:
        final_results5 = batting.groupby(criteria)[
            ['Inns', 'Runs', 'Balls', 'Outs','Centuries','Fifties','RunswithBalls', 'Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff',
             'ball_diff','runswithballs_diff']].sum().reset_index()

    final_results5['ave'] = (final_results5['Runs']) / (final_results5['Outs'])
    final_results5['sr'] = (final_results5['RunswithBalls']) / (final_results5['Balls'])*100
    final_results5['mean_ave'] = (final_results5['run_diff']) / (final_results5['out_diff'])
    final_results5['mean_sr'] = (final_results5['runswithballs_diff']) / (final_results5['ball_diff']) * 100
    final_results5['Match Factor'] = (final_results5['ave']) / (final_results5['mean_ave'])
    final_results5['Strike Factor'] = (final_results5['sr']) / (final_results5['mean_sr'])
    # final_results5 = final_results5[final_results5['New Batter'].isin(names)]
    final_results5 = final_results5.drop(columns=[ 'RunswithBalls','Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff','ball_diff','runswithballs_diff'])
    choice4 = st.multiselect('Team:', data['Team'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Team'].isin(choice4)]
    return final_results5
    # return final_results5[['New Batter','Team','Inns', 'Runs', 'Balls', 'Outs','ave','mean_ave','Match Factor',]].round(2)

def bowlmatchfactor(bowling,criteria):

    df_match_totals = bowling.groupby(['Bowler','Team','BowlType','Start Date','Ground','Host Country','year','OppRating']).agg(
        Inn=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wkts', 'sum'),
        Fivefer=('Fivefer', 'sum'),
        EliteFivefer=('EliteFivefer', 'sum'),
        Filth = ('Filth','sum')
    ).reset_index()
    df_match_totals['Matches'] = 1

    # bowling = bowling[~bowling['Bowler'].isin(['R Ashwin','RA Jadeja'])]
    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    print(bowling.dtypes)
    # bowling['Bowling Position'] = pd.to_numeric(bowling['Bowling Position'], errors='coerce')

    # bowling=bowling[bowling['Bowling Position']<=4]
    df_match_totals2 = bowling.groupby(['Start Date','BowlType','Ground','Host Country','year']).agg(
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wkts', 'sum'),
    ).reset_index()

    bowling = pd.merge(df_match_totals, df_match_totals2, on=['Start Date','BowlType','Ground','Host Country','year'], suffixes=('', '_grouped'))

    bowling['run_diff'] = bowling['Runs_grouped'] - bowling['Runs']
    bowling['ball_diff'] = bowling['Balls_grouped'] - bowling['Balls']
    bowling['wickets_diff'] = bowling['Wickets_grouped'] - bowling['Wickets']

    bowling['AveforWicket'] = (bowling['run_diff']) / (bowling['wickets_diff'])
    bowling['AveforWicket'] = (bowling['Runs_grouped']) / (bowling['Wickets_grouped'])

    bowling.loc[bowling['AveforWicket'] <= 35, 'AveWicket'] = '<=30'
    bowling.loc[bowling['AveforWicket'] > 35, 'AveWicket'] = '>30'

    if criteria == ['Bowler','BowlType','Overall']:
        bowling2 = bowling.groupby(['Bowler','BowlType']).agg(
            Mat=('Matches', 'sum'),
            Runs=('Runs', 'sum'),
            Balls = ('Balls','sum'),
            Wickets=('Wickets', 'sum'),
            run_diff = ('run_diff','sum'),
            ball_diff = ('ball_diff','sum'),
            wickets_diff = ('wickets_diff','sum'),
        ).reset_index()
    else:
        bowling2 = bowling.groupby(criteria).agg(
            Mat=('Matches', 'sum'),
            Runs=('Runs', 'sum'),
            Balls = ('Balls','sum'),
            Wickets=('Wickets', 'sum'),
            run_diff = ('run_diff','sum'),
            ball_diff = ('ball_diff','sum'),
            wickets_diff = ('wickets_diff','sum'),
        ).reset_index()
    # most_frequent_team = bowling.groupby(criteria)['Team'].agg(lambda x: x.mode().iat[0]).reset_index()
    # bowling2 = pd.merge(bowling2, most_frequent_team, on=criteria, suffixes=('', '_grouped'))
    bowling2['Ave'] = bowling2['Runs']/bowling2['Wickets']
    bowling2['SR'] = bowling2['Balls']/bowling2['Wickets']
    bowling2['Mean Ave'] = bowling2['run_diff']/bowling2['wickets_diff']
    bowling2['Mean SR'] = bowling2['ball_diff']/bowling2['wickets_diff']
    bowling2['Match Factor'] = bowling2['Mean Ave']/bowling2['Ave']
    bowling2['SR Factor'] = bowling2['Mean SR']/bowling2['SR']
    bowling2 = bowling2.drop(columns=[ 'Mean Ave', 'Mean SR','run_diff', 'wickets_diff','ball_diff'])
    return bowling2.round(2)



@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data

def main():
    st.title('Match Factor')
    choice0 = st.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])
    if choice0 == 'Batting':
        data = load_data('entrypoints.csv')
        factorchoice = st.selectbox('Select Match Factor by Team or Team and Opposition:', ['Team and Opposition','Team'])
        start_pos = st.slider('Select Batting Position Baseline:', min_value=1,max_value=12)
        data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')
        valid_dates = data['Start Date'].dropna()
        import datetime
        if not valid_dates.empty:
            min_dt = valid_dates.min().date()
            max_dt = valid_dates.max().date()
        else:
            min_dt = datetime.date(2000, 1, 1)
            max_dt = datetime.date(2030, 1, 1)

        start_date = st.date_input("Start date", min_value=min_dt, max_value=max_dt, value=min_dt)
        end_date = st.date_input("End date", min_value=min_dt, max_value=max_dt, value=max_dt)

        # Filtering data based on the user's date selection
        if start_date > end_date:
            st.error('Error: End date must be greater than start date.')

        data2 = data.groupby('New Batter')[['Runs']].sum().reset_index()
        run = max((data2['Runs']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice5 = st.selectbox('Additional Match Factor Groups:', ['Overall','Host Country', 'Opposition','year',f'Top{start_pos}Average','FiftyPlusScored','CenturiesScored','HomeorAway',])
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        # choice3 = st.multiselect('Home or Away:', ['Home', 'Away'])
        choice4 = st.multiselect('Host Country:', data['Host Country'].unique())
        # choice5 = st.multiselect('Team:', data['Team'].unique())
    #    Filtering data based on the user's Date selection


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
        #     filtered_data2 = filtered_data2[filtered_data2['HomeorAway'].isin(choice3)]
        if choice4:
            filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)]
        # if choice5:
        #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)]
        filtered_data2 = filtered_data2.rename(columns={'Result2':'Result or Draw'})
        # start_over, end_over = st.slider('Select Entry Over (1999 onwards):', min_value=1, max_value=run, value=(1, run))
        # # Track interaction manually
        # if 'slider_touched' not in st.session_state:
        #     st.session_state.slider_touched = False
        #
        # # When user changes the slider, flag it
        # if st.session_state.run_slider != (1, run):
        #     st.session_state.slider_touched = True
        #
        # # Now act only after interaction
        # if st.session_state.slider_touched:
        #     # Your logic here
        #     filtered_data2 = filtered_data2[filtered_data2['year']>=1999]


        # choice6 = st.multiselect('Result:', data['Result'].unique())
        # if choice6:
        #     filtered_data2 = filtered_data2[filtered_data2['Result'].isin(choice6)]
        x = filtered_data2
        # A button to trigger the analysis

        # if st.button('Analyse'):
        # Call a hypothetical function to analyze data

        results = matchfactor(filtered_data2,['New Batter','Team',choice5],start_pos,factorchoice)
        results = results[
            (results['Runs'] >= start_runs) & (results['Runs'] <= end_runs)]
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
        data = load_data('toughwickets.csv')
        data['Start Date'] = pd.to_datetime(data['Start Date'], errors='coerce')

        start_date = st.date_input('Start date', data['Start Date'].min())
        end_date = st.date_input('End date', data['Start Date'].max())

        # Filtering data based on the user's date selection
        if start_date > end_date:
            st.error('Error: End date must be greater than start date.')

        data2 = data.groupby('Bowler')[['Wkts']].sum().reset_index()
        run = max((data2['Wkts']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice = st.selectbox('Select your option:', options)
        choice2 = st.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        choice3 = st.multiselect('Pace or Spin:', ['Pace', 'Spin'])
        choice4 = st.multiselect('Host Country:', data['Host Country'].unique())
        # choice5 = st.multiselect('Team:', data['Team'].unique())
    #    Filtering data based on the user's Date selection
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
            filtered_data2 = filtered_data2[filtered_data2['BowlType'].isin(choice3)]
        if choice4:
            filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)]
        # if choice5:
        #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)]
        choice5 = st.selectbox('Additional Match Factor Groups:', ['Overall','Host Country', 'year',])
        x = filtered_data2
        # A button to trigger the analysis


        results = bowlmatchfactor(filtered_data2,['Bowler','BowlType',choice5])
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
