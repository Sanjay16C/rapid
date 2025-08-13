# backend/generate_trains_graph.py
import random
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "train_db"
TRAINS_COLLECTION = "trains"
STATIONS_COLLECTION = "stations"

NUM_TRAINS = 1000
RANDOM_SEED = 42

# ----------------------------
# Rail graph (approx distances, km)
# Only these links are allowed when building routes
# ----------------------------
EDGES = {
    # North ↔ West corridor
    ("Delhi", "Jaipur"): 280,
    ("Jaipur", "Ahmedabad"): 650,
    ("Ahmedabad", "Vadodara"): 110,
    ("Vadodara", "Surat"): 130,
    ("Surat", "Thane"): 260,
    ("Thane", "Mumbai"): 25,
    ("Mumbai", "Pune"): 150,
    ("Ahmedabad", "Rajkot"): 215,

    # North ↔ East corridor
    ("Delhi", "Agra"): 210,
    ("Agra", "Lucknow"): 330,
    ("Lucknow", "Varanasi"): 300,
    ("Varanasi", "Patna"): 230,
    ("Patna", "Kolkata"): 560,

    # East coast corridor (Kolkata → Chennai)
    ("Kolkata", "Bhubaneswar"): 440,
    ("Bhubaneswar", "Visakhapatnam"): 440,
    ("Visakhapatnam", "Vijayawada"): 350,
    ("Vijayawada", "Chennai"): 455,
    ("Chennai", "Tirupati"): 135,

    # South spine (West coast ↔ TN)
    ("Mangalore", "Mysuru"): 255,
    ("Mysuru", "Bangalore"): 145,
    ("Bangalore", "Salem"): 200,
    ("Salem", "Erode"): 55,
    ("Erode", "Coimbatore"): 100,
    ("Coimbatore", "Trichy"): 210,
    ("Trichy", "Madurai"): 140,
    ("Tirupati", "Chennai"): 135,  # duplicate reverse for convenience

    # Konkan / West coast extension
    ("Mangalore", "Calicut"): 230,
    ("Calicut", "Thrissur"): 110,
    ("Thrissur", "Kochi"): 80,
    ("Kochi", "Trivandrum"): 220,

    # Deccan + connectors
    ("Nagpur", "Bhopal"): 350,
    ("Bhopal", "Indore"): 190,
    ("Indore", "Vadodara"): 330,
    ("Nagpur", "Hyderabad"): 500,
    ("Hyderabad", "Vijayawada"): 300,

    # Some sensible southern crosslinks
    ("Bangalore", "Mangalore"): 420,
    ("Bangalore", "Coimbatore"): 365,
    ("Chennai", "Salem"): 340,
    ("Chennai", "Vellore"): 140,
    ("Vellore", "Bangalore"): 210,
}

# Make undirected adjacency
from collections import defaultdict, deque

GRAPH = defaultdict(dict)
for (a, b), d in EDGES.items():
    GRAPH[a][b] = d
    GRAPH[b][a] = d

# Stations set
STATIONS = sorted(GRAPH.keys())

# Speeds & dwell
AVG_SPEED_KMPH = 55  # average run speed
DWELL_MIN = (2, 8)   # dwell time at each intermediate stop [min,min]

START_HOUR_MIN = 5
START_HOUR_MAX = 18
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

def generate_train_name(i, used):
    # Nice, readable names with de-duplication
    for _ in range(10):
        name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        if name not in used:
            used.add(name)
            return name
    # fallback with a suffix
    suffix = 2
    while f"{name} {suffix}" in used:
        suffix += 1
    name2 = f"{name} {suffix}"
    used.add(name2)
    return name2

def random_start_time():
    hour = random.randint(START_HOUR_MIN, START_HOUR_MAX)
    minute = random.choice(START_MINUTE_CHOICES)
    return datetime(2000, 1, 1, hour, minute)

def random_walk_path(start, min_len=4, max_len=8):
    """Build a simple path (no repeats) by walking neighbors."""
    target_len = random.randint(min_len, max_len)
    path = [start]
    visited = {start}
    current = start

    while len(path) < target_len:
        neighbors = [n for n in GRAPH[current].keys() if n not in visited]
        if not neighbors:
            break
        nxt = random.choice(neighbors)
        path.append(nxt)
        visited.add(nxt)
        current = nxt
    return path if len(path) >= min_len else None

def build_train_stops_from_path(path):
    """Create stops with per-segment distances and times from the given node path."""
    t = random_start_time()
    stops = []
    for i, station in enumerate(path):
        if i == 0:
            seg_km = 0
        else:
            seg_km = GRAPH[path[i-1]][path[i]]
        stops.append({
            "station": station,
            "distance": seg_km,  # distance from previous station
            "departure": t.strftime("%H:%M"),
        })
        if i < len(path) - 1:
            # run time + dwell at arrival
            run_minutes = int(round(seg_km / AVG_SPEED_KMPH * 60))
            dwell = random.randint(*DWELL_MIN)
            t = t + timedelta(minutes=run_minutes + dwell)
    return stops

def generate_trains(n=NUM_TRAINS):
    random.seed(RANDOM_SEED)

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    trains_col = db[TRAINS_COLLECTION]
    stations_col = db[STATIONS_COLLECTION]

    # Reset (comment if appending is desired)
    trains_col.delete_many({})
    stations_col.delete_many({})

    used_names = set()
    docs = []

    for i in range(n):
        start = random.choice(STATIONS)
        path = None
        # Try a few times to get a decent walk
        for _ in range(8):
            path_try = random_walk_path(start, min_len=4, max_len=8)
            if path_try:
                path = path_try
                break
        if not path:
            continue

        stops = build_train_stops_from_path(path)
        train_name = generate_train_name(i, used_names)
        docs.append({"train_name": train_name, "stops": stops})

    if docs:
        trains_col.insert_many(docs)

    # stations collection for dropdowns
    stations_doc = [{"name": s} for s in sorted(STATIONS)]
    if stations_doc:
        stations_col.insert_many(stations_doc)
        stations_col.create_index([("name", ASCENDING)], unique=True)

    # helpful indexes
    trains_col.create_index([("stops.station", ASCENDING)])
    trains_col.create_index([("train_name", ASCENDING)], unique=True)

    print(f"Inserted {len(docs)} trains into '{DB_NAME}.{TRAINS_COLLECTION}'.")
    print(f"Inserted {len(stations_doc)} stations into '{DB_NAME}.{STATIONS_COLLECTION}'.")

if __name__ == "__main__":
    generate_trains(NUM_TRAINS)
