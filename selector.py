import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, JsCode

st.set_page_config(page_title="Team Selector", layout="centered")

# 🧢 Your full squad
players = [
    "KL Rahul", "Yashasvi Jaiswal", "Karun Nair", "Shubman Gill", "Rishabh Pant (wk)",
    "Dhruv Jurel", "Ravindra Jadeja", "Kuldeep Yadav", "Jasprit Bumrah",
    "Mohammed Siraj", "Prasidh Krishna", "Akash Deep", "Nitish Kumar Reddy",
    "Washington Sundar", "Abhimanyu Easwaran", "Shardul Thakur",
    "Harshit Rana", "Arshdeep Singh", "Sai Sudharsan"
]

# 🗂 Convert to DataFrame with IDs
df = pd.DataFrame({
    "Player": players
})
df["id"] = df.index

# 💡 JavaScript: uniquely identify rows by 'id'
getRowNodeId = JsCode("function getRowNodeId(data) { return data.id; }")

# 🧠 Grid options
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_column("Player", rowDrag=True, rowDragEntireRow=True, header_name="🧢 Drag to reorder")
gb.configure_grid_options(
    rowDragManaged=True,
    animateRows=True,
    getRowNodeId=getRowNodeId,
    deltaRowDataMode=True
)
gridOptions = gb.build()

st.title("🏏 Drag-and-Drop Team Selector")
st.markdown("Drag players up/down to choose your order (e.g., batting lineup)")

# 🧙 AG Grid render
grid_return = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    height=600
)

# 📝 Output: reordered list
if grid_return['data'] is not None:
    reordered_df = grid_return['data'].reset_index(drop=True)
    st.subheader("📋 Your Selected Order")
    for i, row in reordered_df.iterrows():
        st.write(f"{i+1}. {row['Player']}")

    st.download_button(
        label="Download Team as CSV",
        data=reordered_df.to_csv(index=False),
        file_name="selected_team.csv",
        mime="text/csv"
    )