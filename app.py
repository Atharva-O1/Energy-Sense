import streamlit as st
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard


def main():
    st.set_page_config(layout="wide")

    # =====================================================
    # HEADER
    # =====================================================

    st.title("⚡ EnergySense")
    st.caption("Energy Consumption Optimizer for Smart Buildings")

    st.markdown("---")

    # =====================================================
    # LOAD & TRAIN
    # =====================================================

    base_df = generate_data()
    model = train_model(base_df)
    base_df["prediction"] = predict_energy(model, base_df)

    # =====================================================
    # 1️⃣ PROBLEM CONTEXT
    # =====================================================

    st.markdown("## 🏢 The Problem")

    st.markdown(
        """
        Commercial and educational buildings are experiencing rising electricity consumption
        due to increased HVAC usage, climate variation, and occupancy changes.

        Most systems only show past bills — they do not predict or prevent waste.
        """
    )

    actual_energy = base_df["energy_kwh"].sum()
    st.metric("Current Building Energy Usage (kWh)", round(actual_energy, 2))

    st.markdown("---")

    # =====================================================
    # 2️⃣ HVAC WHAT-IF SIMULATOR
    # =====================================================

    st.markdown("## ⚙ HVAC What-If Simulator")
    st.caption("Simulate operational changes before implementation.")

    col1, col2 = st.columns(2)

    occupancy_change = col1.slider("Occupancy Change (%)", -50.0, 100.0, 0.0, 1.0)
    extra_hours = col2.slider("Extend Working Hours (hrs/day)", 0.0, 8.0, 0.0, 0.5)

    st.markdown("### 🌡 HVAC Controls")

    colH1, colH2, colH3 = st.columns(3)

    hvac_intensity = colH1.slider("HVAC Intensity (%)", 50.0, 150.0, 100.0, 1.0)
    temp_change = colH2.slider("Temperature Setpoint Change (°C)", -5.0, 5.0, 0.0, 0.5)
    hvac_extension = colH3.slider("HVAC Extension (hrs)", 0.0, 6.0, 0.0, 0.5)

    df = base_df.copy()

    df["occupancy"] *= (1 + occupancy_change / 100)

    if extra_hours > 0:
        mask = df["hour"].between(18, 18 + int(extra_hours))
        df.loc[mask, "occupancy"] *= 1.2

    df["temperature"] += temp_change
    df["temperature"] *= (hvac_intensity / 100)

    if hvac_extension > 0:
        mask = df["hour"].between(18, 18 + int(hvac_extension))
        df.loc[mask, "temperature"] *= 1.15

    df["prediction"] = predict_energy(model, df)
    df = detect_inefficiency(df)

    predicted_energy = df["prediction"].sum()
    energy_difference = predicted_energy - actual_energy

    cost_per_kwh = 8
    predicted_cost = predicted_energy * cost_per_kwh

    # =====================================================
    # 3️⃣ EXECUTIVE OVERVIEW
    # =====================================================

    st.markdown("## 📊 Executive Energy Overview")

    colA, colB, colC = st.columns(3)

    colA.metric("Actual Energy (kWh)", round(actual_energy, 2))
    colB.metric(
        "Predicted Energy (kWh)",
        round(predicted_energy, 2),
        delta=round(energy_difference, 2),
        delta_color="inverse",
    )
    colC.metric("Predicted Cost (₹)", round(predicted_cost, 2))

    st.line_chart(df[["energy_kwh", "prediction"]])

    st.markdown("---")

    # =====================================================
    # 4️⃣ OPTIMIZATION INSIGHTS
    # =====================================================

    st.markdown("## 💡 Optimization Insights")

    inefficient_df = df[df["inefficiency_flag"]]

    if inefficient_df.empty:
        st.success("System operating efficiently.")
    else:
        avg_waste = inefficient_df["estimated_waste_percent"].mean()
        st.warning(f"Average inefficiency: {round(avg_waste, 2)}%")

        st.markdown(
            """
            **Recommended Actions:**
            - Reduce HVAC runtime during low occupancy  
            - Adjust thermostat setpoints  
            - Optimize after-hours cooling  
            - Implement occupancy-based automation  
            """
        )

    st.markdown("---")

    # =====================================================
    # 5️⃣ CLIMATE IMPACT
    # =====================================================

    st.markdown("## 🌍 Climate Impact")

    emission_factor = 0.82
    emissions = predicted_energy * emission_factor
    trees_required = emissions / 21

    colX, colY = st.columns(2)

    colX.metric("Projected CO₂ Emissions (kg)", round(emissions, 2))
    colY.metric("Trees Required to Offset", round(trees_required, 1))

    st.markdown("---")

    # =====================================================
    # 6️⃣ BENCHMARKING
    # =====================================================

    st.markdown("## 📈 Why EnergySense?")

    st.markdown(
        """
        **Traditional Systems**
        - Show past bills
        - Fixed HVAC schedules
        - No prediction
        - Reactive management

        **EnergySense**
        - Predicts future energy usage
        - Detects inefficiencies
        - HVAC-focused optimization
        - Interactive simulation
        - Lightweight & accessible
        """
    )

    st.markdown("---")

    # =====================================================
    # 7️⃣ TECHNICAL DASHBOARD
    # =====================================================

    with st.expander("🔬 View Technical Dashboard"):
        render_dashboard(df)


if __name__ == "__main__":
    main()