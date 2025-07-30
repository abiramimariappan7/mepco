import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

st.set_page_config(page_title="Mepcrete Data Analyzer", layout="wide")
st.title("🏗️ Mepcrete Data Analyzer Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    st.success("Data successfully loaded!")

    # Department-based Salary Adjustment
    dept_salary_factor = {
        'Engineering': 1.2,
        'Marketing': 0.9,
        'HR': 1.0,
        'Operations': 0.8,
        'Sales': 1.1,
        'Admin': 0.85,
        'Finance': 1.15
    }
    if 'Current Salary' in df.columns and 'Department' in df.columns:
        df['Adjusted Salary'] = df.apply(
            lambda row: row['Current Salary'] * dept_salary_factor.get(row['Department'], 1.0), axis=1
        )

    # Show raw data
    with st.expander("📄 View Raw Data"):
        st.dataframe(df.head(50))

    # Filter by Data Type
    if 'Adjusted Salary' in df.columns and 'Job Title' in df.columns:
        emp_df = df.dropna(subset=["Adjusted Salary", "Job Title"])

        st.subheader("📊 Employee Salary Insights")

        # Average Salary by Job Title
        job_salary_avg = emp_df.groupby("Job Title")["Adjusted Salary"].mean().sort_values(ascending=False).reset_index()
        fig_job = px.bar(job_salary_avg, x="Job Title", y="Adjusted Salary",
                         title="Average Adjusted Salary by Job Title",
                         text_auto='.2s', color="Adjusted Salary",
                         color_continuous_scale="Purples")
        fig_job.update_layout(template="plotly_white")
        st.plotly_chart(fig_job, use_container_width=True)

        # Average Salary by Department
        if 'Department' in df.columns:
            dept_salary_avg = emp_df.groupby("Department")["Adjusted Salary"].mean().sort_values(ascending=False).reset_index()
            fig_dept = px.bar(dept_salary_avg, x="Department", y="Adjusted Salary",
                              title="Average Adjusted Salary by Department",
                              text_auto='.2s', color="Adjusted Salary",
                              color_continuous_scale="Purples")
            fig_dept.update_layout(template="plotly_white")
            st.plotly_chart(fig_dept, use_container_width=True)

    # ML: Salary Prediction
    if 'Adjusted Salary' in df.columns and 'Experience (Years)' in df.columns:
        st.subheader("🤖 Predict Adjusted Salary using Experience")
        ml_df = df.dropna(subset=['Adjusted Salary', 'Experience (Years)'])

        X = ml_df[['Experience (Years)']]
        y = ml_df['Adjusted Salary']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        st.write(f"Model Accuracy (Lower RMSE = Better): {mean_squared_error(y_test, y_pred, squared=False):.2f}")

        exp_input = st.number_input("Enter Years of Experience", min_value=0.0, step=0.5)
        if exp_input:
            predicted_salary = model.predict([[exp_input]])[0]
            st.success(f"Predicted Adjusted Salary: ₹{predicted_salary:,.2f}")

    # Block Estimator Tool
    st.subheader("📐 Block Estimator")
    length = st.number_input("Room Length (ft)", min_value=1.0)
    width = st.number_input("Room Width (ft)", min_value=1.0)
    height = st.number_input("Room Height (ft)", min_value=1.0)

    door_area = 21  # Average door area (ft^2)
    window_area = 12  # Average window area (ft^2)
    num_doors = st.number_input("Number of Doors", min_value=0, step=1)
    num_windows = st.number_input("Number of Windows", min_value=0, step=1)

    block_length = 1.3  # ft
    block_height = 0.67  # ft
    block_thickness = 0.33  # ft (Assuming standard AAC block)
    block_area = block_length * block_height

    if st.button("Estimate Blocks"):
        wall_area = 2 * height * (length + width)
        opening_area = (door_area * num_doors) + (window_area * num_windows)
        net_wall_area = wall_area - opening_area
        blocks_needed = net_wall_area / block_area
        st.info(f"🧱 Estimated Blocks Required: {int(blocks_needed)}")
