import streamlit as st
import numpy as np
import pandas as pd
import requests
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


st.set_page_config(layout="wide")


# ======================================================
# DATA SOURCE SELECTION
# ======================================================
st.sidebar.title("🔌 Data Source")

data_source = st.sidebar.radio(
    "Select Data Source",
    ["Simulated Building Data", "External Building API"]
)


def fetch_external_data(api_url, api_key):
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(api_url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            return df
        else:
            st.error("API connection failed.")
            return None
    except Exception:
        st.error("Error connecting to building system.")
        return None


# ======================================================
# LOAD DATA BASED ON SOURCE
# ======================================================
if data_source == "Simulated Building Data":

    @st.cache_resource
    def load_and_train():
        df = generate_data()
        model = train_model(df)
        return df, model

    base_df, model = load_and_train()
    st.sidebar.success("Using simulated building data.")

else:

    st.sidebar.markdown("### API Configuration")

    api_url = st.sidebar.text_input("Building API URL")
    api_key = st.sidebar.text_input("API Key", type="password")

    if api_url and api_key:
        base_df = fetch_external_data(api_url, api_key)

        if base_df is not None:
            st.sidebar.success("Connected to Building Management System")
            model = train_model(base_df)
        else:
            st.stop()
    else:
        st.sidebar.warning("Enter API credentials to connect.")
        st.stop()


# Run prediction
base_df["prediction"] = predict_energy(model, base_df)


# ======================================================
# SIDEBAR NAVIGATION
# ======================================================
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select View",
    [
        "Executive Overview",
        "Optimization",
        "Climate",
        "Usage Analyzer",
        "Technical Dashboard"
    ]
)

role = st.sidebar.selectbox(
    "User Role",
    ["Executive", "Facility Manager", "Sustainability Officer"]
)

st.sidebar.markdown("---")

occupancy_increase = st.sidebar.slider("Occupancy Increase (%)", 0, 150, 0)
extra_hours = st.sidebar.slider("Extend Working Hours", 0, 12, 0)
hvac_adjustment = st.sidebar.slider("HVAC Adjustment (%)", -40, 60, 0)


# ======================================================
# SCENARIO SIMULATION
# ======================================================
df = base_df.copy()

df["occupancy"] *= (1 + occupancy_increase / 100)

if extra_hours > 0:
    extended_mask = df["hour"].between(18, 18 + extra_hours)
    df.loc[extended_mask, "occupancy"] *= 1.2

df["temperature"] *= (1 + hvac_adjustment / 100)

df["prediction"] = predict_energy(model, df)
df = detect_inefficiency(df)


# ======================================================
# CORE METRICS
# ======================================================
actual_energy = base_df["energy_kwh"].sum()
predicted_energy = df["prediction"].sum()
cost_per_kwh = 8
predicted_cost = predicted_energy * cost_per_kwh

inefficient_df = df[df["inefficiency_flag"]]
waste_energy = inefficient_df["prediction"].sum()

emission_factor = 0.82
co2_per_tree = 21
predicted_emissions = predicted_energy * emission_factor
trees_required = predicted_emissions / co2_per_tree

efficiency_score = int((1 - len(inefficient_df)/len(df)) * 100)


# ======================================================
# EXECUTIVE OVERVIEW
# ======================================================
if page == "Executive Overview":

    st.title("📊 Executive Energy Overview")

    st.markdown("### 🤖 Machine Learning Engine")
    st.info(
        "Prediction models built using Scikit-Learn (Random Forest Regression) "
        "to forecast energy consumption and support scenario-based optimization."
    )

    with st.expander("View Model Details"):
        st.write("""
        - Algorithm: Random Forest Regressor  
        - Library: Scikit-Learn  
        - Features Used: Hour, Temperature, Occupancy, Weekend Indicator  
        - Training Split: 80/20  
        - Purpose: Predict future energy demand and optimize building performance  
        """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Energy (kWh)", round(predicted_energy, 2))
    col2.metric("Predicted Cost (₹)", round(predicted_cost, 2))
    col3.metric("Efficiency Score", f"{efficiency_score}/100")


# ======================================================
# OPTIMIZATION
# ======================================================
elif page == "Optimization":

    st.title("⚡ Optimization Insights")

    st.metric("Waste Energy (kWh)", round(waste_energy, 2))

    optimized_energy = predicted_energy - (waste_energy * 0.15)
    optimized_cost = optimized_energy * cost_per_kwh

    colA, colB = st.columns(2)
    colA.metric("Optimized Energy Target", round(optimized_energy, 2))
    colB.metric("Optimized Cost Target (₹)", round(optimized_cost, 2))


# ======================================================
# CLIMATE
# ======================================================
elif page == "Climate":

    st.title("🌍 Climate Impact")

    col1, col2 = st.columns(2)
    col1.metric("Projected CO₂ Emissions (kg)", round(predicted_emissions, 2))
    col2.metric("Trees Required for Offset", int(round(trees_required, 0)))


# ======================================================
# USAGE ANALYZER
# ======================================================
elif page == "Usage Analyzer":

    st.title("📈 Advanced Energy Forecasting")

    historical_df = base_df.tail(7 * 24).copy()
    st.line_chart(historical_df["energy_kwh"])


# ======================================================
# TECHNICAL DASHBOARD
# ======================================================
elif page == "Technical Dashboard":

    st.title("🔬 Technical Energy Dashboard")
    render_dashboard(df)


# ======================================================
# PDF EXPORT
# ======================================================
st.sidebar.markdown("---")

if st.sidebar.button("Download Executive PDF Report"):

    doc = SimpleDocTemplate("EnergySense_Report.pdf")
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("EnergySense Executive Report", styles["Heading1"]))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(f"Predicted Energy: {round(predicted_energy, 2)} kWh", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Predicted Cost: ₹{round(predicted_cost, 2)}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"CO₂ Emissions: {round(predicted_emissions, 2)} kg", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Trees Required for Offset: {int(round(trees_required, 0))}", styles["Normal"]))

    doc.build(elements)

    with open("EnergySense_Report.pdf", "rb") as file:
        st.sidebar.download_button(
            "Click to Download Report",
            file,
            file_name="EnergySense_Report.pdf"
        )