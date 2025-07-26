import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Mepcrete Dashboard", layout="wide")

# Title
st.title("🏗️ Mepcrete Block & Salary Dashboard")

# Load data
@st.cache_data
def load_data():
    excel_path = "mepcrete_data_combined.xlsx"
    df_salary = pd.read_excel(excel_path, sheet_name='Employee Salary Data')
    df_blocks = pd.read_excel(excel_path, sheet_name='AAC Block Measurements')
    df_inventory = pd.read_excel(excel_path, sheet_name='Inventory Data')
    return df_salary, df_blocks, df_inventory

df_salary, df_blocks, df_inventory = load_data()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Inventory Analysis", "🧱 Block Calculator", "💼 Salary Insights"])

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

# ------------------ TAB 2: BLOCK CALCULATOR ------------------
with tab2:
    st.subheader("🧮 Block Usage Calculator")

    # Get average block volume
    avg_volume = df_blocks['Volume (m3)'].mean()

    user_input_volume = st.number_input("Enter total construction volume (m³)", min_value=0.0, step=0.1)

    if user_input_volume > 0:
        blocks_needed = int(user_input_volume / avg_volume)
        st.success(f"🔢 Approx. **{blocks_needed} blocks** are needed for {user_input_volume} m³")

    st.markdown("##### Block Measurement Samples")
    st.dataframe(df_blocks.head(), use_container_width=True)

# ------------------ TAB 3: SALARY ------------------
with tab3:
    st.subheader("💼 Employee Salary Data")

    st.markdown("#### 📋 Raw Data")
    st.dataframe(df_salary.head(), use_container_width=True)

    st.markdown("#### 📊 Salary vs Experience")
    fig3 = px.scatter(df_salary, x='Years of Experience', y='Current Salary',
                      size='Workload (Hours/Week)', color='Job Title',
                      title="Salary vs Experience", hover_name='Job Title')
    st.plotly_chart(fig3, use_container_width=True)

    avg_salary = int(df_salary['Current Salary'].mean())
    st.metric("💰 Average Salary", f"₹{avg_salary}")

# Footer
st.markdown("---")
st.markdown("Built by Abirami Mariappan | Mepcrete AAC Dashboard 🌟")
