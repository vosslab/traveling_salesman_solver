#!/usr/bin/env python3

# Standard Library
import random
import time

# PIP3 modules
import openrouteservice
import yaml

#============================================
def load_config(path: str) -> dict:
	"""
	Load configuration from a YAML file.

	Args:
		path: Path to the YAML configuration file.

	Returns:
		Dictionary with configuration values.
	"""
	# open the YAML configuration file
	with open(path, "r", encoding="ascii") as config_file:
		config = yaml.safe_load(config_file)

	# return the configuration dictionary
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
	# create the OpenRouteService client
	client = openrouteservice.Client(key=api_key)

	# return the client object
	return client

# Simple assertion test for make_client
assert callable(make_client)

#============================================
def geocode_address(
	client: openrouteservice.Client,
	address: str,
) -> tuple:
	"""
	Geocode a postal address to longitude and latitude.

	Args:
		client: OpenRouteService Client instance.
		address: Address string.

	Returns:
		Tuple with (longitude, latitude) as floats.
	"""
	# sleep briefly to avoid overloading the API
	time.sleep(random.random())

	# send geocoding request to OpenRouteService
	response = client.pelias_search(
		text=address,
		size=1,
	)

	# extract the first feature and its coordinates
	feature = response["features"][0]
	coordinates = feature["geometry"]["coordinates"]
	longitude = coordinates[0]
	latitude = coordinates[1]

	# return the longitude and latitude
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
	# geocode the home address
	home_longitude, home_latitude = geocode_address(client, home_address)

	# initialize names and coordinates with home at index 0
	names = [home_name]
	coords = [(home_longitude, home_latitude)]

	# iterate over all other locations and geocode them
	for location in locations:
		location_name = location["name"]
		location_address = location["address"]

		# geocode the location address
		location_longitude, location_latitude = geocode_address(
			client,
			location_address,
		)

		# append the location name and coordinates
		names.append(location_name)
		coords.append((location_longitude, location_latitude))

	# return names and coordinates
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
		avoid_highways: If True, request routes that avoid highways.

	Returns:
		Dictionary mapping (i, j) index pairs to duration values in seconds.
	"""
	# set route options, possibly avoiding highways
	options = {}
	if avoid_highways:
		options["avoid_features"] = ["highways"]

	# sleep briefly to avoid overloading the API
	time.sleep(random.random())

	# request a duration matrix from OpenRouteService
	response = client.distance_matrix(
		locations=coords,
		profile="driving-car",
		metrics=["duration"],
		resolve_locations=False,
		optimized=False,
		options=options,
	)

	# extract matrix of durations in seconds
	durations = response["durations"]

	# convert list-of-lists into a dictionary keyed by index pairs
	matrix = {}
	num_points = len(durations)
	for i_index in range(num_points):
		for j_index in range(num_points):
			duration_seconds = durations[i_index][j_index]
			matrix[i_index, j_index] = duration_seconds

	# return the duration matrix dictionary
	return matrix
