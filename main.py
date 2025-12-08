#!/usr/bin/env python3

# Standard Library
import argparse

# PIP3 modules
import yaml

# local repo modules
import openroute
import routesolver

# simple ANSI color codes for terminal output
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[32m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"
COLOR_MAGENTA = "\033[35m"

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
	openroute.print_duration_matrix(names, matrix)

	tour = routesolver.solve_tsp_hillclimb(
		matrix,
		args.max_iter,
		args.max_eval,
	)

	total_seconds = routesolver.tour_length_cycle(matrix, tour)
	total_minutes = total_seconds / 60.0

	# print forward route with per-leg details
	print(f"{COLOR_BOLD}{COLOR_GREEN}Best route (forward):{COLOR_RESET}")
	for step_index in range(len(tour) - 1):
		i_index = tour[step_index]
		j_index = tour[step_index + 1]
		leg_seconds = matrix[i_index, j_index]
		leg_minutes = leg_seconds / 60.0
		print(
			f"  {i_index:2d} {names[i_index]} -> "
			f"{j_index:2d} {names[j_index]}: "
			f"{leg_minutes:.1f} minutes",
		)

	print(
		f"{COLOR_CYAN}Forward route total travel time: "
		f"{total_minutes:.1f} minutes{COLOR_RESET}",
	)

	# compute and report reverse route with per-leg details
	reverse_tour = routesolver.compute_reverse_cycle(tour)
	reverse_seconds = routesolver.tour_length_cycle(matrix, reverse_tour)
	reverse_minutes = reverse_seconds / 60.0

	print(f"{COLOR_BOLD}{COLOR_MAGENTA}Reverse route:{COLOR_RESET}")
	for step_index in range(len(reverse_tour) - 1):
		i_index = reverse_tour[step_index]
		j_index = reverse_tour[step_index + 1]
		leg_seconds = matrix[i_index, j_index]
		leg_minutes = leg_seconds / 60.0
		print(
			f"  {i_index:2d} {names[i_index]} -> "
			f"{j_index:2d} {names[j_index]}: "
			f"{leg_minutes:.1f} minutes",
		)

	print(
		f"{COLOR_CYAN}Reverse route total travel time: "
		f"{reverse_minutes:.1f} minutes{COLOR_RESET}",
	)

	# report API call counts
	geocode_calls, matrix_calls = openroute.get_api_call_counts()
	total_calls = geocode_calls + matrix_calls

	print(f"{COLOR_BOLD}{COLOR_YELLOW}API call summary:{COLOR_RESET}")
	print(f"  Geocoding calls: {geocode_calls}")
	print(f"  Matrix calls:    {matrix_calls}")
	print(f"  Total API calls: {total_calls}")

#============================================
if __name__ == "__main__":
	main()
