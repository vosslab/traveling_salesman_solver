# openroute.py

import csv
import yaml
import openrouteservice as ors


def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_locations(csv_path):
    """Read locations from CSV into a list of dicts."""
    locations = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append({"name": row["name"], "address": row["address"]})
    return locations


def make_client(api_key):
    return ors.Client(key=api_key)


def geocode_address(client, address):
    """Return (lon, lat) for a postal address using ORS search."""
    resp = client.pelias_search(text=address, size=1)
    feat = resp["features"][0]
    lon, lat = feat["geometry"]["coordinates"]
    return lon, lat


def build_coords_with_home(client, config, locations):
    """Return names list and coords list with home at index 0."""
    home_name = config["home"]["name"]
    home_addr = config["home"]["address"]

    home_lon, home_lat = geocode_address(client, home_addr)

    names = [home_name]
    coords = [(home_lon, home_lat)]

    for loc in locations:
        lon, lat = geocode_address(client, loc["address"])
        coords.append((lon, lat))
        names.append(loc["name"])

    return names, coords


def ors_duration_matrix(client, coords, avoid_highways=False):
    """Call ORS matrix API and return matrix[(i, j)] in seconds."""
    options = {}
    if avoid_highways:
        options["avoid_features"] = ["highways"]

    resp = client.distance_matrix(
        locations=coords,
        profile="driving-car",
        metrics=["duration"],
        resolve_locations=False,
        optimized=False,
        options=options,
    )

    durations = resp["durations"]
    matrix = {}
    n = len(durations)
    for i in range(n):
        for j in range(n):
            matrix[i, j] = durations[i][j]
    return matrix
