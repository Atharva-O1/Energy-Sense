from data_engine import generate_data
from model_engine import train_model, predict_energy

df = generate_data()
model = train_model(df)
df["prediction"] = predict_energy(model, df)

print(df[["energy_kwh", "prediction"]].head())