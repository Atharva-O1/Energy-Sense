import streamlit as st
import numpy as np
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard


def main():
    st.set_page_config(layout="wide")

    # Load base data
    base_df = generate_data()

    # Train model once
    model = train_model(base_df)

    st.markdown("## ⚙️ What-If Scenario Simulator")
    st.caption("Simulate operational changes before they happen.")

    # -----------------------
    # Simulation Controls
    # -----------------------
    occupancy_increase = st.slider(
        "What if occupancy increases by (%)",
        0, 50, 0
    )

    extra_hours = st.slider(
        "What if working hours extend by (hours per day)",
        0, 4, 0
    )

    hvac_adjustment = st.slider(
        "What if HVAC load increases by (%)",
        -20, 30, 0
    )

    # Copy dataframe for scenario
    df = base_df.copy()

    # Apply occupancy change
    df["occupancy"] = df["occupancy"] * (1 + occupancy_increase / 100)

    # Apply working hour extension
    if extra_hours > 0:
        extended_mask = df["hour"].between(18, 18 + extra_hours)
        df.loc[extended_mask, "occupancy"] *= 1.2

    # Apply HVAC adjustment (via temperature impact)
    df["temperature"] = df["temperature"] * (1 + hvac_adjustment / 100)

    # Predict new energy
    df["prediction"] = predict_energy(model, df)

    # Detect inefficiency
    df = detect_inefficiency(df)

    # -----------------------
    # Impact Metrics
    # -----------------------
    baseline_energy = base_df["energy_kwh"].sum()
    scenario_energy = df["prediction"].sum()

    energy_change = scenario_energy - baseline_energy

    st.markdown("### 📊 Scenario Impact")

    col1, col2 = st.columns(2)

    col1.metric(
        "Predicted Total Energy (kWh)",
        round(scenario_energy, 2),
        delta=round(energy_change, 2)
    )

    cost_per_kwh = 8
    cost_impact = energy_change * cost_per_kwh

    col2.metric(
        "Estimated Cost Impact (₹)",
        round(scenario_energy * cost_per_kwh, 2),
        delta=round(cost_impact, 2)
    )

    # Smart Explanation
    st.markdown("### 🧠 Insight")

    if energy_change > 0:
        st.warning(
            "Operational changes increase projected energy consumption. "
            "Consider optimizing HVAC schedules or load balancing."
        )
    elif energy_change < 0:
        st.success(
            "Scenario reduces projected energy consumption. "
            "This configuration improves operational efficiency."
        )
    else:
        st.info("No operational impact detected.")

    # Render dashboard
    render_dashboard(df)


if __name__ == "__main__":
    main()