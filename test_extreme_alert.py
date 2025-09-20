# test_extreme_alert.py
import time
from alerts_index import get_alert_index
from logic_no_gpd import is_point_in_alert, nearest_safe_city_vectorized

# --- Step 1: Add a fake extreme alert for testing ---
alerts_index = get_alert_index()
alerts = alerts_index["raw_alerts"]

# Add Extreme alert for Orlando (or any city)
fake_alert = {
    "properties": {
        "severity": "Extreme",
        "event": "Test Extreme Alert",
        "areaDesc": "Orlando"
    },
    "geometry": None  # optional polygon
}
alerts.append(fake_alert)

# --- Step 2: Test if Orlando is in alert ---
active_alerts = is_point_in_alert(28.5383, -81.3792, city_name="Orlando", state_id="FL", alerts=alerts)
print("Active Alerts for Orlando:", active_alerts)

# --- Step 3: Find nearby safe cities ---
safe_cities = nearest_safe_city_vectorized(28.5383, -81.3792, max_km=200, alerts=alerts)
print("Nearby Safe Cities:", safe_cities)