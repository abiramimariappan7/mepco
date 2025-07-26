import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl # Added this as it was an optional dependency for pandas with Excel files

st.set_page_config(page_title="Mepcrete AI Tool", layout="wide")

# Load data
@st.cache_data
def load_data():
    # Load each CSV file individually using pd.read_csv
    # Ensure these filenames EXACTLY match the names of the CSV files
    # in the root of your GitHub repository.
    df_emp = pd.read_csv("mepcrete_data_combined.xlsx - Employee Salary Data.csv")
    df_block = pd.read_csv("mepcrete_data_combined.xlsx - AAC Block Measurements.csv")
    df_inv = pd.read_csv("mepcrete_data_combined.xlsx - Inventory Data.csv")
    return df_emp, df_block, df_inv

# Call the data loading function
df_emp, df_block, df_inv = load_data()

# Streamlit App Title
st.title("🏗️ Mepcrete AAC Block AI Tool")

# Navigation Sidebar
section = st.sidebar.radio("Choose Module", ["🏠 Block Estimator", "👷 Employee Salary Prediction", "📊 Inventory Analysis"])

# ---------------- Block Estimator Section ----------------
if section == "🏠 Block Estimator":
    st.header("AAC Block Estimator")
    length = st.number_input("Enter Room Length (ft)", min_value=1.0)
    width = st.number_input("Enter Room Width (ft)", min_value=1.0)
    height = st.number_input("Enter Room Height (ft)", min_value=1.0)

    # Assuming these are block dimensions in mm for volume calculation
    block_sizes = {
        "100mm": 600 * 200 * 100, # LxWxH in mm
        "150mm": 600 * 200 * 150,
        "200mm": 600 * 200 * 200,
        "230mm": 600 * 200 * 230,
        "250mm": 600 * 200 * 250,
        "300mm": 600 * 200 * 300,
    }

    # Map selected size to a common key (assuming your df_block uses these keys)
    selected_block_size_label = st.selectbox(
        "Select Block Thickness (mm)", list(block_sizes.keys())
    )
    block_volume_mm3 = block_sizes[selected_block_size_label]
    block_volume_m3 = block_volume_mm3 / (1000**3) # Convert mm^3 to m^3

    # Calculate room volume in cubic feet
    room_volume_ft3 = length * width * height

    # Convert room volume to cubic meters (1 ft = 0.3048 m)
    room_volume_m3 = room_volume_ft3 * (0.3048**3)

    if st.button("Estimate Blocks"):
        if block_volume_m3 > 0:
            num_blocks = room_volume_m3 / block_volume_m3
            st.success(f"Estimated number of {selected_block_size_label} blocks needed: {int(np.ceil(num_blocks)):,} blocks")
        else:
            st.error("Invalid block size selected.")

# ---------------- Employee Salary Prediction Section ----------------
elif section == "👷 Employee Salary Prediction":
    st.header("Employee Salary Prediction")

    # Dropdowns for categorical features
    job = st.selectbox("Job Title", df_emp["Job Title"].unique())
    dept = st.selectbox("Department", df_emp["Department"].unique())
    loc = st.selectbox("Location", df_emp["Location"].unique())
    emp_type = st.selectbox("Employment Type", df_emp["Employment Type"].unique())
    comp_size = st.selectbox("Company Size", df_emp["Company Size"].unique())
    industry = st.selectbox("Industry", df_emp["Industry"].unique())
    skills = st.selectbox("Skills", df_emp["Skills"].unique())

    # Numeric inputs
    exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=5)
    edu = st.selectbox("Education Level", df_emp["Education Level"].unique())
    hrs = st.slider("Working Hours per Week", 10, 100, 40)

    if st.button("Predict Salary"):
        # Filter for average salary based on selected criteria
        avg_salary = df_emp[
            (df_emp["Job Title"] == job) &
            (df_emp["Department"] == dept) &
            (df_emp["Location"] == loc) &
            (df_emp["Employment Type"] == emp_type) &
            (df_emp["Company Size"] == comp_size) &
            (df_emp["Industry"] == industry) &
            (df_emp["Skills"] == skills) &
            (df_emp["Education Level"] == edu)
        ]["Current Salary"].mean()

        if pd.isna(avg_salary):
            st.error("Not enough data to make a specific prediction based on all selected criteria. Please try broader selections.")
            # Fallback to broader average if specific criteria too narrow
            avg_salary = df_emp["Current Salary"].mean()
            st.info(f"Using overall average salary as a base: ₹{int(avg_salary):,}")
            bonus = (exp * 500) + ((hrs - 40) * 100 if hrs > 40 else 0)
            final_salary = avg_salary + bonus
            st.success(f"Estimated Monthly Salary (based on broader data): ₹{int(final_salary):,}")
        else:
            bonus = (exp * 500) + ((hrs - 40) * 100 if hrs > 40 else 0)
            final_salary = avg_salary + bonus
            st.success(f"Predicted Monthly Salary: ₹{int(final_salary):,}")

# ---------------- Inventory Analysis Section ----------------
elif section == "📊 Inventory Analysis":
    st.header("Inventory & Sales Dashboard")

    # Assuming column names are correct as inferred from your CSV data snippets
    total_produced = df_inv["Blocks Made"].sum()
    total_sold = df_inv["Blocks Sold"].sum()
    total_remaining = df_inv["Blocks Left"].sum() # Use "Blocks Left" as per CSV snippet
    waste = df_inv["Waste (kg)"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏗️ Blocks Made", int(total_produced))
    col2.metric("📦 Blocks Sold", int(total_sold))
    col3.metric("📊 Remaining", int(total_remaining))
    col4.metric("♻️ Waste (kg)", int(waste))

    st.subheader("Daily Inventory Trends")
    # Convert 'Date' column to datetime if not already
    df_inv["Date"] = pd.to_datetime(df_inv["Date"])
    # Set 'Date' as index for plotting
    df_inv_plot = df_inv.set_index("Date")

    st.line_chart(df_inv_plot[["Blocks Made", "Blocks Sold", "Blocks Left"]])

    st.subheader("Waste Analysis")
    st.line_chart(df_inv_plot["Waste (kg)"])

    st.subheader("Raw Data Preview - Inventory")
    st.dataframe(df_inv)
