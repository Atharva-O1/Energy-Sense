import pandas as pd


def detect_inefficiency(df, occupancy_threshold=30):
    """
    Flags inefficient energy usage periods.

    Conditions:
    - Occupancy below threshold
    - Energy usage above daily average

    Adds:
    - inefficiency_flag (True/False)
    - estimated_waste_percent
    """

    df = df.copy()

    daily_avg = df["energy_kwh"].mean()

    df["inefficiency_flag"] = (
        (df["occupancy"] < occupancy_threshold) &
        (df["energy_kwh"] > daily_avg)
    )

    df["estimated_waste_percent"] = 0.0
    waste_rows = df["inefficiency_flag"]

    df.loc[waste_rows, "estimated_waste_percent"] = (
        (df.loc[waste_rows, "energy_kwh"] - daily_avg)
        / daily_avg
    ) * 100

    df["estimated_waste_percent"] = df["estimated_waste_percent"].clip(0, 100)

    return df