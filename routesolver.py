#!/usr/bin/env python3

# Standard Library
import random

#============================================
def all_pairs(size: int, shuffle=random.shuffle):
	"""
	Generate index pairs for a sequence of the given size.

	Args:
		size: Length of the sequence.
		shuffle: Function to shuffle index order, or None for deterministic order.

	Returns:
		Generator that yields (i_index, j_index) index pairs.
	"""
	r1 = list(range(size))
	r2 = list(range(size))

	if shuffle:
		shuffle(r1)
		shuffle(r2)

	for i_index in r1:
		for j_index in r2:
			yield (i_index, j_index)

# Simple assertion test for all_pairs
pairs_test = list(all_pairs(3, shuffle=None))
assert (0, 0) in pairs_test and (2, 2) in pairs_test

#============================================
def reversed_sections(tour: list):
	"""
	Generate tours where sections between two cities are reversed.

	Args:
		tour: List of city indices representing a tour.

	Returns:
		Generator that yields modified tours with reversed sections.
	"""
	for i_index, j_index in all_pairs(len(tour)):
		if i_index < j_index:
			copy_tour = tour[:]
			copy_tour[i_index:j_index + 1] = reversed(
				tour[i_index:j_index + 1],
			)
			if copy_tour != tour:
				yield copy_tour

#============================================
def shift_cities(tour: list):
	"""
	Generate tours where a single city is shifted to a new position.

	Args:
		tour: List of city indices representing a tour.

	Returns:
		Generator that yields modified tours with shifted cities.
	"""
	num_cities = len(tour)

	for i_index in range(num_cities):
		for j_index in range(num_cities):
			if i_index == j_index:
				continue

			copy_tour = tour[:]
			city = copy_tour.pop(i_index)

			if j_index > i_index:
				insert_index = j_index - 1
			else:
				insert_index = j_index

			copy_tour.insert(insert_index, city)
			yield copy_tour

#============================================
def tour_length_cycle(matrix: dict, tour: list) -> float:
	"""
	Compute total cycle length for a tour based on a matrix of costs.

	Args:
		matrix: Dictionary mapping (i_index, j_index) to travel cost.
		tour: List of city indices representing a cycle.

	Returns:
		Total cost of the tour as a float.
	"""
	total_cost = 0.0
	num_cities = len(tour)

	for i_index in range(num_cities):
		j_index = (i_index + 1) % num_cities
		city_i = tour[i_index]
		city_j = tour[j_index]
		edge_cost = matrix[city_i, city_j]
		total_cost = total_cost + edge_cost

	return total_cost

# Simple assertion test for tour_length_cycle
test_matrix = {
	(0, 1): 1.0,
	(1, 0): 1.0,
}
assert tour_length_cycle(test_matrix, [0, 1]) == 2.0

#============================================
def hillclimb(
	init_function,
	move_operator,
	objective_function,
	max_evaluations: int,
) -> tuple:
	"""
	Run a single hillclimbing search.

	Args:
		init_function: Function that creates an initial tour.
		move_operator: Function that generates neighbor tours.
		objective_function: Function that maps a tour to a score.
		max_evaluations: Maximum number of objective evaluations.

	Returns:
		Tuple:
		- num_evaluations: Number of objective evaluations performed.
		- best_score: Best objective score found.
		- best_tour: Best tour found.
	"""
	best_tour = init_function()
	best_score = objective_function(best_tour)
	num_evaluations = 1

	while num_evaluations < max_evaluations:
		move_made = False

		for candidate_tour in move_operator(best_tour):
			if num_evaluations >= max_evaluations:
				break

			candidate_score = objective_function(candidate_tour)
			num_evaluations = num_evaluations + 1

			if candidate_score > best_score:
				best_tour = candidate_tour
				best_score = candidate_score
				move_made = True
				break

		if not move_made:
			break

	result_tuple = (num_evaluations, best_score, best_tour)
	return result_tuple

#============================================
def hillclimb_and_restart(
	init_function,
	move_operator,
	objective_function,
	max_iterations: int,
	max_evaluations: int,
) -> tuple:
	"""
	Run repeated hillclimbs with restarts.

	Args:
		init_function: Function that creates an initial tour.
		move_operator: Function that generates neighbor tours.
		objective_function: Function that maps a tour to a score.
		max_iterations: Maximum number of hillclimb runs.
		max_evaluations: Maximum evaluations per hillclimb run.

	Returns:
		Tuple:
		- total_evaluations: Total number of objective evaluations.
		- best_score: Best objective score found across all runs.
		- best_tour: Best tour found across all runs.
	"""
	best_tour = None
	best_score = float("-inf")
	total_evaluations = 0

	for iteration_index in range(max_iterations):
		evaluations, score, tour = hillclimb(
			init_function,
			move_operator,
			objective_function,
			max_evaluations,
		)
		total_evaluations = total_evaluations + evaluations

		if best_tour is None or score > best_score:
			best_tour = tour
			best_score = score

	result_tuple = (total_evaluations, best_score, best_tour)
	return result_tuple

#============================================
def normalize_home_first(tour: list, home: int) -> list:
	"""
	Rotate a tour so that the home index appears first.

	Args:
		tour: List of city indices representing a cycle.
		home: City index that represents the home location.

	Returns:
		New tour list with home at index 0.
	"""
	home_index = tour.index(home)
	rotated = tour[home_index:] + tour[:home_index]
	return rotated

# Simple assertion test for normalize_home_first
assert normalize_home_first([2, 0, 1], 0) == [0, 1, 2]

#============================================
def solve_tsp_hillclimb(
	matrix: dict,
	max_iter: int,
	max_eval: int,
) -> list:
	"""
	Solve a TSP-like routing problem using hillclimb with restarts.

	Args:
		matrix: Dictionary mapping (i_index, j_index) to travel cost.
		max_iter: Number of hillclimb restarts.
		max_eval: Maximum evaluations per hillclimb run.

	Returns:
		List of city indices representing a tour that starts and ends at home.
	"""
	city_indices = {i_index for (i_index, _) in matrix.keys()}
	num_cities = len(city_indices)

	def init_tour():
		"""
		Create a random tour visiting all cities once.

		Returns:
			List of city indices representing a tour.
		"""
		tour = list(range(num_cities))
		random.shuffle(tour)
		return tour

	def fitness(tour: list) -> float:
		"""
		Compute objective score for a tour.

		Args:
			tour: List of city indices.

		Returns:
			Negative tour cost as a float.
		"""
		cost = tour_length_cycle(matrix, tour)
		score = -cost
		return score

	_, score_stage_one, best_tour = hillclimb_and_restart(
		init_tour,
		reversed_sections,
		fitness,
		max_iter,
		max_eval,
	)

	def init_best():
		"""
		Return a copy of the best tour found so far.

		Returns:
			List of city indices representing a tour.
		"""
		tour_copy = best_tour[:]
		return tour_copy

	_, score_stage_two, improved_tour = hillclimb_and_restart(
		init_best,
		shift_cities,
		fitness,
		2,
		max_eval,
	)

	if score_stage_two > score_stage_one:
		final_tour_base = improved_tour
	else:
		final_tour_base = best_tour

	final_tour = normalize_home_first(final_tour_base, 0)

	if final_tour[-1] != 0:
		final_tour.append(0)

	return final_tour

#============================================
def compute_reverse_cycle(tour: list) -> list:
	"""
	Compute the fully reversed cycle for a tour starting and ending at home.

	Args:
		tour: List of city indices, for example [0, 3, 2, 1, 0].

	Returns:
		Reversed tour list such as [0, 1, 2, 3, 0].
	"""
	inner = tour[:-1]
	home_index = inner[0]
	remainder = inner[1:]
	rev_remainder = list(reversed(remainder))

	reverse_tour = [home_index]
	reverse_tour.extend(rev_remainder)
	reverse_tour.append(home_index)

	return reverse_tour

# Simple assertion test for compute_reverse_cycle
assert compute_reverse_cycle([0, 1, 2, 0]) == [0, 2, 1, 0]
