import streamlit as st
from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency
from dashboard import render_dashboard


def main():
    st.set_page_config(layout="wide")

    # Step 1: Load data
    df = generate_data()

    # Step 2: Train model
    model = train_model(df)

    # Step 3: Predict energy
    df["prediction"] = predict_energy(model, df)

    # --- What-If Control (PUT IT HERE) ---
    threshold = st.slider(
        "Occupancy Threshold for Inefficiency Detection",
        min_value=10,
        max_value=60,
        value=30,
        help="If occupancy falls below this value while energy is high, it is flagged as inefficient."
    )

    # Step 4: Apply inefficiency detection
    df = detect_inefficiency(df, occupancy_threshold=threshold)

    # Step 5: Render dashboard
    render_dashboard(df)


if __name__ == "__main__":
    main()