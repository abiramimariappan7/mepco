import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl # Ensure this is in your requirements.txt

st.set_page_config(page_title="Mepcrete AI Tool", layout="wide")

# Load data
@st.cache_data
def load_data():
    # Load each CSV file individually
    df_emp = pd.read_csv("mepcrete_data_combined.xlsx - Employee Salary Data.csv")
    df_block = pd.read_csv("mepcrete_data_combined.xlsx - AAC Block Measurements.csv")
    df_inv = pd.read_csv("mepcrete_data_combined.xlsx - Inventory Data.csv")
    return df_emp, df_block, df_inv

df_emp, df_block, df_inv = load_data()

# The rest of your app.py code follows...
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
        "150mm": 600 * 200 * 150
        # ... rest of your block_sizes
    }
    # ... rest of your app.py logic
