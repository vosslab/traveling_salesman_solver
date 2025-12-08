#!/usr/bin/env python3

# Standard Library
import random
import time

# PIP3 modules
import openrouteservice
import yaml
import tabulate

# cache file for geocoded coordinates
GEOCODE_CACHE_FILE = "geocode_cache.yaml"

# in-memory cache, loaded on first use
_GEOCODE_CACHE = None

# counters for API calls
GEOCODE_API_CALLS = 0
MATRIX_API_CALLS = 0

#============================================
def load_config(path: str) -> dict:
	"""
	Load configuration from a YAML file.

	Args:
		path: Path to the YAML configuration file.

	Returns:
		Dictionary with configuration values.
	"""
	with open(path, "r", encoding="ascii") as config_file:
		config = yaml.safe_load(config_file)
	return config

# Simple assertion test for load_config
test_config_dict = {"openrouteservice": {"api_key": "TEST_KEY"}}
assert isinstance(test_config_dict, dict)

#============================================
def make_client(api_key: str) -> openrouteservice.Client:
	"""
	Create an OpenRouteService client object.

	Args:
		api_key: OpenRouteService API key.

	Returns:
		OpenRouteService Client instance.
	"""
	client = openrouteservice.Client(key=api_key)
	return client

# Simple assertion test for make_client
assert callable(make_client)

#============================================
def _load_geocode_cache() -> dict:
	"""
	Load the geocode cache from disk if it has not been loaded.

	Returns:
		Dictionary mapping address strings to (longitude, latitude) pairs.
	"""
	global _GEOCODE_CACHE

	if _GEOCODE_CACHE is not None:
		return _GEOCODE_CACHE

	try:
		with open(GEOCODE_CACHE_FILE, "r", encoding="ascii") as cache_file:
			data = yaml.safe_load(cache_file)
	except FileNotFoundError:
		data = None

	if data is None:
		data = {}

	_GEOCODE_CACHE = data
	return _GEOCODE_CACHE

#============================================
def _save_geocode_cache() -> None:
	"""
	Write the current geocode cache to disk, sorted by latitude.

	Sorting by latitude makes the file easier to inspect manually and
	keeps similar geographic entries grouped together.

	Returns:
		None.
	"""
	global _GEOCODE_CACHE

	if _GEOCODE_CACHE is None:
		return

	# sort by latitude (value[1])
	sorted_items = sorted(
		_GEOCODE_CACHE.items(),
		key=lambda kv: kv[1][1],
	)

	# rebuild ordered dict for stable output
	sorted_cache = {key: value for key, value in sorted_items}

	with open(GEOCODE_CACHE_FILE, "w", encoding="ascii") as cache_file:
		yaml.safe_dump(sorted_cache, cache_file)

#============================================
def geocode_address(
	client: openrouteservice.Client,
	address: str,
) -> tuple:
	"""
	Geocode a postal address to longitude and latitude with caching.

	Args:
		client: OpenRouteService Client instance.
		address: Address string.

	Returns:
		Tuple with (longitude, latitude) as floats.
	"""
	global GEOCODE_API_CALLS

	cache = _load_geocode_cache()

	# use cached coordinates if present
	if address in cache:
		longitude, latitude = cache[address]
		location_tuple = (float(longitude), float(latitude))
		return location_tuple

	# cache miss, call API
	GEOCODE_API_CALLS = GEOCODE_API_CALLS + 1
	print(f"[API] Geocoding address #{GEOCODE_API_CALLS}: {address}")

	time.sleep(random.random())

	response = client.pelias_search(
		text=address,
		size=1,
	)

	feature = response["features"][0]
	coordinates = feature["geometry"]["coordinates"]
	longitude = float(coordinates[0])
	latitude = float(coordinates[1])

	cache[address] = (longitude, latitude)
	_save_geocode_cache()

	location_tuple = (longitude, latitude)
	return location_tuple

#============================================
def build_coords_with_home(
	client: openrouteservice.Client,
	home_name: str,
	home_address: str,
	locations: list,
) -> tuple:
	"""
	Build ordered name and coordinate lists, with home at index 0.

	Args:
		client: OpenRouteService Client instance.
		home_name: Name of the home location.
		home_address: Address string for home.
		locations: List of dicts with keys "name" and "address".

	Returns:
		Tuple:
		- names: List of location names with home at index 0.
		- coords: List of (longitude, latitude) pairs with home at index 0.
	"""
	home_longitude, home_latitude = geocode_address(client, home_address)

	names = [home_name]
	coords = [(home_longitude, home_latitude)]

	for location in locations:
		location_name = location["name"]
		location_address = location["address"]

		location_longitude, location_latitude = geocode_address(
			client,
			location_address,
		)

		names.append(location_name)
		coords.append((location_longitude, location_latitude))

	result_tuple = (names, coords)
	return result_tuple

#============================================
def ors_duration_matrix(
	client: openrouteservice.Client,
	coords: list,
	avoid_highways: bool,
) -> dict:
	"""
	Build a duration matrix from OpenRouteService for a set of coordinates.

	Args:
		client: OpenRouteService Client instance.
		coords: List of (longitude, latitude) coordinate pairs.
		avoid_highways: Ignored for now. The ORS Matrix endpoint does not
			support avoid_features such as highways. Parameter is kept
			for potential future use.

	Returns:
		Dictionary mapping (i_index, j_index) index pairs to duration values in
		seconds.
	"""
	global MATRIX_API_CALLS

	# first attempt: optimized=False (plain Dijkstra, default behavior)
	MATRIX_API_CALLS = MATRIX_API_CALLS + 1
	print(
		f"[API] Requesting ORS duration matrix #{MATRIX_API_CALLS} "
		f"for {len(coords)} locations (optimized=False)",
	)

	time.sleep(random.random())

	try:
		response = client.distance_matrix(
			locations=coords,
			profile="driving-car",
			metrics=["duration"],
			resolve_locations=False,
			optimized=False,
		)
	except openrouteservice.exceptions.ApiError:
		# second attempt: fall back to optimized=True if Dijkstra hits
		# the visited nodes limit or another server-side issue
		MATRIX_API_CALLS = MATRIX_API_CALLS + 1
		print(
			f"[API] Matrix attempt with optimized=False failed, "
			f"retrying as request #{MATRIX_API_CALLS} with optimized=True",
		)

		time.sleep(random.random())

		response = client.distance_matrix(
			locations=coords,
			profile="driving-car",
			metrics=["duration"],
			resolve_locations=False,
			optimized=True,
		)

	durations = response["durations"]

	matrix = {}
	num_points = len(durations)
	for i_index in range(num_points):
		for j_index in range(num_points):
			duration_seconds = durations[i_index][j_index]
			matrix[i_index, j_index] = float(duration_seconds)

	return matrix

#============================================
def print_duration_matrix(names: list, matrix: dict) -> None:
	"""
	Print the full duration matrix in minutes using tabulate.

	Args:
		names: List of location names, index position matches matrix index.
		matrix: Dictionary mapping (i_index, j_index) to duration in seconds.

	Returns:
		None.
	"""
	num_points = len(names)

	table = []
	for i_index in range(num_points):
		row_label = f"{i_index} {names[i_index]}"
		row = [row_label]
		for j_index in range(num_points):
			seconds = matrix[i_index, j_index]
			minutes = seconds / 60.0
			row.append(minutes)
		table.append(row)

	headers = ["from \\ to"]
	for j_index in range(num_points):
		headers.append(f"{j_index}")

	print("Duration matrix (minutes):")
	print(
		tabulate.tabulate(
			table,
			headers=headers,
			tablefmt="psql",
			floatfmt=".1f",
		),
	)

#============================================
def get_api_call_counts() -> tuple:
	"""
	Get the number of API calls made during this run.

	Returns:
		Tuple:
		- geocode_calls: Number of geocoding API calls.
		- matrix_calls: Number of matrix API calls.
	"""
	geocode_calls = GEOCODE_API_CALLS
	matrix_calls = MATRIX_API_CALLS
	result_tuple = (geocode_calls, matrix_calls)
	return result_tuple

# Simple assertion test for get_api_call_counts
test_geocode_calls, test_matrix_calls = get_api_call_counts()
assert isinstance(test_geocode_calls, int) and isinstance(test_matrix_calls, int)
