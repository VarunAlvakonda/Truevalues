import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def main():
    st.set_page_config(page_title="Team Selector", layout="centered")

    players = [
        "KL Rahul", "Yashasvi Jaiswal", "Karun Nair", "Shubman Gill", "Rishabh Pant (wk)",
        "Dhruv Jurel", "Ravindra Jadeja", "Kuldeep Yadav", "Jasprit Bumrah",
        "Mohammed Siraj", "Prasidh Krishna", "Akash Deep", "Nitish Kumar Reddy",
        "Washington Sundar", "Abhimanyu Easwaran", "Shardul Thakur",
        "Harshit Rana", "Arshdeep Singh", "Sai Sudharsan"
    ]

    df = pd.DataFrame({"Player": players})
    df["Order"] = range(1, len(df) + 1)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("Player", rowDrag=True, rowDragEntireRow=True)
    gb.configure_grid_options(rowDragManaged=True, animateRows=True)
    gridOptions = gb.build()

    st.title("🏏 Drag-and-Drop Team Selector")
    st.markdown("Reorder your XI with drag & drop. Top = higher batting order.")

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        height=600
    )

    if grid_response["data"] is not None:
        reordered_df = grid_response["data"].reset_index(drop=True)
        st.subheader("📋 Your Team Order")
        for i, row in reordered_df.iterrows():
            st.write(f"{i+1}. {row['Player']}")

        st.download_button(
            label="📥 Download as CSV",
            data=reordered_df.to_csv(index=False),
            file_name="selected_team.csv",
            mime="text/csv"
        )


# Run the main function
if __name__ == '__main__':
    main()
