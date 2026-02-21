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
# ENERGY SCALING
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
# REAL ML TRAIN/TEST SPLIT
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
# METRICS
# =====================================================

total_energy = df["energy_kwh"].sum()
predicted_energy = df["prediction"].sum()
peak_load = df["prediction"].max()
avg_load = df["prediction"].mean()
peak_ratio = peak_load / avg_load
load_variance = df["prediction"].std()
energy_per_sqm = total_energy / area

# =====================================================
# ENERGY OVERVIEW
# =====================================================

st.subheader("📊 Energy Overview")

colA, colB, colC = st.columns(3)
colA.metric("Total Energy (kWh)", round(total_energy, 2))
colB.metric("Predicted Energy (kWh)", round(predicted_energy, 2))
colC.metric("Peak Load (kWh)", round(peak_load, 2))

colD, colE = st.columns(2)
colD.metric("Energy Intensity (kWh/sqm)", round(energy_per_sqm, 2))
colE.metric("Model Accuracy (R²)", round(model_accuracy, 3))

st.line_chart(df[["energy_kwh", "prediction"]])

# =====================================================
# PEAK RISK
# =====================================================

st.subheader("⚡ Peak Risk")

st.metric("Load Variability Index", round(load_variance, 2))

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

col1, col2, col3 = st.columns(3)
col1.metric("CO₂ Emissions (kg)", round(emissions, 2))
col2.metric("Trees Required", round(trees, 1))
col3.metric("Carbon Cost (₹)", round(carbon_cost, 2))

# =====================================================
# CLIMATE CHANGE ANALYZER
# =====================================================

st.subheader("🌡 Climate Change Impact Analyzer")

temp_rise = st.slider("Global Temp Rise (°C)", 0.0, 5.0, 1.0, 0.1)

climate_sensitivity = {
    "Office": 0.03,
    "Educational": 0.025,
    "Mall": 0.05,
    "Hospital": 0.045
}

climate_factor = 1 + (temp_rise * climate_sensitivity[building_type])

st.metric(
    "Future Energy (kWh)",
    round(total_energy * climate_factor, 2),
    delta=round(total_energy * (climate_factor - 1), 2)
)

# =====================================================
# WHAT IF
# =====================================================

st.subheader("🔮 What-If Simulation")

hypo = st.number_input("Hypothetical Energy (kWh)",
                       0.0, float(total_energy * 2),
                       float(total_energy))

if st.button("Run What-If Simulation"):
    st.metric("Projected Cost (₹)", round(hypo * 8, 2))
    st.metric("Projected CO₂ (kg)", round(hypo * 0.82, 2))

# =====================================================
# MANUAL ANALYZER
# =====================================================

st.subheader("🧠 Manual Energy Consumption Analyzer")

user_energy = st.number_input(
    "Enter Energy Consumed (kWh)",
    min_value=0.0,
    step=50.0
)

if st.button("Run Manual Analysis"):

    predicted_next = user_energy * 1.05
    cost_estimate = user_energy * 8
    emissions_estimate = user_energy * 0.82

    col1, col2, col3 = st.columns(3)

    col1.metric("Predicted Next Period (kWh)",
                round(predicted_next, 2),
                delta=round(predicted_next - user_energy, 2))
    col2.metric("Estimated Cost (₹)", round(cost_estimate, 2))
    col3.metric("CO₂ Emissions (kg)", round(emissions_estimate, 2))

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

if temp_rise > 2.5:
    recommendations.append("Prepare adaptive cooling strategies.")

if len(recommendations) == 0:
    st.success("System operating within optimal efficiency.")
else:
    with st.expander("📋 View Optimization Plan"):
        for rec in recommendations:
            st.write("•", rec)

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
    elements.append(Paragraph(f"Generated: {datetime.now()}",
                              styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Building Configuration", styles["Heading2"]))
    elements.append(Paragraph(
        f"""
        Type: {building_type}<br/>
        Area: {area} sqm<br/>
        Floors: {floors}<br/>
        HVAC: {hvac_type}<br/>
        Intensity: {intensity}
        """,
        styles["Normal"]
    ))

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
        Trees Required: {round(trees,1)}<br/>
        Model Accuracy (R²): {round(model_accuracy,3)}
        """,
        styles["Normal"]
    ))

    if recommendations:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Optimization Recommendations",
                                  styles["Heading2"]))
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles["Normal"]))

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