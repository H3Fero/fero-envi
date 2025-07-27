from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
cache = redis.Redis(host="redis", port=6379, decode_responses=True)

stations_data = {
    "Paris": [
        {"train": "EIY30U", "destination": "Londres", "heure": "08:00"},
        {"train": "AEV7C0", "destination": "Amsterdam", "heure": "09:30"},
        {"train": "A9TI8C", "destination": "Lisbonne", "heure": "12:00"}
    ],
    "Amsterdam": [
        {"train": "E2ME1Z", "destination": "Paris", "heure": "10:00"},
        {"train": "A4SH3L", "destination": "Londres", "heure": "15:30"},
        {"train": "UJ2CHU", "destination": "Lisbonne", "heure": "17:00"}
    ],
    "Londres": [
        {"train": "WI0PH1", "destination": "Paris", "heure": "09:00"}
    ],
    "Lisbonne": [
        {"train": "OHNAH9", "destination": "Paris", "heure": "07:00"}
    ]
}

@app.get("/horaires/{station}")
def horaires(station: str):
    if cache.exists(station):
        return json.loads(cache.get(station))
    data = stations_data.get(station, [])
    cache.setex(station, 300, json.dumps(data))
    return data