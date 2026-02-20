import streamlit as st
import pandas as pd


def render_dashboard(df):
    st.title("EnergySense")
    st.write("Predictive energy optimization dashboard for smart buildings")

    st.subheader("Key Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Energy (kWh)",
        round(df["energy_kwh"].mean(), 2)
    )

    peak_hour = (
        df.groupby("hour")["energy_kwh"]
        .mean()
        .idxmax()
    )
    col2.metric("Peak Hour", peak_hour)

    col3.metric(
        "Inefficient Periods",
        int(df["inefficiency_flag"].sum())
    )

    st.subheader("Energy Usage: Actual vs Predicted")

    chart_df = df[["energy_kwh", "prediction"]]
    st.line_chart(chart_df)

    if df["inefficiency_flag"].any():
        st.warning("⚠ Energy inefficiencies detected")

        inefficient_df = df[df["inefficiency_flag"]][
            ["hour", "occupancy", "energy_kwh", "estimated_waste_percent"]
        ].sort_values("estimated_waste_percent", ascending=False)

        st.dataframe(inefficient_df.head(10))
