import datetime
import functools

import gradio as gr
import numpy as np
import polars as pl

# ── Constants ─────────────────────────────────────────────────────────────────

PARQUET_FILE = "T20DataT20Leagues_optimized.parquet"

# ── Pure computation (unchanged from Streamlit version) ───────────────────────


def cubic_poly(w, a, b, c, d):
    return a * w**3 + b * w**2 + c * w + d


def truemetrics(truevalues):
    truevalues = truevalues.with_columns(
        [
            pl.when(pl.col("Out") == 0)
            .then(pl.col("Runs Scored"))
            .otherwise(pl.col("Runs Scored") / pl.col("Out"))
            .alias("Ave"),
            pl.when(pl.col("BF") == 0)
            .then(pl.lit(0.0))
            .otherwise((pl.col("Runs Scored") / pl.col("BF")) * 100)
            .alias("SR"),
            pl.when(pl.col("Expected Outs") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Expected Runs") / pl.col("Expected Outs"))
            .alias("Expected Ave"),
            pl.when(pl.col("BF") == 0)
            .then(pl.lit(0.0))
            .otherwise((pl.col("Expected Runs") / pl.col("BF")) * 100)
            .alias("Expected SR"),
        ]
    )
    truevalues = truevalues.with_columns(
        [
            (pl.col("Ave") - pl.col("Expected Ave")).alias("True Ave"),
            (pl.col("SR") - pl.col("Expected SR")).alias("True SR"),
            pl.when(pl.col("Out") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Expected Outs") / pl.col("Out"))
            .alias("Out Ratio"),
        ]
    )
    return truevalues


def truemetricsbowling(truevalues):
    truevalues = truevalues.with_columns(
        [
            pl.when(pl.col("BF") == 0)
            .then(pl.lit(0.0))
            .otherwise((pl.col("RC") / pl.col("BF")) * 6)
            .alias("Econ"),
            pl.when(pl.col("Out") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("BF") / pl.col("Out"))
            .alias("SR"),
            pl.when(pl.col("BF") == 0)
            .then(pl.lit(0.0))
            .otherwise((pl.col("Expected Runs") / pl.col("BF")) * 6)
            .alias("Expected Econ"),
            pl.when(pl.col("Expected Outs") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("BF") / pl.col("Expected Outs"))
            .alias("Expected SR"),
        ]
    )
    truevalues = truevalues.with_columns(
        [
            (pl.col("Expected Econ") - pl.col("Econ")).alias("True Econ"),
            pl.when(pl.col("BF") == 0)
            .then(pl.lit(0.0))
            .otherwise((pl.col("Out") - pl.col("Expected Outs")) / (pl.col("BF") / 24))
            .alias("True Wickets"),
        ]
    )
    return truevalues


@functools.lru_cache(maxsize=4)
def load_data(filename: str) -> pl.DataFrame:
    return pl.read_parquet(filename)


def analyze_data_for_year3(year, player_data, baseline_data, place):
    combineddata = player_data.filter(
        (pl.col("TeamInns") < 3) & (pl.col("year") == year)
    )
    baseline = baseline_data.filter((pl.col("TeamInns") < 3) & (pl.col("year") == year))

    inns = (
        combineddata.group_by(["Batsman", "Batter", "MatchNum"])
        .agg(pl.col("Runs").sum())
        .with_columns(pl.lit(1).alias("I"))
    )
    inns2 = (
        inns.group_by(["Batsman", "Batter"])
        .agg(pl.col("I").sum())
        .select([pl.col("Batsman"), pl.col("Batter").alias("Player"), pl.col("I")])
    )

    valid = ["X", "WX"]
    dismissed_data = combineddata.filter(pl.col("Notes").is_in(valid)).with_columns(
        pl.lit(1).alias("Out")
    )
    merge_cols = ["MatchNum", "TeamInns", "Batsman", "Batter", "Notes", "over"]
    combineddata = combineddata.join(
        dismissed_data.select(merge_cols + ["Out"]), on=merge_cols, how="left"
    ).with_columns(pl.col("Out").fill_null(0))

    groupby_player = ["Batsman", "Batter", "TeamInns", place, "over"]
    player_outs = (
        dismissed_data.group_by(groupby_player)
        .agg(pl.col("Out").sum())
        .select(
            [
                pl.col("Batsman"),
                pl.col("Batter").alias("Player"),
                pl.col("TeamInns"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("Out"),
            ]
        )
    )
    player_runs = (
        combineddata.group_by(groupby_player)
        .agg(
            [
                pl.col("Runs").sum().alias("Runs Scored"),
                pl.col("B").sum().alias("BF"),
                pl.col("Impact").sum(),
            ]
        )
        .select(
            [
                pl.col("Batsman"),
                pl.col("Batter").alias("Player"),
                pl.col("TeamInns"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("Runs Scored"),
                pl.col("BF"),
                pl.col("Impact"),
            ]
        )
    )

    groupby_over = ["TeamInns", place, "over"]
    baseline_dismissed = baseline.filter(pl.col("Notes").is_in(valid)).with_columns(
        pl.lit(1).alias("Out")
    )
    over_outs = (
        baseline_dismissed.group_by(groupby_over)
        .agg(pl.col("Out").sum().alias("Outs"))
        .select(
            [
                pl.col("TeamInns"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("Outs"),
            ]
        )
    )
    over_runs = (
        baseline.group_by(groupby_over)
        .agg([pl.col("Runs").sum(), pl.col("B").sum()])
        .select(
            [
                pl.col("TeamInns"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("Runs"),
                pl.col("B"),
            ]
        )
    )

    combined_df = player_runs.join(
        player_outs, on=["Batsman", "Player", "TeamInns", place, "Over"], how="left"
    )
    combined_df2 = over_runs.join(over_outs, on=["TeamInns", place, "Over"], how="left")
    combined_df3 = combined_df.join(
        combined_df2, on=["TeamInns", place, "Over"], how="left"
    )
    combined_df3 = combined_df3.with_columns(
        [pl.col("Outs").fill_null(0), pl.col("Out").fill_null(0)]
    )
    combined_df3 = combined_df3.with_columns(
        [
            (pl.col("Runs") - pl.col("Runs Scored")).alias("Over_Runs"),
            (pl.col("B") - pl.col("BF")).alias("Over_B"),
            (pl.col("Outs") - pl.col("Out")).alias("Over_Outs"),
        ]
    )
    combined_df3 = combined_df3.with_columns(
        [
            pl.when(pl.col("Over_B") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Over_Runs") / pl.col("Over_B"))
            .alias("BSR"),
            pl.when(pl.col("Over_B") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Over_Outs") / pl.col("Over_B"))
            .alias("OPB"),
        ]
    )
    combined_df3 = combined_df3.with_columns(
        [
            (pl.col("BF") * pl.col("BSR")).alias("Expected Runs"),
            (pl.col("BF") * pl.col("OPB")).alias("Expected Outs"),
        ]
    )

    agg_cols = ["Runs Scored", "BF", "Out", "Expected Runs", "Expected Outs", "Impact"]
    truevalues = combined_df3.group_by(["Player", "Batsman"]).agg(
        [pl.col(c).sum() for c in agg_cols]
    )
    final_results = truemetrics(truevalues)

    players_years = (
        combineddata.select(["Batsman", "Batter", "year"])
        .unique()
        .select(
            [
                pl.col("Batsman"),
                pl.col("Batter").alias("Player"),
                pl.col("year").alias("Year"),
            ]
        )
    )
    final_results2 = inns2.join(final_results, on=["Batsman", "Player"], how="left")
    final_results3 = players_years.join(
        final_results2, on=["Batsman", "Player"], how="left"
    )
    float_cols = final_results3.select(pl.col(pl.Float64)).columns
    return final_results3.with_columns([pl.col(c).round(2) for c in float_cols])


def analyze_data_for_year6(year, player_data, baseline_data, place):
    combineddata = player_data.filter(
        (pl.col("TeamInns") < 3) & (pl.col("year") == year)
    )
    baseline = baseline_data.filter((pl.col("TeamInns") < 3) & (pl.col("year") == year))

    inns = (
        combineddata.group_by(["Bowlers", "Bowler", "MatchNum"])
        .agg(pl.col("Runs").sum())
        .with_columns(pl.lit(1).alias("I"))
    )
    inns2 = (
        inns.group_by(["Bowlers", "Bowler"])
        .agg(pl.col("I").sum())
        .select(
            [
                pl.col("Bowlers").alias("Player"),
                pl.col("Bowler").alias("BowlNum"),
                pl.col("I"),
            ]
        )
    )

    valid = ["X", "XC", "XT", "XU", "XSUTC", "NX", "LX", "NXT", "XZ", "XP", "PX", "WX"]
    dismissed_data = combineddata.filter(
        pl.col("Notes").is_in(valid)
        & (pl.col("BowlDis") == "Y")
        & (pl.col("LongDis") != "run out")
    ).with_columns(pl.lit(1).alias("Out"))
    merge_cols = ["MatchNum", "TeamInns", place, "Bowlers", "Bowler", "Notes", "over"]
    combineddata = (
        combineddata.join(
            dismissed_data.select(merge_cols + ["Out"]), on=merge_cols, how="left"
        )
        .with_columns(pl.col("Out").fill_null(0))
        .unique()
    )

    player_outs = (
        dismissed_data.group_by(["Bowlers", "Bowler", place, "over"])
        .agg(pl.col("Out").sum())
        .select(
            [
                pl.col("Bowlers").alias("Player"),
                pl.col("Bowler").alias("BowlNum"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("Out"),
            ]
        )
    )
    player_runs = (
        combineddata.group_by(["Bowlers", "Bowler", place, "over"])
        .agg(
            [pl.col("RC").sum(), pl.col("B").sum().alias("BF"), pl.col("Impact").sum()]
        )
        .select(
            [
                pl.col("Bowlers").alias("Player"),
                pl.col("Bowler").alias("BowlNum"),
                pl.col(place),
                pl.col("over").alias("Over"),
                pl.col("RC"),
                pl.col("BF"),
                pl.col("Impact"),
            ]
        )
    )

    baseline_dismissed = baseline.filter(
        pl.col("Notes").is_in(valid)
        & (pl.col("BowlDis") == "Y")
        & (pl.col("LongDis") != "run out")
    ).with_columns(pl.lit(1).alias("Out"))
    over_outs = (
        baseline_dismissed.group_by([place, "over"])
        .agg(pl.col("Out").sum().alias("Outs"))
        .select([pl.col(place), pl.col("over").alias("Over"), pl.col("Outs")])
    )
    over_runs = (
        baseline.group_by([place, "over"])
        .agg([pl.col("RC").sum().alias("Runs"), pl.col("B").sum()])
        .select(
            [pl.col(place), pl.col("over").alias("Over"), pl.col("Runs"), pl.col("B")]
        )
    )

    combined_df = player_runs.join(
        player_outs, on=["Player", "BowlNum", place, "Over"], how="left"
    )
    combined_df2 = over_runs.join(over_outs, on=[place, "Over"], how="left")
    combined_df3 = combined_df.join(combined_df2, on=[place, "Over"], how="left")
    combined_df3 = combined_df3.with_columns(
        [pl.col("Outs").fill_null(0), pl.col("Out").fill_null(0)]
    )
    combined_df3 = combined_df3.with_columns(
        [
            (pl.col("Runs") - pl.col("RC")).alias("Over_Runs"),
            (pl.col("B") - pl.col("BF")).alias("Over_B"),
            (pl.col("Outs") - pl.col("Out")).alias("Over_Outs"),
        ]
    )
    combined_df3 = combined_df3.with_columns(
        [
            pl.when(pl.col("Over_B") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Over_Runs") / pl.col("Over_B"))
            .alias("BSR"),
            pl.when(pl.col("Over_B") == 0)
            .then(pl.lit(0.0))
            .otherwise(pl.col("Over_Outs") / pl.col("Over_B"))
            .alias("OPB"),
        ]
    )
    combined_df3 = combined_df3.with_columns(
        [
            (pl.col("BF") * pl.col("BSR")).alias("Expected Runs"),
            (pl.col("BF") * pl.col("OPB")).alias("Expected Outs"),
        ]
    )

    agg_cols = ["RC", "BF", "Out", "Expected Runs", "Expected Outs", "Impact"]
    truevalues = combined_df3.group_by(["Player", "BowlNum"]).agg(
        [pl.col(c).sum() for c in agg_cols]
    )
    final_results = truemetricsbowling(truevalues)

    players_years = (
        combineddata.select(["Bowlers", "Bowler", "BowlCat", "year"])
        .unique()
        .select(
            [
                pl.col("Bowlers").alias("Player"),
                pl.col("Bowler").alias("BowlNum"),
                pl.col("BowlCat").alias("Type"),
                pl.col("year").alias("Year"),
            ]
        )
    )
    final_results2 = inns2.join(final_results, on=["Player", "BowlNum"], how="left")
    final_results3 = players_years.join(
        final_results2, on=["Player", "BowlNum"], how="left"
    )
    float_cols = final_results3.select(pl.col(pl.Float64)).columns
    return final_results3.with_columns([pl.col(c).round(2) for c in float_cols])


# ── UI helpers ────────────────────────────────────────────────────────────────


def get_competitions():
    data = load_data(PARQUET_FILE)
    return sorted(data["CompName"].drop_nulls().unique(maintain_order=False).to_list())


def get_date_bounds():
    data = load_data(PARQUET_FILE)
    dates = data["Date"].drop_nulls()
    return dates.min().date(), dates.max().date()


def update_players(selected_leagues, choice0, start_date_str, end_date_str):
    """Refresh player dropdown when context changes."""
    try:
        data = load_data(PARQUET_FILE)
        if selected_leagues:
            data = data.filter(pl.col("CompName").is_in(selected_leagues))
        sd = datetime.date.fromisoformat(start_date_str)
        ed = datetime.date.fromisoformat(end_date_str)
        start_dt = datetime.datetime.combine(sd, datetime.time.min)
        end_dt = datetime.datetime.combine(ed, datetime.time.max)
        data = data.filter((pl.col("Date") >= start_dt) & (pl.col("Date") <= end_dt))
        col = "Batter" if choice0 == "Batting" else "Bowlers"
        players = sorted(data[col].drop_nulls().unique(maintain_order=False).to_list())
        return gr.Dropdown(choices=players, value=[])
    except Exception:
        return gr.Dropdown(choices=[], value=[])


# ── Main analysis function ─────────────────────────────────────────────────────


def run_analysis(
    selected_leagues,
    choice0,
    view,
    scope,
    start_date_str,
    end_date_str,
    selected_players,
    bowl_type,
    innings,
    min_bf_inn,
    max_bf_inn,
    bat_positions,
    start_over,
    end_over,
    min_primary,
    max_primary,
    min_bf,
    max_bf,
):
    try:
        data = load_data(PARQUET_FILE)

        # Determine venue grouping column
        if selected_leagues and "Twenty20 International" not in selected_leagues:
            place = "Venue_x"
        else:
            place = "Country"

        if selected_leagues:
            data = data.filter(pl.col("CompName").is_in(selected_leagues))

        # Date filter
        sd = datetime.date.fromisoformat(start_date_str)
        ed = datetime.date.fromisoformat(end_date_str)
        if sd > ed:
            return None, "❌ End date must be after start date."
        start_dt = datetime.datetime.combine(sd, datetime.time.min)
        end_dt = datetime.datetime.combine(ed, datetime.time.max)
        data = data.filter((pl.col("Date") >= start_dt) & (pl.col("Date") <= end_dt))

        # Overs filter → this becomes the baseline (unaffected by pace/spin/innings)
        baseline_data = data.filter(
            (pl.col("over") >= start_over) & (pl.col("over") <= end_over)
        )

        # Player-specific filters on top of baseline
        player_data = baseline_data
        if bowl_type:
            player_data = player_data.filter(pl.col("BowlCat").is_in(bowl_type))
        if innings:
            player_data = player_data.filter(
                pl.col("TeamInns").is_in([int(i) for i in innings])
            )
        if choice0 == "Batting":
            player_data = player_data.filter(
                (pl.col("BatterBalls") >= int(min_bf_inn))
                & (pl.col("BatterBalls") <= int(max_bf_inn))
            )
            if bat_positions:
                player_data = player_data.filter(
                    pl.col("BatPos").is_in([int(p) for p in bat_positions])
                )

        unique_years = sorted(player_data["year"].drop_nulls().unique().to_list())
        if not unique_years:
            return None, "❌ No data matches the current filters."

        # Run per-year analysis
        all_data = []
        for year in unique_years:
            if choice0 == "Batting":
                result = analyze_data_for_year3(year, player_data, baseline_data, place)
            else:
                result = analyze_data_for_year6(year, player_data, baseline_data, place)
            all_data.append(result)

        combined_data = pl.concat(all_data)

        # Aggregate across years for Overall Stats
        if choice0 == "Batting":
            agg_cols = [
                "I",
                "Runs Scored",
                "BF",
                "Out",
                "Expected Runs",
                "Expected Outs",
                "Impact",
            ]
            final_results = truemetrics(
                combined_data.group_by(["Player", "Batsman"]).agg(
                    [pl.col(c).sum() for c in agg_cols]
                )
            ).sort("Runs Scored", descending=True)
        else:
            agg_cols = [
                "I",
                "RC",
                "BF",
                "Out",
                "Expected Runs",
                "Expected Outs",
                "Impact",
            ]
            final_results = truemetricsbowling(
                combined_data.group_by(["Player", "BowlNum", "Type"]).agg(
                    [pl.col(c).sum() for c in agg_cols]
                )
            ).sort("Out", descending=True)

        # Select the right dataset for the chosen view
        df = final_results if view == "Overall Stats" else combined_data

        # Individual player filter
        if scope == "Individual" and selected_players:
            df = df.filter(pl.col("Player").is_in(selected_players))

        # Drop internal columns and apply result-level filters
        if choice0 == "Batting":
            drop = [
                "Expected Runs",
                "Expected Outs",
                "Out Ratio",
                "Expected Ave",
                "Expected SR",
            ]
            df = (
                df.drop([c for c in drop if c in df.columns])
                .filter(
                    (pl.col("Runs Scored") >= int(min_primary))
                    & (pl.col("Runs Scored") <= int(max_primary))
                    & (pl.col("BF") >= int(min_bf))
                    & (pl.col("BF") <= int(max_bf))
                )
                .with_columns((pl.col("Impact") / pl.col("I")).alias("Impact/Inns"))
                .drop("Impact")
            )
            if view == "Season By Season":
                df = df.sort("Year", descending=True)
        else:
            drop = ["Expected Runs", "Expected Outs", "Expected Econ", "Expected SR"]
            df = (
                df.drop([c for c in drop if c in df.columns])
                .filter(
                    (pl.col("Out") >= int(min_primary))
                    & (pl.col("Out") <= int(max_primary))
                    & (pl.col("BF") >= int(min_bf))
                    & (pl.col("BF") <= int(max_bf))
                )
                .with_columns((pl.col("Impact") / pl.col("I")).alias("Impact/Inns"))
                .drop("Impact")
            )
            if view == "Season By Season":
                df = df.sort("Year", descending=True)

        # Final rounding
        float_cols = df.select(pl.col(pl.Float64)).columns
        df = df.with_columns([pl.col(c).round(2) for c in float_cols])

        return df.to_pandas(), f"✓ {len(df)} rows"

    except Exception as e:
        return None, f"❌ Error: {e}"


# ── Gradio layout ─────────────────────────────────────────────────────────────

min_date, max_date = get_date_bounds()

with gr.Blocks(title="True Values", theme=gr.themes.Soft()) as app:
    gr.Markdown("# True Values")

    with gr.Row():
        # ── Left panel: filters ──────────────────────────────────────────────
        with gr.Column(scale=1, min_width=280):
            gr.Markdown("### Filters")

            selected_leagues = gr.Dropdown(
                choices=get_competitions(),
                multiselect=True,
                label="Competitions",
            )
            choice0 = gr.Radio(
                ["Batting", "Bowling"], value="Batting", label="Batting or Bowling"
            )
            view = gr.Radio(
                ["Overall Stats", "Season By Season"],
                value="Overall Stats",
                label="View",
            )
            scope = gr.Radio(
                ["Everyone", "Individual"], value="Everyone", label="Scope"
            )

            with gr.Row():
                start_date = gr.Textbox(
                    label="Start date (YYYY-MM-DD)", value=str(min_date)
                )
                end_date = gr.Textbox(
                    label="End date (YYYY-MM-DD)", value=str(max_date)
                )

            selected_players = gr.Dropdown(
                choices=[],
                multiselect=True,
                label="Players (Individual mode only)",
            )

            bowl_type = gr.CheckboxGroup(["Pace", "Spin"], label="Pace / Spin")
            innings = gr.CheckboxGroup(["1", "2"], label="Innings")

            with gr.Accordion("Batting-only filters", open=False):
                with gr.Row():
                    min_bf_inn = gr.Number(
                        value=0, label="Min balls (inns)", precision=0
                    )
                    max_bf_inn = gr.Number(
                        value=500, label="Max balls (inns)", precision=0
                    )
                bat_positions = gr.CheckboxGroup(
                    [str(i) for i in range(1, 13)], label="Batting positions"
                )

            with gr.Row():
                start_over = gr.Slider(1, 20, value=1, step=1, label="From over")
                end_over = gr.Slider(1, 20, value=20, step=1, label="To over")

            gr.Markdown("### Result filters")
            with gr.Row():
                min_primary = gr.Number(
                    value=0, label="Min runs / wickets", precision=0
                )
                max_primary = gr.Number(
                    value=99999, label="Max runs / wickets", precision=0
                )
            with gr.Row():
                min_bf = gr.Number(value=0, label="Min BF (career)", precision=0)
                max_bf = gr.Number(value=99999, label="Max BF (career)", precision=0)

            run_btn = gr.Button("Run Analysis", variant="primary")

        # ── Right panel: output ──────────────────────────────────────────────
        with gr.Column(scale=3):
            status = gr.Textbox(label="Status", interactive=False, max_lines=1)
            output_table = gr.Dataframe(
                label="Results",
                interactive=False,
                wrap=False,
            )

    # ── Dynamic player list ───────────────────────────────────────────────────
    for trigger in [selected_leagues, choice0, start_date, end_date]:
        trigger.change(
            update_players,
            inputs=[selected_leagues, choice0, start_date, end_date],
            outputs=[selected_players],
        )

    # ── Run button ────────────────────────────────────────────────────────────
    run_btn.click(
        run_analysis,
        inputs=[
            selected_leagues,
            choice0,
            view,
            scope,
            start_date,
            end_date,
            selected_players,
            bowl_type,
            innings,
            min_bf_inn,
            max_bf_inn,
            bat_positions,
            start_over,
            end_over,
            min_primary,
            max_primary,
            min_bf,
            max_bf,
        ],
        outputs=[output_table, status],
    )


if __name__ == "__main__":
    app.launch()
