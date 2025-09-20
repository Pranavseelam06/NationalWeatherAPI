import json

with open("data/alerts.geojson") as f:
    data = json.load(f)

print(data)
