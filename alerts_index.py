import time
import requests
from shapely.geometry import shape

CACHE_DURATION = 5 * 60  # 5 minutes
_alert_cache = {"data": None, "timestamp": 0, "index": None}

def load_live_alerts():
    """
    Fetch active alerts from NWS API.
    """
    url = "https://api.weather.gov/alerts/active?status=actual&message_type=alert"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("features", [])
    except Exception as e:
        print("Error fetching alerts:", e)
        return []

def build_alert_index(alerts):
    severe_extreme = set()
    minor_moderate = set()
    polygons = []

    for alert in alerts:
        props = alert["properties"]
        severity = props.get("severity", "Unknown").lower()
        area_desc = props.get("areaDesc", "").lower()
        areas = [a.strip() for a in area_desc.split(";")]

        if severity in ["severe", "extreme"]:
            severe_extreme.update(areas)
        elif severity in ["minor", "moderate"]:
            minor_moderate.update(areas)

        geom = alert.get("geometry")
        if geom:
            try:
                polygons.append((severity, shape(geom)))
            except Exception:
                pass

    # --- FAKE EXTREME ALERT FOR TESTING ---
    fake_alert = {
        "properties": {
            "severity": "Extreme",
            "event": "Test Extreme Alert",
            "areaDesc": "Orlando"
        },
        "geometry": None
    }
    alerts.append(fake_alert)
    severe_extreme.add("orlando")
    fake_alert = {
        "properties": {
            "severity": "Extreme",
            "event": "Test Extreme Alert",
            "areaDesc": "Fremont"
        },
        "geometry": None
    }   
    alerts.append(fake_alert)
    severe_extreme.add("fremont")

    # -------------------------------------

    return {
        "severe_extreme": severe_extreme,
        "minor_moderate": minor_moderate,
        "polygons": polygons,
        "raw_alerts": alerts
    }


def get_alert_index():
    """
    Returns cached alerts and pre-built index.
    """
    now = time.time()
    if _alert_cache["data"] is None or now - _alert_cache["timestamp"] > CACHE_DURATION:
        alerts = load_live_alerts()
        _alert_cache["data"] = alerts
        _alert_cache["index"] = build_alert_index(alerts)
        _alert_cache["timestamp"] = now
    return _alert_cache["index"]
