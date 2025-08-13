
import random
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
from collections import defaultdict

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "train_db"
TRAINS_COLLECTION = "trains"
STATIONS_COLLECTION = "stations"

NUM_TRAINS = 1000
RANDOM_SEED = 42

CUSTOM_TRAIN_NAMES = []  

STATIONS = [
    "Delhi", "Agra", "Jaipur", "Lucknow", "Varanasi", "Patna", "Kolkata",
    "Ranchi", "Bhubaneswar", "Visakhapatnam",
    "Mumbai", "Thane", "Pune", "Surat", "Vadodara", "Ahmedabad", "Rajkot",
    "Nagpur", "Bhopal", "Indore",
    "Hyderabad", "Vijayawada",
    "Bangalore", "Mysuru", "Mangalore", "Hubli", "Belagavi",
    "Chennai", "Tirupati", "Vellore", "Coimbatore", "Salem", "Erode", "Trichy", "Madurai",
    "Kochi", "Thrissur", "Calicut", "Trivandrum",
]

CORRIDORS = [
    # North–West–West Coast
    ["Delhi", "Jaipur", "Ahmedabad", "Surat", "Mumbai", "Thane", "Pune"],
    # North–Central–West
    ["Delhi", "Agra", "Gwalior", "Bhopal", "Indore", "Vadodara", "Ahmedabad"],
    # North–East
    ["Delhi", "Agra", "Lucknow", "Varanasi", "Patna", "Kolkata"],
    # East Coast (North → South)
    ["Kolkata", "Bhubaneswar", "Visakhapatnam", "Vijayawada", "Chennai", "Tirupati"],
    # South Spine (West Coast ↔ South TN/Kerala)
    ["Mangalore", "Mysuru", "Bangalore", "Salem", "Erode", "Coimbatore", "Trichy", "Madurai", "Tirupati", "Chennai"],
    # Konkan & West Coast
    ["Mumbai", "Thane", "Surat", "Vadodara", "Ahmedabad", "Rajkot"],
    # Deccan
    ["Nagpur", "Bhopal", "Indore", "Vadodara", "Surat", "Mumbai"],
    # Hyderabad connectors
    ["Hyderabad", "Vijayawada", "Chennai", "Tirupati"],
    ["Hyderabad", "Nagpur", "Bhopal", "Indore"],
    # Karnataka–Goa–Konkan-ish
    ["Belagavi", "Hubli", "Bangalore", "Mysuru", "Mangalore"],
]

# Probability to pick a corridor vs a random path
PICK_CORRIDOR_PROB = 0.75
MIN_STOPS = 4
MAX_STOPS = 8

# Segment distance/time ranges
MIN_SEG_KM = 50
MAX_SEG_KM = 300
MIN_SEG_MIN = 60
MAX_SEG_MIN = 240

# First departure window (start of the route)
START_HOUR_MIN = 5   # 05:00
START_HOUR_MAX = 18  # up to 18:00 so longer trains still finish same day
START_MINUTE_CHOICES = [0, 10, 20, 30, 40, 50]


ADJECTIVES = [
    "Viper", "Crimson", "Golden", "Silver", "Emerald", "Sapphire", "Ruby",
    "Coral", "Ivory", "Amber", "Indigo", "Pearl", "Scarlet", "Titan", "Rapid",
    "Royal", "Eastern", "Western", "Northern", "Southern"
]
NOUNS = [
    "Express", "Mail", "Link", "Shatabdi", "Duronto", "Jan Shatabdi",
    "Superfast", "Intercity", "Rajdhani", "Garib Rath", "Vande Bharat"
]

def generate_train_name(i, used_names):
    if CUSTOM_TRAIN_NAMES:
        name = CUSTOM_TRAIN_NAMES[i % len(CUSTOM_TRAIN_NAMES)]
        if name in used_names:
            suffix = 2
            while f"{name} {suffix}" in used_names:
                suffix += 1
            name = f"{name} {suffix}"
        used_names.add(name)
        return name

   
    attempt = 0
    while True:
        adj = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        name = f"{adj} {noun}"
        if name not in used_names:
            used_names.add(name)
            return name
        attempt += 1
        if attempt > 5:
            numbered = f"{name} {random.randint(2, 999)}"
            if numbered not in used_names:
                used_names.add(numbered)
                return numbered

def random_start_time():
    hour = random.randint(START_HOUR_MIN, START_HOUR_MAX)
    minute = random.choice(START_MINUTE_CHOICES)
    return datetime(2000, 1, 1, hour, minute)  # fixed date, only time is relevant

def build_route_from_corridor():
    corridor = random.choice(CORRIDORS)
    if len(corridor) < MIN_STOPS:
        length = len(corridor)
        start_idx = 0
        end_idx = length
    else:
        length = random.randint(MIN_STOPS, min(MAX_STOPS, len(corridor)))
        start_idx = random.randint(0, len(corridor) - length)
        end_idx = start_idx + length
    return corridor[start_idx:end_idx]

def build_route_random():
    length = random.randint(MIN_STOPS, min(MAX_STOPS, len(STATIONS)))
    route = random.sample(STATIONS, length)
    route.sort()
    return route

def build_train_stops(route):
    current = random_start_time()
    stops = []
    for i, station in enumerate(route):
        distance = 0 if i == 0 else random.randint(MIN_SEG_KM, MAX_SEG_KM)
        stops.append({
            "station": station,
            "distance": distance,         
            "departure": current.strftime("%H:%M"),
        })
        # Advance time for next segment
        seg_minutes = random.randint(MIN_SEG_MIN, MAX_SEG_MIN)
        current += timedelta(minutes=seg_minutes)
    return stops

def generate_trains(n=NUM_TRAINS):
    random.seed(RANDOM_SEED)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    trains_col = db[TRAINS_COLLECTION]
    stations_col = db[STATIONS_COLLECTION]

    # Clean old data (comment these two lines if you want to append instead)
    trains_col.delete_many({})
    stations_col.delete_many({})

    used_names = set()
    docs = []

    for i in range(n):
        if random.random() < PICK_CORRIDOR_PROB:
            route = build_route_from_corridor()
        else:
            route = build_route_random()

        # Ensure route has unique stations (it should already) and length >= MIN_STOPS
        route = list(dict.fromkeys(route))  # preserve order, drop dupes
        if len(route) < MIN_STOPS:
            # If too short due to dupes, top up from stations not in route
            candidates = [s for s in STATIONS if s not in route]
            random.shuffle(candidates)
            needed = MIN_STOPS - len(route)
            route.extend(candidates[:needed])

        stops = build_train_stops(route)
        train_name = generate_train_name(i, used_names)
        docs.append({"train_name": train_name, "stops": stops})

    if docs:
        trains_col.insert_many(docs)

    # Build stations collection (for dropdowns)
    station_set = set()
    for d in docs:
        for st in d["stops"]:
            station_set.add(st["station"])
    stations_doc = [{"name": s} for s in sorted(station_set)]
    if stations_doc:
        stations_col.insert_many(stations_doc)
        stations_col.create_index([("name", ASCENDING)], unique=True)

    # Helpful indexes for performance
    trains_col.create_index([("stops.station", ASCENDING)])
    trains_col.create_index([("train_name", ASCENDING)], unique=True)

    print(f"Inserted {len(docs)} trains into '{DB_NAME}.{TRAINS_COLLECTION}'.")
    print(f"Inserted {len(stations_doc)} stations into '{DB_NAME}.{STATIONS_COLLECTION}'.")


if __name__ == "__main__":
    generate_trains(NUM_TRAINS)
