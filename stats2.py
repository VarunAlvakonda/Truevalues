import math

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(filename):
    data = pd.read_csv(filename, low_memory=False)
    return data


def batadjstats(df, start_date, end_date):
    filtered_data2 = df[(df["year"] >= start_date) & (df["year"] <= end_date)]
    filtered_data2.loc[filtered_data2["Batting_Position"] == 2, "Batting_Position"] = 1

    year1, year2 = st.slider(
        "Select Era Adjustment Baseline (Default is 2016-Now):",
        min_value=1971,
        max_value=2026,
        value=(2016, 2026),
    )

    years_of_interest = list(range(year1, year2 + 1))

    df_match_totals3 = df[df["year"].isin(years_of_interest)]
    # final_results4= final_results4[final_results4['OppRating']>1600]
    # Define the years of interest

    choice4 = st.multiselect("Batting_Position:", [1, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    if choice4:
        filtered_data2 = filtered_data2[
            filtered_data2["Batting_Position"].isin(choice4)
        ]

    filtered_data3 = filtered_data2.copy()
    choice4 = st.multiselect(
        "Opposition:", sorted(filtered_data3["Opposition"].unique())
    )
    if choice4:
        filtered_data3 = filtered_data3[filtered_data3["Opposition"].isin(choice4)]

    filtered_data3["IsKeeper"] = filtered_data3["IsKeeper"].fillna("No")

    choice4 = st.multiselect("Result:", filtered_data3["Result"].unique())
    if choice4:
        filtered_data3 = filtered_data3[filtered_data3["Result"].isin(choice4)]

    choice4 = st.multiselect("Keeper:", ["Yes", "No"])

    if choice4:
        filtered_data3 = filtered_data3[filtered_data3["IsKeeper"].isin(choice4)]

    choice_grp = st.selectbox("Overall or By Year:", ["Overall", "year"])

    df_match_totals = (
        filtered_data3.groupby(["New Batter", "Team", "year", "Batting_Position"])
        .agg(
            Inns=("I", "sum"),
            Runs=("Runs", "sum"),
            Outs=("Out", "sum"),
            Balls=("BF", "sum"),
            Fifties=("Fifties", "sum"),
            Centuries=("Centuries", "sum"),
        )
        .reset_index()
    )

    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    df_match_totals2 = (
        filtered_data2.groupby(["year", "Batting_Position"])
        .agg(
            Inns=("I", "sum"),
            Runs=("Runs", "sum"),
            Outs=("Out", "sum"),
            Balls=("BF", "sum"),
            Fifties=("Fifties", "sum"),
            Centuries=("Centuries", "sum"),
        )
        .reset_index()
    )

    # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    df_match_totals3 = (
        df_match_totals3.groupby(["Batting_Position"])
        .agg(
            PresentInns=("I", "sum"),
            PresentRuns=("Runs", "sum"),
            PresentOuts=("Out", "sum"),
            PresentBalls=("BF", "sum"),
            PresentFifties=("Fifties", "sum"),
            PresentCenturies=("Centuries", "sum"),
        )
        .reset_index()
    )

    batting = pd.merge(
        df_match_totals,
        df_match_totals2,
        on=["year", "Batting_Position"],
        suffixes=("", "_grouped"),
    )

    batting["run_diff"] = batting["Runs_grouped"] - batting["Runs"]
    batting["out_diff"] = batting["Outs_grouped"] - batting["Outs"]
    batting["ball_diff"] = batting["Balls_grouped"] - batting["Balls"]
    batting["cen_diff"] = batting["Centuries_grouped"] - batting["Centuries"]
    batting["Fifties_diff"] = batting["Fifties_grouped"] - batting["Fifties"]
    batting["inn_diff"] = batting["Inns_grouped"] - batting["Inns"]

    batting["BSR"] = batting["run_diff"] / batting["ball_diff"]
    batting["OPB"] = batting["out_diff"] / batting["ball_diff"]
    batting["FPI"] = batting["Fifties_diff"] / batting["inn_diff"]
    batting["CPI"] = batting["cen_diff"] / batting["inn_diff"]

    batting["Expected Runs"] = batting["Balls"] * batting["BSR"]
    batting["Expected Outs"] = batting["Balls"] * batting["OPB"]
    batting["Expected Fifties"] = batting["Inns"] * batting["FPI"]
    batting["Expected Centuries"] = batting["Inns"] * batting["CPI"]

    if choice_grp == "year":
        final_results5 = (
            batting.groupby(["New Batter", "Team", "Batting_Position", "year"])[
                [
                    "Inns",
                    "Runs",
                    "Balls",
                    "Outs",
                    "Fifties",
                    "Centuries",
                    "Expected Runs",
                    "Expected Outs",
                    "Expected Fifties",
                    "Expected Centuries",
                ]
            ]
            .sum()
            .reset_index()
        )
    else:
        final_results5 = (
            batting.groupby(["New Batter", "Team", "Batting_Position"])[
                [
                    "Inns",
                    "Runs",
                    "Balls",
                    "Outs",
                    "Fifties",
                    "Centuries",
                    "Expected Runs",
                    "Expected Outs",
                    "Expected Fifties",
                    "Expected Centuries",
                ]
            ]
            .sum()
            .reset_index()
        )

    batting = pd.merge(
        final_results5,
        df_match_totals3,
        on=["Batting_Position"],
        suffixes=("", "_grouped"),
    )

    batting["BSR"] = batting["PresentRuns"] / batting["PresentBalls"]
    batting["OPB"] = batting["PresentOuts"] / batting["PresentBalls"]
    batting["FPI"] = batting["PresentFifties"] / batting["PresentInns"]
    batting["CPI"] = batting["PresentCenturies"] / batting["PresentInns"]

    batting["Expected Runs 2"] = batting["Balls"] * batting["BSR"]
    batting["Expected Outs 2"] = batting["Balls"] * batting["OPB"]
    batting["Expected Fifties 2"] = batting["Inns"] * batting["FPI"]
    batting["Expected Centuries 2"] = batting["Inns"] * batting["CPI"]

    if choice_grp == "Overall":
        final_results5 = (
            batting.groupby(
                [
                    "New Batter",
                    "Team",
                ]
            )[
                [
                    "Inns",
                    "Runs",
                    "Balls",
                    "Outs",
                    "Fifties",
                    "Centuries",
                    "Expected Runs",
                    "Expected Outs",
                    "Expected Fifties",
                    "Expected Centuries",
                    "Expected Runs 2",
                    "Expected Outs 2",
                    "Expected Fifties 2",
                    "Expected Centuries 2",
                ]
            ]
            .sum()
            .reset_index()
        )

    else:
        final_results5 = (
            batting.groupby(["New Batter", "Team", "year"])[
                [
                    "Inns",
                    "Runs",
                    "Balls",
                    "Outs",
                    "Fifties",
                    "Centuries",
                    "Expected Runs",
                    "Expected Outs",
                    "Expected Fifties",
                    "Expected Centuries",
                    "Expected Runs 2",
                    "Expected Outs 2",
                    "Expected Fifties 2",
                    "Expected Centuries 2",
                ]
            ]
            .sum()
            .reset_index()
        )

    final_results5["ave"] = (final_results5["Runs"]) / (final_results5["Outs"])
    final_results5["sr"] = (final_results5["Runs"]) / (final_results5["Balls"]) * 100
    final_results5["InnsPerCentury"] = (
        (final_results5["Inns"]) / (final_results5["Centuries"])
    )

    final_results5["expected_ave"] = (
        (final_results5["Expected Runs"]) / (final_results5["Expected Outs"])
    )
    final_results5["expected_sr"] = (
        (final_results5["Expected Runs"]) / (final_results5["Balls"]) * 100
    )
    final_results5["expinnsPerCentury"] = (
        (final_results5["Inns"]) / (final_results5["Expected Centuries"])
    )

    final_results5["Ave Ratio"] = (
        (final_results5["ave"]) / (final_results5["expected_ave"])
    )
    final_results5["SR Ratio"] = (
        (final_results5["sr"]) / (final_results5["expected_sr"])
    )
    final_results5["Cen Ratio"] = (
        (final_results5["Centuries"]) / (final_results5["Expected Centuries"])
    )

    final_results5["expected_ave_present"] = (
        (final_results5["Expected Runs 2"]) / (final_results5["Expected Outs 2"])
    )
    final_results5["expected_sr_present"] = (
        (final_results5["Expected Runs 2"]) / (final_results5["Balls"]) * 100
    )

    final_results5["Zulu Ave"] = (
        final_results5["expected_ave_present"] * final_results5["Ave Ratio"]
    )
    final_results5["Zulu Sr"] = (
        final_results5["expected_sr_present"] * final_results5["SR Ratio"]
    )
    final_results5 = final_results5.drop(
        columns=[
            "Expected Runs",
            "Expected Outs",
            "Expected Fifties",
            "Expected Centuries",
            "Expected Runs 2",
            "Expected Outs 2",
            "Expected Fifties 2",
            "Expected Centuries 2",
            "Ave Ratio",
            "SR Ratio",
            "Cen Ratio",
            "expected_ave",
            "expected_sr",
            "expected_ave_present",
            "expected_sr_present",
            "InnsPerCentury",
            "expinnsPerCentury",
        ]
    )
    choice4 = st.multiselect("Team:", sorted(final_results5["Team"].unique()))
    if choice4:
        final_results5 = final_results5[final_results5["Team"].isin(choice4)]
    return final_results5


def bowladjstats(df, start_date, end_date):
    year1, year2 = st.slider(
        "Select Era Adjustment Baseline (Default is 2016-Now):",
        min_value=1971,
        max_value=2026,
        value=(2016, 2026),
    )

    years_of_interest = list(range(year1, year2 + 1))

    df_match_totals3 = df[df["year"].isin(years_of_interest)].copy()
    filtered_data2 = df[(df["year"] >= start_date) & (df["year"] <= end_date)]
    filtered_data3 = filtered_data2
    filtered_data2["Matches"] = 1

    choice4 = st.multiselect(
        "Bowling Position:", sorted(filtered_data2["Bowling_Position"].unique())
    )
    if choice4:
        filtered_data2 = filtered_data2[
            filtered_data2["Bowling_Position"].isin(choice4)
        ]

    df_match_totals = (
        filtered_data2.groupby(["Bowler", "BowlType", "Team", "year"])
        .agg(
            Matches=("Matches", "sum"),
            Inn=("I", "sum"),
            Runs=("Runs", "sum"),
            Balls=("Balls", "sum"),
            Wickets=("Wkts", "sum"),
        )
        .reset_index()
    )

    df_match_totals2 = (
        filtered_data3.groupby(["BowlType", "year"])
        .agg(
            Matches=("Matches", "sum"),
            Runs=("Runs", "sum"),
            Balls=("Balls", "sum"),
            Wickets=("Wkts", "sum"),
        )
        .reset_index()
    )

    bowling = pd.merge(
        df_match_totals,
        df_match_totals2,
        on=["BowlType", "year"],
        suffixes=("", "_grouped"),
    )

    bowling["matches_diff"] = bowling["Matches_grouped"] - bowling["Matches"]
    bowling["run_diff"] = bowling["Runs_grouped"] - bowling["Runs"]
    bowling["ball_diff"] = bowling["Balls_grouped"] - bowling["Balls"]
    bowling["wickets_diff"] = bowling["Wickets_grouped"] - bowling["Wickets"]

    # bowling = bowling[bowling['year'].isin(years_of_interest)]
    # bowling = bowling[bowling['Bowler'].isin(['R Ashwin','RA Jadeja'])]
    bowling2 = (
        bowling.groupby(
            [
                "Bowler",
                "BowlType",
                "Team",
            ]
        )
        .agg(
            Matches=("Matches", "sum"),
            Inn=("Inn", "sum"),
            Runs=("Runs", "sum"),
            Balls=("Balls", "sum"),
            Wickets=("Wickets", "sum"),
            matches_diff=("matches_diff", "sum"),
            run_diff=("run_diff", "sum"),
            ball_diff=("ball_diff", "sum"),
            wickets_diff=("wickets_diff", "sum"),
        )
        .reset_index()
    )
    # batting2 = batting2[batting2['New Batter'].isin(batters3000)]
    bowling2["Ave"] = bowling2["Runs"] / bowling2["Wickets"]
    bowling2["Econ"] = bowling2["Runs"] / bowling2["Balls"] * 6
    bowling2["SR"] = bowling2["Balls"] / bowling2["Wickets"]
    # bowling2['BPM'] = bowling2['Balls']/bowling2['Mat']
    bowling2["Mean Ave"] = bowling2["run_diff"] / bowling2["wickets_diff"]
    bowling2["Mean Econ"] = bowling2["run_diff"] / bowling2["ball_diff"] * 6
    bowling2["Mean SR"] = bowling2["ball_diff"] / bowling2["wickets_diff"]

    bowling2["Era Ave Factor"] = bowling2["Mean Ave"] / bowling2["Ave"]
    bowling2["Era Econ Factor"] = bowling2["Mean Econ"] / bowling2["Econ"]
    bowling2["Era SR Factor"] = bowling2["Mean SR"] / bowling2["SR"]

    df_match_totals3["Matches"] = 1
    # # Group by Match_ID and Batter, then calculate the total runs and outs for each player in each match
    df_match_totals3 = (
        df_match_totals3.groupby(["BowlType"])
        .agg(
            PresentMatches=("Matches", "sum"),
            PresentRuns=("Runs", "sum"),
            PresentWickets=("Wkts", "sum"),
            PresentBalls=("Balls", "sum"),
        )
        .reset_index()
    )
    #
    bowling3 = pd.merge(
        bowling2, df_match_totals3, on=["BowlType"], suffixes=("", "_grouped")
    )
    bowling3["PresentAve"] = bowling3["PresentRuns"] / bowling3["PresentWickets"]
    bowling3["PresentSR"] = bowling3["PresentBalls"] / bowling3["PresentWickets"]
    bowling3["PresentEcon"] = bowling3["PresentRuns"] / bowling3["PresentBalls"] * 6
    bowling3["AdjAve"] = bowling3["PresentAve"] / bowling3["Era Ave Factor"]
    bowling3["AdjEcon"] = bowling3["PresentEcon"] / bowling3["Era Econ Factor"]
    bowling3["AdjSR"] = bowling3["PresentSR"] / bowling3["Era SR Factor"]
    bowling3["AdjWPM"] = (bowling3["Balls"] / bowling3["Matches"]) / bowling3["AdjSR"]

    bowling3 = bowling3.drop(
        columns=[
            "matches_diff",
            "run_diff",
            "ball_diff",
            "wickets_diff",
            "Mean Ave",
            "Mean Econ",
            "Mean SR",
            "PresentMatches",
            "PresentRuns",
            "PresentBalls",
            "PresentWickets",
            "PresentAve",
            "PresentSR",
            "PresentEcon",
            "Era Ave Factor",
            "Era SR Factor",
            "Era Econ Factor",
            "AdjWPM",
        ]
    )
    choice4 = st.multiselect("Team:", sorted(bowling3["Team"].unique()))
    if choice4:
        bowling3 = bowling3[bowling3["Team"].isin(choice4)]
    return bowling3


def main():
    st.title("Adjusted ODI Stats")
    choice0 = st.selectbox("Batting Or Bowling:", ["Batting", "Bowling"])
    if choice0 == "Batting":
        filtered_data2 = load_data("entrypointsodi.csv")
        # Create a select box
        filtered_data2["Start_Date"] = pd.to_datetime(
            filtered_data2["Start_Date"], errors="coerce"
        )
        start_date, end_date = st.slider(
            "Select Year:", min_value=1971, max_value=2026, value=(1971, 2026)
        )

        data2 = (
            filtered_data2[
                (filtered_data2["year"] >= start_date)
                & (filtered_data2["year"] <= end_date)
            ]
            .groupby("New Batter")[["Runs"]]
            .sum()
            .reset_index()
        )
        run = max((data2["Runs"]).astype(int))

        # Selectors for user input
        options = [
            "Overall",
        ]

        # Create a select box
        choice2 = st.selectbox(
            "Individual Player or Everyone:", ["Everyone", "Individual"]
        )
        # choice3 = st.multiselect('Home or Away:', ['Home', 'Away'])
        # choice5 = st.multiselect('Team:', data['Team'].unique())
        #    Filtering data based on the user's Date selection

        start_runs, end_runs = st.slider(
            "Select Minimum Runs:", min_value=1, max_value=run, value=(1, run)
        )

        if choice2 == "Individual":
            players = filtered_data2["New Batter"].unique()
            player = st.multiselect("Select Players:", players)
            # name = st.selectbox('Choose the Player From the list', data['striker'].unique())

        results = batadjstats(filtered_data2, start_date, end_date)
        results = results[
            (results["Runs"] >= start_runs) & (results["Runs"] <= end_runs)
        ]

        if choice2 == "Individual":
            temp = []
            for i in player:
                if i in results["New Batter"].unique():
                    temp.append(i)
                else:
                    st.subheader(f"{i} not in this list")
            results = results[results["New Batter"].isin(temp)]
            results = results.rename(columns={"New Batter": "Batsman"})

            st.dataframe(
                results
                # [
                #     [
                #         "Batsman",
                #         "Team",
                #         "Inns",
                #         "Runs",
                #         "Balls",
                #         "Outs",
                #         "Fifties",
                #         "Centuries",
                #         "ave",
                #         "sr",
                #         "Zulu Ave",
                #         "Zulu Sr",
                #     ]
                # ]
                .round(2)
            )
        else:
            results = results.rename(columns={"New Batter": "Batsman"})

            results = results.sort_values(by=["Runs"], ascending=False)
            st.dataframe(
                results
                # [
                #     [
                #         "Batsman",
                #         "Team",
                #         "Inns",
                #         "Runs",
                #         "Balls",
                #         "Outs",
                #         "Fifties",
                #         "Centuries",
                #         "ave",
                #         "sr",
                #         "Zulu Ave",
                #         "Zulu Sr",
                #     ]
                # ]
                .round(2)
            )
    else:
        filtered_data2 = load_data("oditoughwickets.csv")
        # Create a select box
        # filtered_data2["Start Date"] = pd.to_datetime(
        #     filtered_data2["Start Date"], errors="coerce"
        # )
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
        start_date, end_date = st.slider(
            "Select Year:", min_value=1971, max_value=2026, value=(1971, 2026)
        )
        # filtered_data2["year"] = pd.to_datetime(
        #     filtered_data2["Start Date"], format="mixed"
        # ).dt.year
        data2 = (
            filtered_data2[
                (filtered_data2["year"] >= start_date)
                & (filtered_data2["year"] <= end_date)
            ]
            .groupby("Bowler")[["Wkts"]]
            .sum()
            .reset_index()
        )
        wkts = max((data2["Wkts"]).astype(int))
        #
        choice2 = st.multiselect("Pace or Spin:", ["Pace", "Spin"])
        choice3 = st.selectbox(
            "Individual Player or Everyone:", ["Everyone", "Individual"]
        )
        if choice2:
            filtered_data2 = filtered_data2[filtered_data2["BowlType"].isin(choice2)]
        if choice3 == "Individual":
            players = filtered_data2["Bowler"].unique()
            player = st.multiselect("Select Players:", players)
        start_wickets, end_wickets = st.slider(
            "Select Minimum Wickets:", min_value=1, max_value=wkts, value=(1, wkts)
        )

        results = bowladjstats(filtered_data2, start_date, end_date)
        results = results[
            (results["Wickets"] >= start_wickets) & (results["Wickets"] <= end_wickets)
        ]

        if choice3 == "Individual":
            temp = []
            for i in player:
                if i in results["Bowler"].unique():
                    temp.append(i)
                else:
                    st.subheader(f"{i} not in this list")
            results = results[results["Bowler"].isin(temp)]

            st.dataframe(results.round(2))
        else:
            results = results.sort_values(by=["Wickets"], ascending=False)
            st.dataframe(results.round(2))


# Run the main function
if __name__ == "__main__":
    main()
