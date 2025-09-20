from fastapi import FastAPI, Query
from logic_no_gpd import is_point_in_alert, nearest_safe_city_vectorized
from alerts_index import get_alert_index

app = FastAPI(title="Weather Safety API")

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
    # Get alerts (includes fake test alert)
    alerts_index = get_alert_index()
    alerts = alerts_index["raw_alerts"]

    # All alerts (any severity) affecting the location
    active_alerts = is_point_in_alert(lat, lon, city_name=city, state_id=state, alerts=alerts)

    # Check if there is any Severe or Extreme alert
    has_major_alert = any(a["severity"].lower() in ["severe", "extreme"] for a in active_alerts)

    # Only skip cities with Severe/Extreme alerts
    safe_cities = nearest_safe_city_vectorized(lat, lon, alerts=alerts) if has_major_alert else []

    return {
        "location_inside_alert": bool(active_alerts),
        "active_alerts": active_alerts,
        "nearest_safe_cities": [
            {"name": n, "lat": la, "lon": lo, "distance_km": round(d,2)}
            for n, la, lo, d in safe_cities
        ]
    }
