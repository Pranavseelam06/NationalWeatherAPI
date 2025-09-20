import pandas as pd
import numpy as np
from shapely.geometry import shape, Point
from alerts_index import get_alert_index

# ----------------------------
# Load US cities CSV
# ----------------------------
cities_df = pd.read_csv("data/cities.csv", usecols=["city", "state_id", "county_name", "lat", "lng"])
cities_df.rename(columns={"city": "name", "lng": "lon"}, inplace=True)

city_lats = cities_df["lat"].to_numpy()
city_lons = cities_df["lon"].to_numpy()
city_names = cities_df["name"].to_numpy()
city_states = cities_df["state_id"].to_numpy()
city_counties = cities_df["county_name"].to_numpy()

city_to_county = {
    f"{row['name'].strip().lower()},{row['state_id'].strip().lower()}": row['county_name'].strip().lower()
    for _, row in cities_df.iterrows()
}

# ----------------------------
# Check if a point is inside alerts
# ----------------------------
def is_point_in_alert(lat, lon, city_name=None, state_id=None, alerts=None, severities=None):
    """
    Returns a list of alerts affecting the given point/city.
    Only considers alerts with severity in `severities` if provided.
    """
    if alerts is None:
        alerts = get_alert_index()["raw_alerts"]

    if severities:
        severities = [s.lower() for s in severities]

    point = Point(lon, lat)
    active_alerts = []

    city_county = None
    if city_name and state_id:
        city_key = f"{city_name.strip().lower()},{state_id.strip().lower()}"
        city_county = city_to_county.get(city_key)

    for feature in alerts:
        severity = feature["properties"].get("severity", "Unknown").lower()

        if severities and severity not in severities:
            continue  # ignore alerts outside desired severities

        geom = feature.get("geometry")
        in_alert = False

        # Polygon check
        if geom:
            try:
                poly = shape(geom)
                if poly.contains(point):
                    in_alert = True
            except Exception:
                pass

        # Fallback: areaDesc matching
        if not in_alert:
            area = feature["properties"].get("areaDesc", "")
            areas = [a.strip().lower() for a in area.split(";")]

            if city_name:
                city_lower = city_name.strip().lower()
                for a in areas:
                    if city_lower in a or a in city_lower:
                        in_alert = True
                        break

            if not in_alert and city_county:
                for a in areas:
                    if city_county in a or a in city_county:
                        in_alert = True
                        break

        if in_alert:
            active_alerts.append({
                "type": feature["properties"].get("event"),
                "severity": feature["properties"].get("severity")
            })

    return active_alerts

# ----------------------------
# Vectorized nearest safe cities
# ----------------------------
def nearest_safe_city_vectorized(user_lat, user_lon, max_km=500, alerts=None, max_results=1):
    if alerts is None:
        alerts = get_alert_index()["raw_alerts"]

    lat1 = np.radians(user_lat)
    lon1 = np.radians(user_lon)
    lat2 = np.radians(city_lats)
    lon2 = np.radians(city_lons)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distances = 6371 * c

    mask = distances <= max_km
    filtered_indices = np.where(mask)[0]

    safe_cities = []
    for i in filtered_indices:
        state = city_states[i]
        city = city_names[i].strip()
        county = city_to_county.get(f"{city.lower()},{state.strip().lower()}", "").strip()

        # Only consider Severe/Extreme as unsafe
        city_alerts = is_point_in_alert(
            city_lats[i],
            city_lons[i],
            city_name=city,
            state_id=state,
            alerts=alerts,
            severities=["severe", "extreme"]
        )
        if city_alerts:
            continue  # skip unsafe

        safe_cities.append((city_names[i], city_lats[i], city_lons[i], distances[i]))

    safe_cities.sort(key=lambda x: x[3])
    return safe_cities[:max_results]
