import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

FEATURE_COLUMNS = [
    "hour",
    "temperature",
    "occupancy",
    "is_weekend"
]

def train_model(df):
    X = df[FEATURE_COLUMNS]
    y = df["energy_kwh"]

    split_index = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=10
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    print(f"[Model] RMSE: {rmse:.2f}")

    return model

def predict_energy(model, df):
    X = df[FEATURE_COLUMNS]
    return model.predict(X)