from fastapi import FastAPI
import redis
import json

app = FastAPI()
cache = redis.Redis(host="redis", port=6379, decode_responses=True)

stations_data = {
    "Paris": [
        {"train": "ES001", "destination": "Londres", "heure": "08:00"},
        {"train": "ES002", "destination": "Amsterdam", "heure": "09:30"},
        {"train": "ES003", "destination": "Lisbonne", "heure": "12:00"}
    ],
    "Amsterdam": [
        {"train": "ES004", "destination": "Paris", "heure": "10:00"},
        {"train": "ES005", "destination": "Londres", "heure": "15:30"}
    ],
    "Londres": [
        {"train": "ES006", "destination": "Paris", "heure": "09:00"}
    ],
    "Lisbonne": [
        {"train": "ES007", "destination": "Paris", "heure": "07:00"}
    ]
}

@app.get("/horaires/{station}")
def horaires(station: str):
    if cache.exists(station):
        return json.loads(cache.get(station))
    data = stations_data.get(station, [])
    cache.setex(station, 300, json.dumps(data))
    return data