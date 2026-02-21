from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

app = FastAPI()

# In-memory storage for hackathon
ingested_data = []

class EnergyPayload(BaseModel):
    timestamp: datetime
    temperature: float
    occupancy: float
    energy_kwh: float

@app.post("/ingest")
def ingest_data(payload: EnergyPayload):
    record = payload.dict()
    ingested_data.append(record)
    return {"status": "Data received successfully"}

@app.get("/data")
def get_data():
    return ingested_data