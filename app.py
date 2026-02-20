import streamlit as st
import numpy as np
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard

# Clean PDF imports (minimal + stable)
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


st.set_page_config(layout="wide")


# -----------------------
# Cached Model Loading
# -----------------------
@st.cache_resource
def load_and_train():
    df = generate_data()
    model = train_model(df)
    return df, model


base_df, model = load_and_train()
base_df["prediction"] = predict_energy(model, base_df)


# -----------------------
# Sidebar Navigation
# -----------------------
st.sidebar.title("⚡ EnergySense Navigation")

page = st.sidebar.radio(
    "Select View",
    ["Executive Overview", "Optimization", "Climate", "Technical Dashboard"]
)

role = st.sidebar.selectbox(
    "User Role",
    ["Executive", "Facility Manager", "Sustainability Officer"]
)

st.sidebar.markdown("---")

occupancy_increase = st.sidebar.slider("Occupancy Increase (%)", 0, 50, 0)
extra_hours = st.sidebar.slider("Extend Working Hours", 0, 4, 0)
hvac_adjustment = st.sidebar.slider("HVAC Adjustment (%)", -20, 30, 0)


# -----------------------
# Scenario Simulation
# -----------------------
df = base_df.copy()

df["occupancy"] *= (1 + occupancy_increase / 100)

if extra_hours > 0:
    extended_mask = df["hour"].between(18, 18 + extra_hours)
    df.loc[extended_mask, "occupancy"] *= 1.2

df["temperature"] *= (1 + hvac_adjustment / 100)

df["prediction"] = predict_energy(model, df)
df = detect_inefficiency(df)


# -----------------------
# Core Metrics
# -----------------------
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


# -----------------------
# Executive Overview Page
# -----------------------
if page == "Executive Overview":

    st.title("📊 Executive Energy Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Energy (kWh)", round(predicted_energy, 2))
    col2.metric("Predicted Cost (₹)", round(predicted_cost, 2))
    col3.metric("Efficiency Score", f"{efficiency_score}/100")

    st.subheader("🏭 Industry Benchmark Comparison")

    industry_avg = actual_energy * 1.15
    benchmark_diff = predicted_energy - industry_avg

    st.metric(
        "Industry Benchmark Energy (kWh)",
        round(industry_avg, 2),
        delta=round(benchmark_diff, 2),
        delta_color="inverse"
    )

    comparison_text = "more efficient" if predicted_energy < industry_avg else "less efficient"
    st.info(f"Your system is {comparison_text} compared to industry average.")


# -----------------------
# Optimization Page
# -----------------------
elif page == "Optimization":

    st.title("⚡ Optimization Insights")

    st.metric("Waste Energy (kWh)", round(waste_energy, 2))

    optimized_energy = predicted_energy - (waste_energy * 0.15)
    optimized_cost = optimized_energy * cost_per_kwh

    colA, colB = st.columns(2)
    colA.metric("Optimized Energy Target (kWh)", round(optimized_energy, 2))
    colB.metric("Optimized Cost Target (₹)", round(optimized_cost, 2))

    st.markdown("### 💡 Recommended Actions")
    st.markdown("""
    - Optimize HVAC setpoints  
    - Introduce occupancy sensors  
    - Reduce after-hours consumption  
    - Implement predictive maintenance  
    """)


# -----------------------
# Climate Page
# -----------------------
elif page == "Climate":

    st.title("🌍 Climate Impact")

    col1, col2 = st.columns(2)
    col1.metric("Projected CO₂ Emissions (kg)", round(predicted_emissions, 2))
    col2.metric("Trees Required for Offset", int(round(trees_required, 0)))

    st.progress(min(predicted_emissions / (actual_energy * emission_factor * 1.3), 1))


# -----------------------
# Technical Dashboard
# -----------------------
elif page == "Technical Dashboard":

    st.title("🔬 Technical Energy Dashboard")
    render_dashboard(df)


# -----------------------
# PDF Report Generator
# -----------------------
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