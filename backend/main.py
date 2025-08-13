from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient

app = FastAPI()

# Allow React frontend to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["train_db"]
trains_collection = db["trains"]

# Constants
AVG_SPEED_KMPH = 50  # average train speed

# Helper: Calculate price
def calc_price(distance_km: int) -> float:
    return distance_km * 1.25

# Helper: Calculate duration (hours, minutes)
def calc_duration(distance_km: int):
    total_hours = distance_km / AVG_SPEED_KMPH
    hours = int(total_hours)
    minutes = int((total_hours - hours) * 60)
    return hours, minutes

@app.get("/stations")
def get_stations():
    stations = trains_collection.distinct("stops.station")
    return {"stations": stations}

@app.get("/sources")
def get_sources():
    sources = set()
    trains = trains_collection.find()
    for train in trains:
        if train["stops"]:
            sources.add(train["stops"][0]["station"])
    return {"sources": list(sources)}

@app.get("/destinations")
def get_destinations(source: str = Query(...)):
    destinations = set()
    trains = trains_collection.find({"stops.station": source})
    for train in trains:
        stops = train["stops"]
        src_idx = next((i for i, s in enumerate(stops) if s["station"] == source), None)
        if src_idx is not None:
            for stop in stops[src_idx + 1:]:
                destinations.add(stop["station"])
    return {"destinations": list(destinations)}

@app.get("/trains")
def search_trains(source: str = Query(...), destination: str = Query(...)):
    results = []

    # ------------------
    # Direct trains
    # ------------------
    direct_trains = trains_collection.find({
        "stops.station": {"$all": [source, destination]}
    })

    for train in direct_trains:
        stops = train["stops"]
        src_idx = next((i for i, s in enumerate(stops) if s["station"] == source), None)
        dest_idx = next((i for i, s in enumerate(stops) if s["station"] == destination), None)

        if src_idx is not None and dest_idx is not None and src_idx < dest_idx:
            distance = sum(stops[i]["distance"] for i in range(src_idx + 1, dest_idx + 1))
            route_segment = [s["station"] for s in stops[src_idx:dest_idx + 1]]

            hrs, mins = calc_duration(distance)

            results.append({
                "type": "direct",
                "trainName": train["train_name"],
                "start": stops[src_idx]["departure"],
                "end": stops[dest_idx]["departure"],
                "distance": distance,
                "durationHours": hrs,
                "durationMinutes": mins,
                "price": calc_price(distance),
                "route": route_segment
            })

    if results:
        return {"trains": results}

    # ------------------
    # Connecting trains
    # ------------------
    trains_from_source = trains_collection.find({"stops.station": source})

    for train1 in trains_from_source:
        stops1 = train1["stops"]
        src_idx = next((i for i, s in enumerate(stops1) if s["station"] == source), None)

        if src_idx is None:
            continue

        for hub_idx in range(src_idx + 1, len(stops1)):
            hub_station = stops1[hub_idx]["station"]

            trains_from_hub = trains_collection.find({
                "stops.station": {"$all": [hub_station, destination]}
            })

            for train2 in trains_from_hub:
                stops2 = train2["stops"]
                hub_idx2 = next((i for i, s in enumerate(stops2) if s["station"] == hub_station), None)
                dest_idx2 = next((i for i, s in enumerate(stops2) if s["station"] == destination), None)

                if hub_idx2 is not None and dest_idx2 is not None and hub_idx2 < dest_idx2:
                    dist1 = sum(stops1[i]["distance"] for i in range(src_idx + 1, hub_idx + 1))
                    dist2 = sum(stops2[i]["distance"] for i in range(hub_idx2 + 1, dest_idx2 + 1))
                    total_distance = dist1 + dist2

                    hrs, mins = calc_duration(total_distance)

                    route1 = [s["station"] for s in stops1[src_idx:hub_idx + 1]]
                    route2 = [s["station"] for s in stops2[hub_idx2:dest_idx2 + 1]]

                    results.append({
                        "type": "connecting",
                        "firstTrain": train1["train_name"],
                        "secondTrain": train2["train_name"],
                        "hub": hub_station,
                        "start": stops1[src_idx]["departure"],
                        "hub_arrival": stops1[hub_idx]["departure"],
                        "hub_departure": stops2[hub_idx2]["departure"],
                        "end": stops2[dest_idx2]["departure"],
                        "distance": total_distance,
                        "durationHours": hrs,
                        "durationMinutes": mins,
                        "price": calc_price(total_distance),
                        "route": [route1, route2]
                    })

    return {"trains": results}
