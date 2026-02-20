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

    # Step 4: Detect inefficiencies
    df = detect_inefficiency(df)

    # Step 5: Render dashboard
    render_dashboard(df)


if __name__ == "__main__":
    main()