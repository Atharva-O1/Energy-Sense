import streamlit as st
import pandas as pd
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from datetime import datetime
import matplotlib.pyplot as plt
import os

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# =====================================================
# THEME TOGGLE
# =====================================================

colA, colB = st.columns([8, 2])
with colB:
    toggle = st.toggle("🌙 Dark Mode")
    st.session_state.theme = "Dark" if toggle else "Light"

if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    section[data-testid="stSidebar"] { background-color: #1F2937; }
    div[data-testid="stMetricValue"] { color: #22D3EE; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #E2E8F0; }
    div[data-testid="stMetricValue"] { color: #1D4ED8; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("""
<style>
@keyframes gradientFlow {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.header-container {
    background: linear-gradient(270deg, #00C9FF, #92FE9D, #FF6FD8, #00C9FF);
    background-size: 800% 800%;
    animation: gradientFlow 12s ease infinite;
    padding: 40px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 30px;
}
.header-title {
    font-size: 42px;
    font-weight: 800;
    color: white;
}
</style>

<div class="header-container">
    <div class="header-title">⚡ EnergySense</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# DIGITAL TWIN
# =====================================================

st.subheader("🏢 Digital Twin Configuration")

col1, col2, col3 = st.columns(3)

building_type = col1.selectbox("Building Type",
                               ["Office", "Educational", "Mall", "Hospital"])
area = col2.number_input("Area (sqm)", 1000, 50000, 5000)
floors = col3.number_input("Floors", 1, 50, 5)

hvac_type = st.selectbox("HVAC Type",
                         ["Central HVAC", "VRV/VRF", "Split Units"])
intensity = st.selectbox("Energy Intensity",
                         ["Low", "Medium", "High"])

# =====================================================
# DATA + SCALING
# =====================================================

df = generate_data()

intensity_map = {"Low": 0.9, "Medium": 1.0, "High": 1.2}
hvac_map = {"Central HVAC": 1.2, "VRV/VRF": 1.1, "Split Units": 1.0}

multiplier = (
    (area / 5000) *
    (floors / 5) *
    intensity_map[intensity] *
    hvac_map[hvac_type]
)

df["energy_kwh"] *= multiplier

# =====================================================
# ML VALIDATION
# =====================================================

X = df.drop(["energy_kwh"], axis=1)
y = df["energy_kwh"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

train_df = pd.concat([X_train, y_train], axis=1)
model = train_model(train_df)

df["prediction"] = predict_energy(model, X)
preds_test = predict_energy(model, X_test)

model_accuracy = r2_score(y_test, preds_test)

df = detect_inefficiency(df)

# =====================================================
# METRICS CALCULATION
# =====================================================

total_energy = df["energy_kwh"].sum()
predicted_energy = df["prediction"].sum()

energy_diff = predicted_energy - total_energy
energy_percent = (energy_diff / total_energy) * 100 if total_energy else 0

peak_load = df["prediction"].max()
avg_load = df["prediction"].mean()
peak_diff = peak_load - avg_load
peak_percent = (peak_diff / avg_load) * 100 if avg_load else 0
peak_ratio = peak_load / avg_load

load_variance = df["prediction"].std()
baseline_variance = df["energy_kwh"].std()
variance_diff = load_variance - baseline_variance
variance_percent = (variance_diff / baseline_variance) * 100 if baseline_variance else 0

energy_per_sqm = total_energy / area

# =====================================================
# ENERGY OVERVIEW
# =====================================================

st.subheader("📊 Energy Overview")

colA, colB, colC = st.columns(3)

colA.metric("Total Energy (kWh)", round(total_energy, 2))

colB.metric("Predicted Energy (kWh)",
            round(predicted_energy, 2),
            delta=f"{round(energy_diff,2)} ({round(energy_percent,2)}%)")

colC.metric("Peak Load (kWh)",
            round(peak_load, 2),
            delta=f"{round(peak_diff,2)} ({round(peak_percent,2)}%)")

colD, colE = st.columns(2)
colD.metric("Energy Intensity (kWh/sqm)", round(energy_per_sqm, 2))
colE.metric("Model Accuracy (R²)", round(model_accuracy, 3))

st.line_chart(df[["energy_kwh", "prediction"]])

# =====================================================
# PEAK RISK
# =====================================================

st.subheader("⚡ Peak Risk")

st.metric("Load Variability Index",
          round(load_variance, 2),
          delta=f"{round(variance_diff,2)} ({round(variance_percent,2)}%)")

if peak_ratio > 1.5:
    st.error("High Peak Risk")
elif peak_ratio > 1.3:
    st.warning("Moderate Peak Risk")
else:
    st.success("Stable")

# =====================================================
# CLIMATE IMPACT
# =====================================================

st.subheader("🌍 Climate Impact")

emissions = total_energy * 0.82
trees = emissions / 21
carbon_price = 85
carbon_cost = (emissions / 1000) * carbon_price

baseline_emissions = predicted_energy * 0.82
emission_diff = emissions - baseline_emissions
emission_percent = (emission_diff / baseline_emissions) * 100 if baseline_emissions else 0

col1, col2, col3 = st.columns(3)

col1.metric("CO₂ Emissions (kg)",
            round(emissions, 2),
            delta=f"{round(emission_diff,2)} ({round(emission_percent,2)}%)")

col2.metric("Trees Required", round(trees, 1))
col3.metric("Carbon Cost (₹)", round(carbon_cost, 2))

# =====================================================
# WHAT-IF SIMULATION
# =====================================================

st.subheader("🔮 What-If Simulation")

hypo = st.number_input("Hypothetical Energy (kWh)",
                       0.0, float(total_energy * 2),
                       float(total_energy))

if st.button("Run What-If Simulation"):

    cost_now = total_energy * 8
    cost_future = hypo * 8
    cost_diff = cost_future - cost_now
    cost_percent = (cost_diff / cost_now) * 100 if cost_now else 0

    co2_now = total_energy * 0.82
    co2_future = hypo * 0.82
    co2_diff = co2_future - co2_now
    co2_percent = (co2_diff / co2_now) * 100 if co2_now else 0

    st.metric("Projected Cost (₹)",
              round(cost_future, 2),
              delta=f"{round(cost_diff,2)} ({round(cost_percent,2)}%)")

    st.metric("Projected CO₂ (kg)",
              round(co2_future, 2),
              delta=f"{round(co2_diff,2)} ({round(co2_percent,2)}%)")

# =====================================================
# HVAC SYSTEM OPTIMIZER
# =====================================================

st.subheader("❄️ HVAC System Optimizer")

hvac_energy_current = total_energy * 0.40
best_hvac = min(hvac_map, key=hvac_map.get)

if hvac_map[hvac_type] > hvac_map[best_hvac]:

    efficiency_gain_ratio = (hvac_map[hvac_type] - hvac_map[best_hvac]) / hvac_map[hvac_type]
    hvac_energy_saved = hvac_energy_current * efficiency_gain_ratio

    savings_percent = (hvac_energy_saved / total_energy) * 100 if total_energy else 0
    cost_savings = hvac_energy_saved * 8
    emission_savings = hvac_energy_saved * 0.82

    col1, col2, col3 = st.columns(3)

    col1.metric("Potential Energy Savings (kWh)",
                round(hvac_energy_saved, 2),
                delta=f"-{round(savings_percent,2)}%")

    col2.metric("Estimated Cost Savings (₹)", round(cost_savings, 2))
    col3.metric("CO₂ Reduction (kg)", round(emission_savings, 2))

    st.info(f"Recommended Upgrade: Switch to {best_hvac}")

else:
    st.success("Current HVAC system is already optimized.")

# =====================================================
# OPTIMIZATION ENGINE
# =====================================================

st.subheader("🛠 Intelligent Energy Optimization Advisor")

recommendations = []

if peak_ratio > 1.5:
    recommendations.append("Implement demand response and load shifting.")
if hvac_type == "Central HVAC":
    recommendations.append("Introduce HVAC zoning and automation.")
if intensity == "High":
    recommendations.append("Upgrade to high-efficiency systems.")
if df["inefficiency_flag"].sum() > 10:
    recommendations.append("Automate low-occupancy scheduling.")

if recommendations:
    with st.expander("📋 View Optimization Plan"):
        for rec in recommendations:
            st.write("•", rec)
else:
    st.success("System operating within optimal efficiency.")

# =====================================================
# MANUAL ANALYZER
# =====================================================

st.subheader("🧠 Manual Energy Consumption Analyzer")

user_energy = st.number_input("Enter Energy Consumed (kWh)", min_value=0.0, step=50.0)

if st.button("Run Manual Analysis"):

    predicted_next = user_energy * 1.05
    cost_estimate = user_energy * 8
    emissions_estimate = user_energy * 0.82

    st.metric("Predicted Next Period (kWh)",
              round(predicted_next, 2),
              delta=round(predicted_next - user_energy, 2))

    st.metric("Estimated Cost (₹)", round(cost_estimate, 2))
    st.metric("CO₂ Emissions (kg)", round(emissions_estimate, 2))

# =====================================================
# FULL PDF REPORT
# =====================================================

st.subheader("📄 Export Full Energy Report")

def generate_pdf():

    file = "EnergySense_Report.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("EnergySense Executive Report", styles["Heading1"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated: {datetime.now()}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    chart_path = "energy_chart.png"
    plt.figure()
    plt.plot(df["energy_kwh"], label="Actual")
    plt.plot(df["prediction"], label="Predicted")
    plt.legend()
    plt.title("Energy Trend")
    plt.savefig(chart_path)
    plt.close()

    elements.append(Image(chart_path, width=400, height=200))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"""
        Total Energy: {round(total_energy,2)} kWh<br/>
        Predicted Energy: {round(predicted_energy,2)} kWh<br/>
        Peak Load: {round(peak_load,2)} kWh<br/>
        CO₂ Emissions: {round(emissions,2)} kg<br/>
        Carbon Cost: {round(carbon_cost,2)} ₹<br/>
        Model Accuracy (R²): {round(model_accuracy,3)}
        """,
        styles["Normal"]
    ))

    doc.build(elements)

    if os.path.exists(chart_path):
        os.remove(chart_path)

    return file

if st.button("Generate Detailed PDF Report"):
    path = generate_pdf()
    with open(path, "rb") as f:
        st.download_button("Download Report",
                           f,
                           file_name="EnergySense_Report.pdf",
                           mime="application/pdf")


