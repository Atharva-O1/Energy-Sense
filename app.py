import streamlit as st
import numpy as np
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard


def main():
    st.set_page_config(layout="wide")

    # -----------------------
    # Load & Train
    # -----------------------
    base_df = generate_data()
    model = train_model(base_df)

    base_df["prediction"] = predict_energy(model, base_df)
    baseline_energy = base_df["prediction"].sum()

    # -----------------------
    # What-If Scenario Simulator
    # -----------------------
    st.markdown("## ⚙️ What-If Scenario Simulator")
    st.caption("Simulate operational changes before implementation.")

    occupancy_increase = st.slider("Occupancy Increase (%)", 0, 50, 0)
    extra_hours = st.slider("Extend Working Hours (hours/day)", 0, 4, 0)
    hvac_adjustment = st.slider("HVAC Load Adjustment (%)", -20, 30, 0)

    df = base_df.copy()

    # Apply occupancy adjustment
    df["occupancy"] = df["occupancy"] * (1 + occupancy_increase / 100)

    # Apply extended hours
    if extra_hours > 0:
        extended_mask = df["hour"].between(18, 18 + extra_hours)
        df.loc[extended_mask, "occupancy"] *= 1.2

    # Apply HVAC adjustment via temperature
    df["temperature"] = df["temperature"] * (1 + hvac_adjustment / 100)

    # Predict new energy
    df["prediction"] = predict_energy(model, df)

    # Detect inefficiencies
    df = detect_inefficiency(df)

    scenario_energy = df["prediction"].sum()
    energy_change = scenario_energy - baseline_energy

    # -----------------------
    # Business Impact
    # -----------------------
    st.markdown("### 📊 Business Impact")

    cost_per_kwh = 8
    scenario_cost = scenario_energy * cost_per_kwh
    baseline_cost = baseline_energy * cost_per_kwh
    cost_change = scenario_cost - baseline_cost

    col1, col2 = st.columns(2)

    col1.metric(
        "Predicted Total Energy (kWh)",
        round(scenario_energy, 2),
        delta=round(energy_change, 2),
        delta_color="inverse"
    )

    col2.metric(
        "Estimated Cost Impact (₹)",
        round(scenario_cost, 2),
        delta=round(cost_change, 2),
        delta_color="inverse"
    )

    # -----------------------
    # Climate Impact Analyzer
    # -----------------------
    st.markdown("## 🌍 Climate Impact Analyzer")
    st.caption("Measure carbon footprint impact of operational decisions.")

    emission_factor = 0.82  # kg CO2 per kWh

    baseline_emissions = baseline_energy * emission_factor
    scenario_emissions = scenario_energy * emission_factor
    emission_change = scenario_emissions - baseline_emissions

    colA, colB = st.columns(2)

    colA.metric(
        "Projected CO₂ Emissions (kg)",
        round(scenario_emissions, 2),
        delta=round(emission_change, 2),
        delta_color="inverse"
    )

    trees_equivalent = scenario_emissions / 21
    colB.metric(
        "Equivalent Trees Required",
        round(trees_equivalent, 1)
    )

    # -----------------------
    # Optimization Recommendations
    # -----------------------
    st.markdown("## 💡 Optimization Recommendations")
    st.caption("AI-driven suggestions to reduce energy waste and lower operational costs.")

    inefficient_df = df[df["inefficiency_flag"]]

    if inefficient_df.empty:
        st.success("No major inefficiencies detected. Current configuration is optimized.")
    else:
        avg_waste_percent = inefficient_df["estimated_waste_percent"].mean()

        potential_savings_kwh = inefficient_df["prediction"].sum() * 0.15
        potential_savings_cost = potential_savings_kwh * cost_per_kwh

        st.warning(
            f"Average waste during flagged periods is approximately {round(avg_waste_percent, 2)}%."
        )

        st.markdown("### 🔧 Suggested Actions")

        st.markdown(
            "- Adjust HVAC scheduling during low occupancy hours.\n"
            "- Reduce cooling/heating load after working hours.\n"
            "- Implement occupancy-based automation systems.\n"
            "- Optimize temperature setpoints by 1–2°C."
        )

        st.markdown("### 💰 Potential Savings Estimate")

        colS1, colS2 = st.columns(2)

        colS1.metric(
            "Potential Energy Savings (kWh)",
            round(potential_savings_kwh, 2)
        )

        colS2.metric(
            "Potential Cost Reduction (₹)",
            round(potential_savings_cost, 2)
        )

    # -----------------------
    # Render Main Dashboard
    # -----------------------
    render_dashboard(df)


if __name__ == "__main__":
    main()