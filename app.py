import streamlit as st
import re
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard


def extract_threshold(question):
    numbers = re.findall(r'\d+', question)
    if numbers:
        value = int(numbers[0])
        if 10 <= value <= 60:
            return value
    return None


def main():
    st.set_page_config(layout="wide")

    # Step 1: Load data
    df = generate_data()

    # Step 2: Train model
    model = train_model(df)

    # Step 3: Predict energy
    df["prediction"] = predict_energy(model, df)

    # ---------------------------------
    # What-If Question Section
    # ---------------------------------
    st.markdown("## 🤔 Ask a What-If Question")
    st.caption("Example: 'What if occupancy threshold is 45?'")

    question = st.text_input("Type your what-if question here:")

    # Baseline
    baseline_df = detect_inefficiency(df.copy(), occupancy_threshold=30)
    baseline_count = int(baseline_df["inefficiency_flag"].sum())
    baseline_waste = baseline_df[baseline_df["inefficiency_flag"]]["energy_kwh"].sum()

    scenario_threshold = 30  # default

    if question:
        extracted = extract_threshold(question)
        if extracted:
            scenario_threshold = extracted
        else:
            st.warning("Please include a threshold value between 10 and 60 in your question.")

    # Scenario calculation
    scenario_df = detect_inefficiency(df.copy(), occupancy_threshold=scenario_threshold)
    scenario_count = int(scenario_df["inefficiency_flag"].sum())
    scenario_waste = scenario_df[scenario_df["inefficiency_flag"]]["energy_kwh"].sum()

    # Replace df with scenario result
    df = scenario_df

    # Cost calculation
    cost_per_kwh = 8
    scenario_cost = scenario_waste * cost_per_kwh
    baseline_cost = baseline_waste * cost_per_kwh
    cost_difference = scenario_cost - baseline_cost

    # Display Answer
    if question:
        st.markdown("### 📊 Scenario Answer")

        st.write(
            f"If occupancy threshold is set to **{scenario_threshold}**, "
            f"the system detects **{scenario_count} inefficient periods**, "
            f"compared to **{baseline_count} under baseline (30)**."
        )

        if scenario_count > baseline_count:
            st.error(
                f"This increases detected inefficiencies by {scenario_count - baseline_count} periods "
                f"and raises estimated cost exposure by ₹{round(cost_difference, 2)}."
            )
        elif scenario_count < baseline_count:
            st.success(
                f"This reduces flagged inefficiencies by {baseline_count - scenario_count} periods "
                f"and lowers projected cost exposure by ₹{abs(round(cost_difference, 2))}."
            )
        else:
            st.info("This threshold produces the same inefficiency detection as baseline.")

    # Render dashboard
    render_dashboard(df)


if __name__ == "__main__":
    main()