
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mepcrete AI Tool", layout="wide")

# Load data
@st.cache_data
def load_data():
    df_emp = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="Employee Salary Data")
    df_block = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="Block Estimation")
    df_inv = pd.read_excel("mepcrete_data_combined.xlsx", sheet_name="Inventory Data")
    return df_emp, df_block, df_inv

df_emp, df_block, df_inv = load_data()

st.title("🏗️ Mepcrete AAC Block AI Tool")

# Navigation
section = st.sidebar.radio("Choose Module", ["🏠 Block Estimator", "👷 Employee Salary Prediction", "📊 Inventory Analysis"])

# ---------------- Block Estimator ----------------
if section == "🏠 Block Estimator":
    st.header("AAC Block Estimator")
    length = st.number_input("Enter Room Length (ft)", min_value=1.0)
    width = st.number_input("Enter Room Width (ft)", min_value=1.0)
    height = st.number_input("Enter Room Height (ft)", min_value=1.0)

    block_sizes = {
        "100mm": 600 * 200 * 100,
        "150mm": 600 * 200 * 150,
        "200mm": 600 * 200 * 200,
        "230mm": 600 * 200 * 230
    }

    if st.button("Estimate Blocks"):
        wall_area = 2 * (length + width) * height * 0.092903  # ft² to m²
        st.write(f"Total Wall Area: {wall_area:.2f} m²")

        for size, vol_mm3 in block_sizes.items():
            block_vol_m3 = vol_mm3 / 1e9  # mm³ to m³
            total_blocks = (wall_area * 0.15) / block_vol_m3  # 15 cm thickness
            st.write(f"{size} Blocks Needed: {int(total_blocks)} blocks")

# ---------------- Employee Salary Prediction ----------------
elif section == "👷 Employee Salary Prediction":
    st.header("Employee Salary Prediction")
    job = st.selectbox("Job Title", df_emp["Job Title"].unique())
    dept = st.selectbox("Department", df_emp["Department"].unique())
    exp = st.slider("Years of Experience", 0, 30, 1)
    edu = st.selectbox("Education Level", df_emp["Education Level"].unique())
    hrs = st.slider("Working Hours per Week", 10, 100, 40)

    if st.button("Predict Salary"):
        avg_salary = df_emp[
            (df_emp["Job Title"] == job) &
            (df_emp["Department"] == dept) &
            (df_emp["Education Level"] == edu)
        ]["Current Salary"].mean()

        if pd.isna(avg_salary):
            st.error("Not enough data to predict salary.")
        else:
            bonus = (exp * 500) + ((hrs - 40) * 100 if hrs > 40 else 0)
            final_salary = avg_salary + bonus
            st.success(f"Predicted Monthly Salary: ₹{int(final_salary):,}")

# ---------------- Inventory & Sales Dashboard ----------------
elif section == "📊 Inventory Analysis":
    st.header("Inventory & Sales Dashboard")

    total_produced = df_inv["Total Blocks Made"].sum()
    total_sold = df_inv["Blocks Sold"].sum()
    total_remaining = df_inv["Remaining Blocks"].sum()
    waste = df_inv["Waste (kg)"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏗️ Blocks Made", int(total_produced))
    col2.metric("📦 Blocks Sold", int(total_sold))
    col3.metric("📊 Remaining", int(total_remaining))
    col4.metric("♻️ Waste (kg)", int(waste))

    st.subheader("Blocks Produced vs Sold")
    fig, ax = plt.subplots()
    df_inv.groupby("Date")[["Total Blocks Made", "Blocks Sold"]].sum().plot(kind="bar", ax=ax)
    st.pyplot(fig)

    st.subheader("Waste Analysis")
    st.bar_chart(df_inv.set_index("Date")["Waste (kg)"])
