# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Title
st.set_page_config(page_title="Smart Construction Insights", layout="wide")
st.title("🏗️ Smart Construction Analytics and Block Estimator")

# Load Excel File
@st.cache_data

def load_data():
    df_salary = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="Employee Salary Data")
    df_blocks = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="AAC Block Measurements")
    df_inventory = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="Inventory Data")
    return df_salary, df_blocks, df_inventory

df_salary, df_blocks, df_inventory = load_data()

# Tabs
st.sidebar.title("Navigation")
tabs = ["📊 Employee Insights", "📐 Block Estimator", "📦 Inventory Analysis", "🤖 Salary Prediction"]
selected_tab = st.sidebar.radio("Go to", tabs)

# --- EMPLOYEE INSIGHTS ---
if selected_tab == tabs[0]:
    st.header("📊 Employee Salary Insights")
    st.write("### Salary Distribution by Job Title")
    fig1 = px.box(df_salary, x="Job Title", y="Current Salary", color="Job Title")
    st.plotly_chart(fig1, use_container_width=True)

    st.write("### Workload vs Salary")
    fig2 = px.scatter(df_salary, x="Workload (Hours/Week)", y="Current Salary",
                      color="Department", hover_data=['Job Title'])
    st.plotly_chart(fig2, use_container_width=True)

# --- BLOCK ESTIMATOR ---
elif selected_tab == tabs[1]:
    st.header("📐 Block Estimator Based on Room Dimensions")

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
        door_area = num_doors * 1.8
        window_area = num_windows * 1.44
        wall_thickness = 0.1
        total_wall_volume = (wall_area - (door_area + window_area)) * wall_thickness
        blocks_needed = total_wall_volume / block_volume
        st.success(f"🧱 Blocks Required: {int(blocks_needed)}")
        st.caption(f"Wall Volume: {total_wall_volume:.2f} m³ | Block Volume: {block_volume:.3f} m³")

# --- INVENTORY DATA ---
elif selected_tab == tabs[2]:
    st.header("📦 Inventory Production & Wastage Insights")
    df_inventory['Date'] = pd.to_datetime(df_inventory['Date'])
    df_sample = df_inventory.head(50)

    fig = px.line(df_sample, x="Date", y=["Blocks Made", "Blocks Sold", "Waste (kg)"],
                  title="Inventory Movement Over Time")
    st.plotly_chart(fig, use_container_width=True)

    total_waste = df_inventory['Waste (kg)'].sum()
    total_made = df_inventory['Blocks Made'].sum()
    waste_percentage = (total_waste / (total_made * 15)) * 100  # assume 1 block = 15kg

    st.metric("Total Waste (kg)", f"{int(total_waste)}")
    st.metric("Estimated Waste %", f"{waste_percentage:.2f}%")

# --- SALARY PREDICTION MODEL ---
elif selected_tab == tabs[3]:
    st.header("🤖 Predict Salary using Experience")

    df_salary['Experience'] = df_salary['Years of Experience']
    X = df_salary[['Experience']]
    y = df_salary['Current Salary']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    model = LinearRegression()
    model.fit(X_train, y_train)

    user_exp = st.number_input("Enter Years of Experience", min_value=0.0, step=0.5)
    if st.button("Predict Salary"):
        predicted_salary = model.predict([[user_exp]])[0]
        st.success(f"💰 Estimated Salary: ₹{int(predicted_salary)}")
