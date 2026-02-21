import streamlit as st
import pandas as pd


def render_dashboard(df):

    st.markdown("## 🔬 Technical Energy Dashboard")

    # =====================================================
    # BASIC METRICS
    # =====================================================

    avg_actual = df["energy_kwh"].mean()
    avg_predicted = df["prediction"].mean()

    peak_hour = (
        df.groupby("hour")["prediction"]
        .mean()
        .idxmax()
    )

    inefficient_count = int(df["inefficiency_flag"].sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Actual (kWh)", round(avg_actual, 2))
    col2.metric("Avg Predicted (kWh)", round(avg_predicted, 2))
    col3.metric("Peak Load Hour", f"{peak_hour}:00")
    col4.metric("Inefficient Periods", inefficient_count)

    st.markdown("---")

    # =====================================================
    # ACTUAL VS PREDICTED TREND
    # =====================================================

    st.subheader("Actual vs Predicted Energy Trend")

    trend_df = df[["energy_kwh", "prediction"]].copy()
    trend_df.columns = ["Actual Energy", "Predicted Energy"]

    st.line_chart(trend_df)

    st.markdown("---")

    # =====================================================
    # HOURLY LOAD PROFILE
    # =====================================================

    st.subheader("Hourly Load Profile (Average)")

    hourly_profile = (
        df.groupby("hour")[["energy_kwh", "prediction"]]
        .mean()
        .reset_index()
    )

    hourly_profile.set_index("hour", inplace=True)
    hourly_profile.columns = ["Actual", "Predicted"]

    st.line_chart(hourly_profile)

    st.markdown("---")

    # =====================================================
    # TOP INEFFICIENT PERIODS
    # =====================================================

    inefficient_df = df[df["inefficiency_flag"]]

    if not inefficient_df.empty:

        st.subheader("Top Inefficient Periods")

        display_cols = [
            "hour",
            "occupancy",
            "energy_kwh",
            "prediction",
            "estimated_waste_percent"
        ]

        st.dataframe(
            inefficient_df[display_cols]
            .sort_values("estimated_waste_percent", ascending=False)
            .head(10),
            use_container_width=True
        )

    else:
        st.success("No inefficiencies detected in current scenario.")