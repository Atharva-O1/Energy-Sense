import streamlit as st
import pandas as pd


def render_dashboard(df):
    st.title("EnergySense")
    st.write("Predictive energy optimization dashboard for smart buildings")

    st.subheader("Key Metrics")
    st.caption("Overview of building energy performance")

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

    # Live inefficiency feedback
    inefficient_count = int(df["inefficiency_flag"].sum())

    if inefficient_count == 0:
        st.success("✅ No inefficiencies detected under current threshold.")
    else:
        st.error(f"⚠ {inefficient_count} inefficient periods detected.")

    st.subheader("Energy Usage: Actual vs Predicted")
    st.caption("Model prediction vs actual consumption trends")

    chart_df = df[["energy_kwh", "prediction"]]
    st.line_chart(chart_df)

    if df["inefficiency_flag"].any():
        st.subheader("Top Inefficient Periods")
        st.caption("Periods where energy usage exceeded expected levels under low occupancy.")

        inefficient_df = df[df["inefficiency_flag"]][
            ["hour", "occupancy", "energy_kwh", "estimated_waste_percent"]
        ].sort_values("estimated_waste_percent", ascending=False)

        st.dataframe(inefficient_df.head(10))