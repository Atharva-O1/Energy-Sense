import pandas as pd
import numpy as np


def generate_data(days=30, freq="H", seed=42):
    np.random.seed(seed)

    periods = days * 24
    timestamps = pd.date_range(
        end=pd.Timestamp.now(),
        periods=periods,
        freq=freq
    )

    df = pd.DataFrame({"timestamp": timestamps})

    # Time features
    df["hour"] = df["timestamp"].dt.hour
    df["dayofweek"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = df["dayofweek"] >= 5

    # Temperature (daily cycle + noise)
    base_temp = 22
    temp_variation = 8 * np.sin(2 * np.pi * df["hour"] / 24)
    df["temperature"] = (
        base_temp
        + temp_variation
        + np.random.normal(0, 1.5, len(df))
    )

    # Occupancy logic
    def occupancy_logic(row):
        if row["is_weekend"]:
            return np.random.randint(5, 30)
        if 9 <= row["hour"] <= 18:
            return np.random.randint(60, 100)
        return np.random.randint(10, 40)

    df["occupancy"] = df.apply(occupancy_logic, axis=1)

    # Energy consumption
    base_energy = 20
    temp_factor = 0.6 * df["temperature"]
    occupancy_factor = 0.4 * df["occupancy"]
    noise = np.random.normal(0, 5, len(df))

    df["energy_kwh"] = base_energy + temp_factor + occupancy_factor + noise
    df["energy_kwh"] = df["energy_kwh"].clip(lower=10)

    return df