import streamlit as st
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from datetime import datetime


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

# =====================================================
# DARK THEME (UNCHANGED)
# =====================================================

if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    section[data-testid="stSidebar"] { background-color: #1F2937; }
    div[data-testid="stMetricValue"] { color: #22D3EE; }
    </style>
    """, unsafe_allow_html=True)

# =====================================================
# LIGHT THEME (IMPROVED)
# =====================================================

else:
    st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #E2E8F0; }
    div[data-testid="stMetricValue"] { color: #1D4ED8; }

    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
    }

    .stButton>button:hover {
        background-color: #1E40AF;
        color: white;
    }
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
# DIGITAL TWIN CONFIGURATION
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

model = train_model(df)
df["prediction"] = predict_energy(model, df)
df = detect_inefficiency(df)

total_energy = df["energy_kwh"].sum()
predicted_energy = df["prediction"].sum()
peak_load = df["prediction"].max()
avg_load = df["prediction"].mean()
peak_ratio = peak_load / avg_load

# =====================================================
# ENERGY OVERVIEW
# =====================================================

st.subheader("📊 Energy Overview")

colA, colB, colC = st.columns(3)
colA.metric("Total Energy (kWh)", round(total_energy, 2))
colB.metric("Predicted Energy (kWh)", round(predicted_energy, 2))
colC.metric("Peak Load (kWh)", round(peak_load, 2))

st.line_chart(df[["energy_kwh", "prediction"]])

# =====================================================
# PEAK RISK
# =====================================================

st.subheader("⚡ Peak Risk")

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

st.metric("CO₂ Emissions (kg)", round(emissions, 2))
st.metric("Trees Required", round(trees, 1))

# =====================================================
# CLIMATE CHANGE ANALYZER
# =====================================================

st.subheader("🌡 Climate Change Impact Analyzer")

temp_rise = st.slider("Global Temp Rise (°C)", 0.0, 5.0, 1.0, 0.1)

climate_factor = 1 + (temp_rise * 0.04)

st.metric(
    "Future Energy (kWh)",
    round(total_energy * climate_factor, 2),
    delta=round(total_energy * (climate_factor - 1), 2)
)

# =====================================================
# WHAT IF SIMULATOR
# =====================================================

st.subheader("🔮 What-If Simulation")

hypo = st.number_input("Hypothetical Energy (kWh)",
                       0.0, float(total_energy * 2),
                       float(total_energy))

if st.button("Run Simulation"):
    st.metric("Projected Cost (₹)", round(hypo * 8, 2))
    st.metric("Projected CO₂ (kg)", round(hypo * 0.82, 2))

# =====================================================
# 🧠 MANUAL ENERGY ANALYZER
# =====================================================

st.subheader("🧠 Manual Energy Consumption Analyzer")

user_energy = st.number_input(
    "Enter Energy Consumed (kWh)",
    min_value=0.0,
    step=100.0
)

if st.button("Analyze Consumption"):

    if user_energy > 0:

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
# 🛠 INTELLIGENT ENERGY OPTIMIZATION ADVISOR (NEW)
# =====================================================

st.subheader("🛠 Intelligent Energy Optimization Advisor")

recommendations = []

if peak_ratio > 1.5:
    recommendations.append(("High Impact",
                            "Implement demand response and load shifting strategies."))

if hvac_type == "Central HVAC":
    recommendations.append(("High Impact",
                            "Adopt HVAC zoning and occupancy-based automation."))

if intensity == "High":
    recommendations.append(("Medium Impact",
                            "Upgrade to energy-efficient equipment and optimize setpoints."))

if df["inefficiency_flag"].sum() > 10:
    recommendations.append(("High Impact",
                            "Automate scheduling during low occupancy hours."))

if temp_rise > 2.5:
    recommendations.append(("Medium Impact",
                            "Prepare adaptive cooling strategy for climate resilience."))

if user_energy > total_energy * 1.2:
    recommendations.append(("Critical",
                            "Immediate operational audit required to reduce excess load."))

if len(recommendations) == 0:
    st.success("System operating within optimal efficiency parameters.")
else:
    for level, rec in recommendations:
        if level == "Critical":
            st.error(f"🔴 {level}: {rec}")
        elif level == "High Impact":
            st.warning(f"🟠 {level}: {rec}")
        else:
            st.info(f"🔵 {level}: {rec}")

# =====================================================
# PDF EXPORT
# =====================================================

st.subheader("📄 Export Report")

def generate_pdf():
    file = "EnergySense_Report.pdf"
    doc = SimpleDocTemplate(file, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("EnergySense Report", styles["Heading1"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated: {datetime.now()}",
                              styles["Normal"]))

    doc.build(elements)
    return file

if st.button("Generate PDF"):
    path = generate_pdf()
    with open(path, "rb") as f:
        st.download_button("Download Report", f,
                           file_name="EnergySense_Report.pdf",
                           mime="application/pdf")