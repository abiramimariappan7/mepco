import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="MepcreteBlock: Smart Construction Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    excel_path = "mepcrete_data_combined.xlsx"
    df_salary = pd.read_excel(excel_path, sheet_name='Employee Salary Data')
    df_blocks = pd.read_excel(excel_path, sheet_name='AAC Block Measurements')
    df_inventory = pd.read_excel(excel_path, sheet_name='Inventory Data')
    return df_salary, df_blocks, df_inventory

df_salary, df_blocks, df_inventory = load_data()

# App title
st.title("🏗️ MepcreteBlock: Smart Estimator & Inventory Dashboard")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Inventory Analysis", "🧱 Block Estimator", "💼 Salary Insights"])

# ------------------ TAB 1: INVENTORY ------------------
with tab1:
    st.subheader("Inventory Data Overview")
    df_inventory['Date'] = pd.to_datetime(df_inventory['Date'])
    df_inventory.sort_values("Date", inplace=True)
    df_inventory_display = df_inventory.copy()

    # Date filter
    min_date, max_date = df_inventory['Date'].min(), df_inventory['Date'].max()
    date_range = st.date_input("Select Date Range", [min_date, max_date])

    if len(date_range) == 2:
        df_inventory_display = df_inventory[
            (df_inventory['Date'] >= pd.to_datetime(date_range[0])) &
            (df_inventory['Date'] <= pd.to_datetime(date_range[1]))
        ]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📦 Blocks Made", int(df_inventory_display['Blocks Made'].sum()))
    with col2:
        st.metric("📤 Blocks Sold", int(df_inventory_display['Blocks Sold'].sum()))
    with col3:
        st.metric("♻️ Waste (kg)", int(df_inventory_display['Waste (kg)'].sum()))

    st.markdown("### 📈 Blocks Made vs Sold")
    fig1 = px.line(df_inventory_display, x='Date', y=['Blocks Made', 'Blocks Sold'],
                   markers=True, title="Blocks Made vs Sold Over Time")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("### 🧯 Waste Over Time")
    fig2 = px.bar(df_inventory_display, x='Date', y='Waste (kg)', color='Waste (kg)',
                  title="Block Waste (kg)", color_continuous_scale='reds')
    st.plotly_chart(fig2, use_container_width=True)

# ------------------ TAB 2: BLOCK ESTIMATOR ------------------
with tab2:
    st.subheader("🏠 Block Estimator Based on Room Dimensions")

    block_volume = df_blocks['Volume (m3)'].mean()

    st.markdown("### 🔹 Enter Room Dimensions (in meters)")
    length = st.number_input("Room Length (m)", min_value=1.0, step=0.5)
    width = st.number_input("Room Width (m)", min_value=1.0, step=0.5)
    height = st.number_input("Wall Height (m)", min_value=1.0, step=0.5)

    st.markdown("### 🔹 Enter Openings")
    num_doors = st.number_input("Number of Doors", min_value=0, step=1)
    num_windows = st.number_input("Number of Windows", min_value=0, step=1)

    if st.button("Estimate Blocks Needed"):
        wall_area = 2 * (length + width) * height
        door_area = num_doors * 1.8  # standard door area
        window_area = num_windows * 1.44  # standard window area
        total_opening_area = door_area + window_area

        wall_thickness = 0.1  # 10 cm thick
        total_wall_volume = (wall_area - total_opening_area) * wall_thickness
        blocks_required = total_wall_volume / block_volume

        st.success(f"🧱 Estimated Blocks Required: **{int(blocks_required)}**")
        st.caption(f"(Wall Volume: {total_wall_volume:.2f} m³, Block Volume: {block_volume:.3f} m³)")

    st.markdown("##### 📏 Sample Block Measurements")
    st.dataframe(df_blocks.head(), use_container_width=True)

# ------------------ TAB 3: SALARY ------------------
with tab3:
    st.subheader("💼 Employee Salary Insights")

    st.markdown("#### 📋 Data Preview")
    st.dataframe(df_salary.head(), use_container_width=True)

    st.markdown("#### 📊 Salary Distribution by Job Title")
    fig_box = px.box(df_salary, x='Job Title', y='Current Salary', points='all',
                     title="Salary Distribution per Job Title")
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("#### 📊 Average Salary by Department")
    if 'Department' in df_salary.columns:
        avg_salary_dept = df_salary.groupby('Department')['Current Salary'].mean().reset_index()
        fig_bar = px.bar(avg_salary_dept, x='Department', y='Current Salary',
                         title="Average Salary by Department", color='Current Salary')
        st.plotly_chart(fig_bar, use_container_width=True)

    avg_salary = int(df_salary['Current Salary'].mean())
    st.metric("💰 Average Salary", f"₹{avg_salary}")

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("📌 Developed by **Abirami Mariappan** | 🎓 B.Tech IT | Internship @ Mepcrete AAC")
