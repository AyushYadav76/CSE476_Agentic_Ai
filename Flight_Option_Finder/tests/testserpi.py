import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("SERPAPI_KEY")

if not api_key:
    raise ValueError("SERPAPI_KEY not found")

print("API key loaded successfully")

params = {
    "engine": "google_flights",
    "departure_id": "DEL",
    "arrival_id": "BOM",
    "type": "2",                 # 2 = One Way
    "outbound_date": "2026-09-15",
    "currency": "INR",
    "hl": "en",
    "gl": "in",
    "travel_class": "1"
}

response = requests.get(
    "https://serpapi.com/search",
    params={
        **params,
        "api_key": api_key
    },
    timeout=60
)

print("\nHTTP Status:", response.status_code)

data = response.json()

if response.status_code != 200:
    print("\nSerpApi Error:")
    print(data)
else:
    print("\nSearch successful!")

    print("\nNumber of best flights:",
          len(data.get("best_flights", [])))

    for flight in data.get("best_flights", []):
        print(flight)