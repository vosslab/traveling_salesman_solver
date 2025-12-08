#!/usr/bin/env python3

# Standard Library
import argparse

# PIP3 modules
import yaml

# local repo modules
import openroute
import routesolver

#============================================
def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.

	Returns:
		Parsed arguments namespace.
	"""
	parser = argparse.ArgumentParser(
		description="Errand route planner using OpenRouteService and TSP hillclimb",
	)
	parser.add_argument(
		"-c",
		"--config",
		dest="config_file",
		required=True,
		help="YAML configuration file with OpenRouteService API key",
	)
	parser.add_argument(
		"-l",
		"--locations",
		dest="locations_file",
		required=True,
		help="YAML file with home and locations",
	)
	parser.add_argument(
		"-a",
		"--avoid-highways",
		dest="avoid_highways",
		help="Request routes that avoid highways",
		action="store_true",
	)
	parser.add_argument(
		"-i",
		"--max-iter",
		dest="max_iter",
		type=int,
		default=5,
		help="Number of hillclimb restarts",
	)
	parser.add_argument(
		"-e",
		"--max-eval",
		dest="max_eval",
		type=int,
		default=50000,
		help="Maximum evaluations per restart",
	)
	args = parser.parse_args()
	return args

#============================================
def load_locations_yaml(path: str) -> tuple:
	"""
	Load home and locations from a YAML file.

	The YAML is expected to have:
	home: <address string>
	locations:
	  - Name1: Address1
	  - Name2: Address2

	Args:
		path: Path to YAML file.

	Returns:
		Tuple:
		- home_name: Name used for the home location.
		- home_address: Address string for home.
		- locations: List of dicts with keys "name" and "address".
	"""
	with open(path, "r", encoding="ascii") as yaml_file:
		data = yaml.safe_load(yaml_file)

	home_address = data["home"]
	home_name = "Home"

	locations = []
	for entry in data.get("locations", []):
		for location_name, location_address in entry.items():
			location_dict = {
				"name": location_name,
				"address": location_address,
			}
			locations.append(location_dict)

	return home_name, home_address, locations

#============================================
def main() -> None:
	"""
	Main entry point.

	Loads configuration and locations, builds duration matrix,
	runs route solver, and prints the best errand route.
	"""
	args = parse_args()

	config = openroute.load_config(args.config_file)
	api_key = config["openrouteservice"]["api_key"]

	client = openroute.make_client(api_key)

	home_name, home_address, locations = load_locations_yaml(
		args.locations_file,
	)

	names, coords = openroute.build_coords_with_home(
		client,
		home_name,
		home_address,
		locations,
	)

	matrix = openroute.ors_duration_matrix(
		client,
		coords,
		args.avoid_highways,
	)

	tour = routesolver.solve_tsp_hillclimb(
		matrix,
		args.max_iter,
		args.max_eval,
	)

	total_seconds = routesolver.tour_length_cycle(matrix, tour)
	total_minutes = total_seconds / 60.0

	print("Best route:")
	for index in tour:
		print(f"{index:2d}  {names[index]}")
	print(f"Total travel time: {total_minutes:.1f} minutes")

#============================================
if __name__ == "__main__":
	main()
