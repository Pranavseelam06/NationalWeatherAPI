from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from logic_no_gpd import is_point_in_alert, nearest_safe_city_vectorized
from alerts_index import get_alert_index

app = FastAPI(title="Weather Safety API")

# Enable CORS so frontend can fetch data
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Send /checkSafety?lat=&lon=&city=CityName&state=StateCode to get alerts and nearby safe cities."}

@app.get("/checkSafety")
def check_safety(
    lat: float = Query(...),
    lon: float = Query(...),
    city: str = Query(None),
    state: str = Query(None)
):
    alerts_index = get_alert_index()
    alerts = alerts_index["raw_alerts"]

    active_alerts = is_point_in_alert(lat, lon, city_name=city, state_id=state, alerts=alerts)

    has_major_alert = any(a["severity"].lower() in ["severe", "extreme"] for a in active_alerts)

    safe_cities = nearest_safe_city_vectorized(lat, lon, alerts=alerts) if has_major_alert else []

    return {
        "location_inside_alert": bool(active_alerts),
        "active_alerts": active_alerts,
        "nearest_safe_cities": [
            {"name": n, "lat": la, "lon": lo, "distance_km": round(d,2)}
            for n, la, lo, d in safe_cities
        ]
    }
