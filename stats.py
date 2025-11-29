import math

import numpy as np
import pandas as pd
import streamlit as st

def matchfactor(data,criteria,Position,typeoffactor):

    final_results4 = data[data['Batting_Position'] >= 0]
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

    final_results5 = final_results4
    choice4 = st.sidebar.multiselect('Batting_Position:', [1,2,3,4,5,6,7,8,9,10,11,12])
    if choice4:
        final_results5 = final_results5[final_results5['Batting_Position'].isin(choice4)]

    print(final_results5.columns)
    # Compute EntryBalls range
    min_age = int(final_results5['Age'].min())
    max_age = int(final_results5['Age'].max())
    # Slider for EntryBalls
    age_rage = st.sidebar.slider(
        "Choose Age Range:",
        min_value=min_age,
        max_value=max_age,
        value=(min_age, max_age)
    )

    # Apply filter only if slider is changed from default
    if age_rage != (min_age, max_age):
        final_results5 = final_results5[
            (final_results5['Age'] >= age_rage[0]) &
            (final_results5['Age'] <= age_rage[1])
            ]

    choice4 = st.sidebar.multiselect('Host Country:', data['Host Country'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Host Country'].isin(choice4)]

    choice4 = st.sidebar.multiselect('Opposition:', data['Opposition'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Opposition'].isin(choice4)]
    final_results5['IsKeeper'] = final_results5['IsKeeper'].fillna('No')
    choice4 = st.sidebar.multiselect('Keeper:', ['Yes','No'])
    if choice4:
        final_results5 = final_results5[final_results5['IsKeeper'].isin(choice4)]

    choice4 = st.sidebar.multiselect('Result:', data['Result'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Result'].isin(choice4)]


    choice4 = st.sidebar.multiselect('SeriesName:', data['SeriesName'].unique())

    if choice4:
        final_results5 = final_results5[final_results5['SeriesName'].isin(choice4)]

    if  int(final_results5['Batting_Position'].max()) >= 3:
        # Compute EntryBalls range
        min_entry = 0
        max_entry = int(final_results5['Runs at Entry'].max())

        # Slider for EntryBalls
        entry_range = st.sidebar.slider(
            "Choose Runs at Entry",
            min_value=min_entry,
            max_value=max_entry,
            value=(min_entry, max_entry)
        )


        final_results5 = final_results5[
            (final_results5['Runs at Entry'] >= entry_range[0]) &
            (final_results5['Runs at Entry'] <= entry_range[1])
            ]

        min_entry = 0
        max_entry = int(final_results5['Wickets at Entry'].max())

        # Slider for EntryBalls
        entry_range = st.sidebar.slider(
            "Choose Wickets at Entry",
            min_value=min_entry,
            max_value=max_entry,
            value=(min_entry, max_entry)
        )

        final_results5 = final_results5[
            (final_results5['Wickets at Entry'] >= entry_range[0]) &
            (final_results5['Wickets at Entry'] <= entry_range[1])
            ]

    # Compute EntryBalls range
    min_entry = 0
    max_entry = int(final_results5['EntryBalls'].max())
    if max_entry == 0:
        max_entry = 1
    # Slider for EntryBalls
    entry_range = st.sidebar.slider(
        "Choose Entry Over (only available from 1999) :",
        min_value=min_entry,
        max_value=max_entry,
        value=(min_entry, max_entry)
    )


    # Apply filter only if slider is changed from default
    if entry_range != (min_entry, max_entry):
        final_results5 = final_results5[final_results5['year']>=1999]
        final_results5 = final_results5[
            (final_results5['EntryBalls'] >= entry_range[0]) &
            (final_results5['EntryBalls'] <= entry_range[1])
            ]


    df_match_totals = final_results5.groupby(['New Batter', 'Team','PlayerID','Start_Date','Host Country','Opposition','year','HomeorAway','SeriesName']).agg(
        Inns=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Outs=('Out', 'sum'),
        Balls=('BF', 'sum'),
        Fifties = ('Fifties','sum'),
        Centuries = ('Centuries','sum'),
        RunswithBalls = ('RunswithBalls','sum')
    ).reset_index()
    df_match_totals['Matches'] = 1
    # final_results4 = final_results2[final_results2['Wickets at Entry'] >= 0]
    # # final_results4 = final_results4[final_results4['New Batter'].isin(players)]
    final_results4 = final_results4[final_results4['Batting_Position'] <= Position]

    if typeoffactor == 'Team and Opposition':
        # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
        df_match_totals2 = final_results4.groupby(['Start_Date','Host Country','year']).agg(
            Runs=('Runs', 'sum'),
            Outs=('Out', 'sum'),
            Balls=('BF', 'sum'),
            Fifties = ('Fifties','sum'),
            Centuries = ('Centuries','sum'),
            RunswithBalls = ('RunswithBalls','sum')
        ).reset_index()

        batting = pd.merge(df_match_totals, df_match_totals2, on=['Start_Date','Host Country','year',], suffixes=('', '_grouped'))
    else:
        df_match_totals2 = final_results4.groupby(['Team','Start_Date','Host Country','year',]).agg(
            Runs=('Runs', 'sum'),
            Outs=('Out', 'sum'),
            Balls=('BF', 'sum'),
            Fifties = ('Fifties','sum'),
            Centuries = ('Centuries','sum'),
            RunswithBalls = ('RunswithBalls','sum')
        ).reset_index()


        batting = pd.merge(df_match_totals, df_match_totals2, on=['Team','Start_Date','Host Country','year'], suffixes=('', '_grouped'))

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
    if criteria == ['New Batter', 'Team','PlayerID',f'Top{Position}Average']:
        start_runs = st.sidebar.slider('Select Average Threshold:', max_value=200)
    batting.loc[batting['mean_ave'] <= start_runs, f'Top{Position}Average'] = f'<={start_runs}'
    batting.loc[batting['mean_ave'] > start_runs, f'Top{Position}Average'] = f'>{start_runs}'
    # if criteria == ['New Batter', 'Team','PlayerID','EntryPoints']:
    #     batting = batting[batting['year']>=1999]
    #     start_runs = st.sidebar.slider('Select Entry Over (from 1999):', max_value=500)
    # batting.loc[batting['EntryBalls'] <= start_runs, 'EntryPoints'] = f'<={start_runs}'
    # batting.loc[batting['EntryBalls'] > start_runs, 'EntryPoints'] = f'>{start_runs}'
    batting.loc[batting['cen_diff'] == start_runs, 'CenturiesScored'] = '0 Centuries'
    batting.loc[batting['FiftiesPlus_diff'] == start_runs, 'FiftyPlusScored'] = '0 FiftyPluses'
    # batting = batting[batting['Host Country'].isin(['England','South Africa','New Zealand','Australia'])]
    # batting = batting[batting['Team'].isin(['IND','BAN','SL','PAK'])]

    # batting.to_csv('toughruns.csv',index=False)
    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    if criteria == ['New Batter', 'Team','PlayerID','Overall']:
        final_results5 = batting.groupby(['New Batter', 'Team','PlayerID',])[
            ['Matches','Inns', 'Runs', 'Balls', 'Outs','Centuries','Fifties','RunswithBalls', 'Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff',
             'ball_diff','runswithballs_diff']].sum().reset_index()
    else:
        final_results5 = batting.groupby(criteria)[
            ['Matches','Inns', 'Runs', 'Balls', 'Outs','Centuries','Fifties','RunswithBalls', 'Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff',
             'ball_diff','runswithballs_diff']].sum().reset_index()

    final_results5['ave'] = (final_results5['Runs']) / (final_results5['Outs'])
    final_results5['sr'] = (final_results5['RunswithBalls']) / (final_results5['Balls'])*100
    final_results5['mean_ave'] = (final_results5['run_diff']) / (final_results5['out_diff'])
    final_results5['mean_sr'] = (final_results5['runswithballs_diff']) / (final_results5['ball_diff']) * 100
    final_results5['Match Factor'] = (final_results5['ave']) / (final_results5['mean_ave'])
    final_results5['Strike Factor'] = (final_results5['sr']) / (final_results5['mean_sr'])
    # final_results5 = final_results5[final_results5['New Batter'].isin(names)]
    final_results5 = final_results5.drop(columns=['mean_ave', 'mean_sr','RunswithBalls','Runs_grouped', 'Outs_grouped','RunswithBalls_grouped', 'run_diff', 'out_diff','ball_diff','runswithballs_diff'])
    run = max((final_results5['Runs']).astype(int))
    start_runs, end_runs = st.sidebar.slider('Select Minimum Runs:', min_value=0, max_value=run, value=(1, run))
    final_results5 = final_results5[(final_results5['Runs'] >= start_runs) & (final_results5['Runs'] <= end_runs)]
    balls = max((final_results5['Balls']).astype(int))
    start_balls, end_balls = st.sidebar.slider('Select Minimum Balls:', min_value=0, max_value=balls, value=(0, balls))

    final_results5 = final_results5[(final_results5['Balls'] >= start_balls) & (final_results5['Balls'] <= end_balls)]
    choice4 = st.sidebar.multiselect('Team:', data['Team'].unique())
    if choice4:
        final_results5 = final_results5[final_results5['Team'].isin(choice4)]
    return final_results5
    # return final_results5[['New Batter', 'Team','PlayerID','Inns', 'Runs', 'Balls', 'Outs','ave','mean_ave','Match Factor',]].round(2)

def bowlmatchfactor(bowling,criteria):


    # bowling = bowling[~bowling['Bowler'].isin(['R Ashwin','RA Jadeja'])]
    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    print(bowling.dtypes)
    # bowling['Bowling Position'] = pd.to_numeric(bowling['Bowling Position'], errors='coerce')
    typeoffactor = st.sidebar.selectbox('Select Match Factor by Team or Team and Opposition:', ['Team and Opposition','Team'])
    # bowling=bowling[bowling['Bowling Position']<=4]
    typeoftype = st.sidebar.selectbox('Select Match Factor by BowlType or Overall:', ['BowlType','Overall'])
    bowling2 = bowling

    choice4 = st.sidebar.multiselect('Team:', bowling2['Team'].unique())
    if choice4:
        bowling2 = bowling2[bowling2['Team'].isin(choice4)]

    choice4 = st.sidebar.multiselect('Opposition:', bowling2['Opposition'].unique())
    if choice4:
        bowling2 = bowling2[bowling2['Opposition'].isin(choice4)]

    choice4 = st.sidebar.multiselect('Result:', bowling['Result'].unique())
    if choice4:
        bowling2 = bowling2[bowling2['Result'].isin(choice4)]


    choice4 = st.sidebar.multiselect('SeriesName:', bowling['SeriesName'].unique())

    if choice4:
        bowling2 = bowling2[bowling2['SeriesName'].isin(choice4)]

    df_match_totals = bowling2.groupby(['Bowler','Team','BowlType','PlayerID','Start_Date','Ground','Host Country','year','OppRating','SeriesName']).agg(
        Inn=('I', 'sum'),
        Runs=('Runs', 'sum'),
        Balls = ('Balls','sum'),
        Wickets=('Wkts', 'sum'),
        Fivefer=('Fivefer', 'sum'),
        EliteFivefer=('EliteFivefer', 'sum'),
        Filth = ('Filth','sum')
    ).reset_index()
    df_match_totals['Matches'] = 1

    if typeoffactor == 'Team and Opposition':
        # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
        if typeoftype == 'BowlType':
            df_match_totals2 = bowling.groupby(['Start_Date','BowlType','Ground','Host Country','year']).agg(
                Runs=('Runs', 'sum'),
                Balls = ('Balls','sum'),
                Wickets=('Wkts', 'sum'),
            ).reset_index()
            bowling = pd.merge(df_match_totals, df_match_totals2, on=['Start_Date','BowlType','Ground','Host Country','year'], suffixes=('', '_grouped'))
        else:
            df_match_totals2 = bowling.groupby(['Start_Date','Ground','Host Country','year']).agg(
                Runs=('Runs', 'sum'),
                Balls = ('Balls','sum'),
                Wickets=('Wkts', 'sum'),
            ).reset_index()
            bowling = pd.merge(df_match_totals, df_match_totals2, on=['Start_Date','Ground','Host Country','year'], suffixes=('', '_grouped'))
    else:
        if typeoftype == 'BowlType':
            df_match_totals2 = bowling.groupby(['Team','Start_Date','BowlType','Ground','Host Country','year']).agg(
                Runs=('Runs', 'sum'),
                Balls = ('Balls','sum'),
                Wickets=('Wkts', 'sum'),
            ).reset_index()

            bowling = pd.merge(df_match_totals, df_match_totals2, on=['Team','Start_Date','BowlType','Ground','Host Country','year'], suffixes=('', '_grouped'))
        else:
            df_match_totals2 = bowling.groupby(['Team','Start_Date','Ground','Host Country','year']).agg(
                Runs=('Runs', 'sum'),
                Balls = ('Balls','sum'),
                Wickets=('Wkts', 'sum'),
            ).reset_index()
            bowling = pd.merge(df_match_totals, df_match_totals2, on=['Team','Start_Date','Ground','Host Country','year'], suffixes=('', '_grouped'))


    bowling['run_diff'] = bowling['Runs_grouped'] - bowling['Runs']
    bowling['ball_diff'] = bowling['Balls_grouped'] - bowling['Balls']
    bowling['wickets_diff'] = bowling['Wickets_grouped'] - bowling['Wickets']

    bowling['AveforWicket'] = (bowling['run_diff']) / (bowling['wickets_diff'])
    # bowling['AveforWicket'] = (bowling['Runs_grouped']) / (bowling['Wickets_grouped'])

    # bowling.loc[bowling['AveforWicket'] <= 35, 'AveWicket'] = '<=30'
    # bowling.loc[bowling['AveforWicket'] > 35, 'AveWicket'] = '>30'
    start_runs = 35
    if criteria == ['Bowler','Team','BowlType','PlayerID','OtherBowlersAverage']:
        start_runs = st.sidebar.slider('Select Average Threshold:', max_value=200)
    bowling.loc[bowling['AveforWicket'] <= start_runs, 'OtherBowlersAverage'] = f'<={start_runs}'
    bowling.loc[bowling['AveforWicket'] > start_runs, 'OtherBowlersAverage'] = f'>{start_runs}'

    if criteria == ['Bowler','Team','BowlType','PlayerID','Overall']:
        bowling2 = bowling.groupby(['Bowler','Team','BowlType','PlayerID',]).agg(
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
    bowling2['mean_ave'] = (bowling2['run_diff']) / (bowling2['wickets_diff'])
    # run = max((batting['mean_ave']).astype(int))
    # start_runs = 35
    # if criteria == ['Bowler','Team','BowlType','PlayerID','OtherBowlersAverage']:
    #     start_runs = st.sidebar.slider('Select Average Threshold:', max_value=200)
    # bowling2.loc[bowling2['mean_ave'] <= start_runs, 'OtherBowlersAverage'] = f'<={start_runs}'
    # bowling2.loc[bowling2['mean_ave'] > start_runs, 'OtherBowlersAverage'] = f'>{start_runs}'
    bowling2 = bowling2.drop(columns=['run_diff', 'wickets_diff','ball_diff','mean_ave'])
    return bowling2.round(2)

def find_peak_period_actual_runs(df, streak):
    streak_length = streak
    peak_period = []
    min_fac = float('-inf')

    # Convert to numpy arrays for faster iteration
    runs = df['Runs'].values
    wkts = df['Wkts'].values
    balls = df['Balls'].values
    run_diff = df['run_diff'].values
    out_diff = df['out_diff'].values
    ball_diff = df['ball_diff'].values

    # For each starting position
    for i in range(len(df) - streak_length + 1):
        run_sum = runs[i:i+streak_length].sum()
        out_sum = wkts[i:i+streak_length].sum()
        ball_sum = balls[i:i+streak_length].sum()
        run_diff_sum = run_diff[i:i+streak_length].sum()
        out_diff_sum = out_diff[i:i+streak_length].sum()
        ball_diff_sum = ball_diff[i:i+streak_length].sum()

        # Avoid division by zero
        if out_sum == 0 or out_diff_sum == 0:
            continue

        run_avg = run_sum / out_sum
        mean_avg = run_diff_sum / out_diff_sum
        fac = mean_avg / run_avg

        # Update if we find a better (higher) fac
        if fac > min_fac:
            min_fac = fac
            peak_period = df.index[i:i+streak_length]

    return peak_period


def find_lowest_average_200_wickets_with_leeway(df, wickets):
    target_wickets = wickets
    lowest_fac = float('-inf')
    peak_period = []

    # Pre-compute cumulative sums for faster window calculations
    cumsum_wkts = df['Wkts'].cumsum()
    cumsum_runs = df['Runs'].cumsum()
    cumsum_out_diff = df['out_diff'].cumsum()
    cumsum_run_diff = df['run_diff'].cumsum()

    n = len(df)

    # Use numpy arrays for faster iteration
    wkts_arr = cumsum_wkts.values
    runs_arr = cumsum_runs.values
    out_diff_arr = cumsum_out_diff.values
    run_diff_arr = cumsum_run_diff.values

    for i in range(n):
        # Binary search or vectorized search for end point where wickets >= target
        # Calculate cumulative wickets from position i
        wickets_from_i = wkts_arr - (wkts_arr[i-1] if i > 0 else 0)

        # Find first index where wickets >= target
        valid_indices = np.where(wickets_from_i >= target_wickets)[0]

        if len(valid_indices) == 0:
            break  # No more valid streaks possible

        j = valid_indices[0]

        # Calculate sums for window [i, j]
        wicket_sum = wkts_arr[j] - (wkts_arr[i-1] if i > 0 else 0)
        run_sum = runs_arr[j] - (runs_arr[i-1] if i > 0 else 0)
        out_diff = out_diff_arr[j] - (out_diff_arr[i-1] if i > 0 else 0)
        run_diff = run_diff_arr[j] - (run_diff_arr[i-1] if i > 0 else 0)

        if out_diff > 0:
            bowling_avg = run_sum / wicket_sum
            mean_avg = run_diff / out_diff
            bowling_fac = mean_avg / bowling_avg

            if bowling_fac > lowest_fac:
                lowest_fac = bowling_fac
                peak_period = df.index[i:j+1]

    return peak_period



@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data

def main():
    st.sidebar.title('Match Factor')
    choice0 = st.sidebar.selectbox('Batting Or Bowling:', ['Batting', 'Bowling'])
    if choice0 == 'Batting':
        data = load_data('entrypoints.csv')
        factorchoice = st.sidebar.selectbox('Select Match Factor by Team or Team and Opposition:', ['Team and Opposition','Team'])
        start_pos = st.sidebar.slider('Select Batting_Position Baseline:', min_value=1,max_value=12)
        data['Start_Date'] = pd.to_datetime(data['Start_Date'], errors='coerce')
        valid_dates = data['Start_Date'].dropna()
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

        data2 = data.groupby('New Batter')[['Runs']].sum().reset_index()
        run = max((data2['Runs']).astype(int))

        # Selectors for user input
        options = ['Overall',]

        # Create a select box
        choice5 = st.sidebar.selectbox('Additional Match Factor Groups:', ['Overall','Host Country', 'Opposition','year',f'Top{start_pos}Average','FiftyPlusScored','CenturiesScored','HomeorAway','SeriesName'])
        choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
        # choice3 = st.sidebar.multiselect('Home or Away:', ['Home', 'Away'])
        # choice4 = st.sidebar.multiselect('Host Country:', data['Host Country'].unique())
        # choice5 = st.sidebar.multiselect('Team:', data['Team'].unique())
    #    Filtering data based on the user's Date selection


        # start_runs, end_runs = st.sidebar.slider('Select Minimum Runs:', min_value=1, max_value=run, value=(1, run))
        filtered_data = data
        filtered_data2 = filtered_data[
            (filtered_data['Start_Date'] >= pd.to_datetime(start_date)) & (filtered_data['Start_Date'] <= pd.to_datetime(end_date))]
        filtered_data2['year'] = pd.to_datetime(filtered_data2['Start_Date'], format='mixed').dt.year

        if choice2 == 'Individual':
            players = filtered_data2['New Batter'].unique()
            player = st.sidebar.multiselect("Select Players:", players)
            # name = st.sidebar.selectbox('Choose the Player From the list', data['striker'].unique())
        # if choice3:
        #     filtered_data2 = filtered_data2[filtered_data2['HomeorAway'].isin(choice3)]
        # if choice4:
        #     filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)]
        # if choice5:
        #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)]
        filtered_data2 = filtered_data2.rename(columns={'Result2':'Result or Draw'})
        # start_over, end_over = st.sidebar.slider('Select Entry Over (1999 onwards):', min_value=1, max_value=run, value=(1, run))
        # # Track interaction manually
        # if 'slider_touched' not in st.sidebar.session_state:
        #     st.sidebar.session_state.slider_touched = False
        #
        # # When user changes the slider, flag it
        # if st.sidebar.session_state.run_slider != (1, run):
        #     st.sidebar.session_state.slider_touched = True
        #
        # # Now act only after interaction
        # if st.sidebar.session_state.slider_touched:
        #     # Your logic here
        #     filtered_data2 = filtered_data2[filtered_data2['year']>=1999]


        # choice6 = st.sidebar.multiselect('Result:', data['Result'].unique())
        # if choice6:
        #     filtered_data2 = filtered_data2[filtered_data2['Result'].isin(choice6)]
        x = filtered_data2
        # A button to trigger the analysis

        # if st.sidebar.button('Analyse'):
        # Call a hypothetical function to analyze data

        results = matchfactor(filtered_data2,['New Batter', 'Team','PlayerID',choice5],start_pos,factorchoice)
        # results = results[
        #     (results['Runs'] >= start_runs) & (results['Runs'] <= end_runs)]
        # Display the results
        if choice2 == 'Individual':
            temp = []
            for i in player:
                if i in results['New Batter'].unique():
                    temp.append(i)
                else:
                    st.sidebar.subheader(f'{i} not in this list')
            results = results[results['New Batter'].isin(temp)]
            results = results.rename(columns={'New Batter': 'Batsman'})

            st.dataframe(results.round(2), use_container_width=True)
        else:
            results = results.rename(columns={'New Batter': 'Batsman'})

            results = results.sort_values(by=['Runs'], ascending=False)
            st.dataframe(results.round(2), use_container_width=True)
    else:
        data = load_data('toughwickets.csv')
        data['Start_Date'] = pd.to_datetime(data['Start_Date'], errors='coerce')
        valid_dates = data['Start_Date'].dropna()
        # valid_dates = data
        import datetime
        if not valid_dates.empty:
            min_dt = valid_dates.min().date()
            max_dt = valid_dates.max().date()
        else:
            min_dt = datetime.date(2000, 1, 1)
            max_dt = datetime.date(2030, 1, 1)

        peaksornot = st.sidebar.selectbox('Bowling Peaks:', ['Yes', 'No'])
        if peaksornot =='No':
            start_date = st.sidebar.date_input("Start date", min_value=min_dt, max_value=max_dt, value=min_dt)
            end_date = st.sidebar.date_input("End date", min_value=min_dt, max_value=max_dt, value=max_dt)


            # Filtering data based on the user's date selection
            if start_date > end_date:
                st.sidebar.error('Error: End date must be greater than start date.')

            data2 = data.groupby('Bowler')[['Wkts']].sum().reset_index()
            run = max((data2['Wkts']).astype(int))

            # Selectors for user input
            options = ['Overall',]

            # Create a select box
            choice = st.sidebar.selectbox('Select your option:', options)
            choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
            choice3 = st.sidebar.multiselect('Pace or Spin:', ['Pace', 'Spin'])
            choice4 = st.sidebar.multiselect('Host Country:', data['Host Country'].unique())
            # choice5 = st.sidebar.multiselect('Team:', data['Team'].unique())
        #    Filtering data based on the user's Date selection
            start_runs, end_runs = st.sidebar.slider('Select Minimum Wickets:', min_value=1, max_value=run, value=(1, run))
            filtered_data = data
            filtered_data2 = filtered_data[
                (filtered_data['Start_Date'] >= pd.to_datetime(start_date)) & (filtered_data['Start_Date'] <= pd.to_datetime(end_date))]
            filtered_data2['year'] = pd.to_datetime(filtered_data2['Start_Date'], format='mixed').dt.year

            if choice2 == 'Individual':
                players = filtered_data2['Bowler'].unique()
                player = st.sidebar.multiselect("Select Players:", players)
                # name = st.sidebar.selectbox('Choose the Player From the list', data['striker'].unique())
            if choice3:
                filtered_data2 = filtered_data2[filtered_data2['BowlType'].isin(choice3)]
            if choice4:
                filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)]
            # if choice5:
            #     filtered_data2 = filtered_data2[filtered_data2['Team'].isin(choice5)]
            choice5 = st.sidebar.selectbox('Additional Match Factor Groups:', ['Overall','Host Country', 'year','SeriesName','OtherBowlersAverage'])
            x = filtered_data2
            # A button to trigger the analysis


            results = bowlmatchfactor(filtered_data2,['Bowler','Team','BowlType','PlayerID',choice5])
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
                            st.sidebar.subheader(f'{i} not in this list')
                    results = results[results['Bowler'].isin(temp)]
                    results = results.rename(columns={'Bowler': 'Bowler'})

                    st.dataframe(results.round(2), use_container_width=True)
                else:
                    results = results.rename(columns={'Bowler': 'Bowler'})

                    results = results.sort_values(by=['Wickets'], ascending=False)
                    st.dataframe(results.round(2), use_container_width=True)
        else:
            # Selectors for user input
            options = ['N Number of Wickets','N Number of Innings']

            # Create a select box
            choice = st.sidebar.selectbox('Do you want Peaks by Number of Innings or Wickets:', options)
            if choice:
                choice2 = st.sidebar.selectbox('Individual Player or Everyone:', ['Individual', 'Everyone'])
                choice3 = st.sidebar.multiselect('Pace or Spin:', ['Pace', 'Spin'])
                choice4 = st.sidebar.multiselect('Host Country:', data['Host Country'].unique())
                data2 = data.groupby('Bowler')[['Wkts']].sum().reset_index()
                wkts = max((data2['Wkts']).astype(int))

                innings_per_bowler = data.groupby('Bowler')['Start_Date'].count().reset_index()
                innings_per_bowler.columns = ['Bowler', 'Innings']

                # Get the maximum number of matches
                max_matches = innings_per_bowler['Matches'].max()


                filtered_data2 = data
                if choice2 == 'Individual':
                    players = filtered_data2['Bowler'].unique()
                    player = st.sidebar.multiselect("Select Players:", players)
                    # name = st.sidebar.selectbox('Choose the Player From the list', data['striker'].unique())
                if choice3:
                    filtered_data2 = filtered_data2[filtered_data2['BowlType'].isin(choice3)]
                if choice4:
                    filtered_data2 = filtered_data2[filtered_data2['Host Country'].isin(choice4)]

                if choice == 'N Number of Wickets':
                    start_runs= st.sidebar.slider('Select the wicket threshold for peaks:', min_value=1,max_value=wkts)
                else:
                    start_runs = st.sidebar.slider('Select the match threshold for peaks:', min_value=1,max_value=max_matches)


                # Create a new 'ispeak' column, default set to 0
                filtered_data2['ispeak'] = 'NotPeak'



                final_results4 = filtered_data2.groupby(['BowlType','Start_Date','Host Country']).agg(
                    InnsTotal = ('I', 'sum'),
                    RunsTotal = ('Runs', 'sum'),
                    OutsTotal = ('Wkts', 'sum'),
                    BallsTotal = ('Balls','sum')
                ).reset_index()

                data2 = pd.merge(filtered_data2, final_results4, on=['BowlType','Start_Date', 'Host Country'], how='left')

                data2 = data2.drop_duplicates()

                data2['inn_diff'] = data2['InnsTotal'] - data2['I']
                data2['run_diff'] = data2['RunsTotal'] - data2['Runs']
                data2['out_diff'] = data2['OutsTotal'] - data2['Wkts']
                data2['ball_diff'] = data2['BallsTotal'] - data2['Balls']

                data2['I'] = 1

                # Apply the peak period calculation for each batter
                for batter, group in data2.groupby('Bowler'):
                    if choice == 'N Number of Innings':
                        peak_matches = find_peak_period_actual_runs(group,start_runs)
                    else:
                        peak_matches = find_lowest_average_200_wickets_with_leeway(group,start_runs)
                    data2.loc[peak_matches, 'ispeak'] = 'Peak'


                streaks_summary = data2.groupby(['Bowler','BowlType','PlayerID','ispeak']).agg(
                    Innings=('I', 'sum'),
                    Runs=('Runs', 'sum'),
                    Balls = ('Balls','sum'),
                    Wkts=('Wkts', 'sum'),
                    inn_diff=('inn_diff', 'sum'),
                    run_diff=('run_diff', 'sum'),
                    ball_diff=('ball_diff', 'sum'),
                    out_diff=('out_diff', 'sum'),
                    StartofPeak = ('Start_Date','min'),
                    EndofPeak = ('Start_Date','max'),
                ).reset_index()

                streaks_summary['Ave'] = streaks_summary['Runs']/streaks_summary['Wkts']
                streaks_summary['Mean Ave'] = streaks_summary['run_diff']/streaks_summary['out_diff']

                streaks_summary['SR'] = streaks_summary['Balls']/streaks_summary['Wkts']
                streaks_summary['Mean SR'] = streaks_summary['ball_diff']/streaks_summary['out_diff']

                streaks_summary['Match Factor'] = streaks_summary['Mean Ave']/streaks_summary['Ave']
                streaks_summary['Strike Rate Factor'] = streaks_summary['Mean SR']/streaks_summary['SR']

                streaks_summary = streaks_summary[streaks_summary['ispeak']=='Peak']
                streaks_summary = streaks_summary.drop(columns=['ispeak','inn_diff','run_diff','ball_diff','out_diff','Mean Ave','Mean SR',])
                streaks_summary['StartofPeak'] = pd.to_datetime(streaks_summary['StartofPeak']).dt.strftime('%d %b %Y')
                streaks_summary['EndofPeak'] = pd.to_datetime(streaks_summary['EndofPeak']).dt.strftime('%d %b %Y')


                if choice2 == 'Individual':
                    temp = []
                    for i in player:
                        if i in streaks_summary['Bowler'].unique():
                            temp.append(i)
                        else:
                            st.sidebar.subheader(f'{i} not in this list')
                    streaks_summary = streaks_summary[streaks_summary['Bowler'].isin(temp)]
                    streaks_summary = streaks_summary.rename(columns={'Bowler': 'Bowler'})

                    st.dataframe(streaks_summary.round(2), use_container_width=True)
                else:
                    streaks_summary = streaks_summary.rename(columns={'Bowler': 'Bowler'})

                    streaks_summary = streaks_summary.sort_values(by=['Match Factor'], ascending=False)
                    st.dataframe(streaks_summary.round(2), use_container_width=True)



# Run the main function
if __name__ == '__main__':
    main()
