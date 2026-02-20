from data_engine import generate_data
from model_engine import train_model, predict_energy
from optimizer import detect_inefficiency

df = generate_data()
model = train_model(df)
df["prediction"] = predict_energy(model, df)

df = detect_inefficiency(df)

print(df[df["inefficiency_flag"]][
    ["hour", "occupancy", "energy_kwh", "estimated_waste_percent"]
].head())