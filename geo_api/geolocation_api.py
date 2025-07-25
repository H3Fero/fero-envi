from fastapi import FastAPI
from pydantic import BaseModel
from geopy.distance import geodesic

app = FastAPI()
STATIONS = {
    "Paris": (48.8566, 2.3522),
    "Amsterdam": (52.379189, 4.899431),
    "Londres": (51.5074, -0.1278),
    "Lisbonne": (38.7169, -9.1399)
}

class LocalisationRequest(BaseModel):
    user_lat: float
    user_lon: float
    station: str

@app.post("/localisation")
def localisation(payload: LocalisationRequest):
    dst_coords = STATIONS.get(payload.station)
    if not dst_coords:
        return {"error": "Station inconnue."}
    user_coords = (payload.user_lat, payload.user_lon)
    dist = geodesic(user_coords, dst_coords).kilometers
    return {
        "station": payload.station,
        "user_coordinates": user_coords,
        "station_coordinates": dst_coords,
        "distance_km": round(dist, 2)
    }