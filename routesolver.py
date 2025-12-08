# routesolver.py

import random


def all_pairs(size, shuffle=random.shuffle):
    r1 = list(range(size))
    r2 = list(range(size))
    if shuffle:
        shuffle(r1)
        shuffle(r2)
    for i in r1:
        for j in r2:
            yield (i, j)


def reversed_sections(tour):
    for i, j in all_pairs(len(tour)):
        if i != j:
            copy = tour[:]
            if i < j:
                copy[i:j+1] = reversed(tour[i:j+1])
            else:
                copy[i+1:] = reversed(tour[:j])
                copy[:j] = reversed(tour[i+1:])
            if copy != tour:
                yield copy


def shift_cities(tour):
    for i, j in all_pairs(len(tour)):
        if i != j:
            copy = tour[0:i]
            copy.extend(tour[i+1:j])
            copy.append(tour[i])
            copy.extend(tour[j:len(tour)])
            yield copy


def tour_length_cycle(matrix, tour):
    total = 0.0
    n = len(tour)
    for i in range(n):
        j = (i + 1) % n
        total += matrix[tour[i], tour[j]]
    return total


def hillclimb(init_function, move_operator, objective_function, max_evaluations):
    best = init_function()
    best_score = objective_function(best)
    num_evaluations = 1

    while num_evaluations < max_evaluations:
        move_made = False
        for candidate in move_operator(best):
            if num_evaluations >= max_evaluations:
                break
            score = objective_function(candidate)
            num_evaluations += 1
            if score > best_score:
                best = candidate
                best_score = score
                move_made = True
                break
        if not move_made:
            break
    return num_evaluations, best_score, best


def hillclimb_and_restart(init_function, move_operator,
                          objective_function, max_iterations, max_evaluations):
    best = None
    best_score = float("-inf")
    total_evals = 0

    for _ in range(max_iterations):
        evals, score, found = hillclimb(
            init_function, move_operator, objective_function, max_evaluations
        )
        total_evals += evals
        if best is None or score > best_score:
            best = found
            best_score = score

    return total_evals, best_score, best


def normalize_home_first(tour, home=0):
    """Rotate the cycle so that home is first."""
    idx = tour.index(home)
    rotated = tour[idx:] + tour[1:idx+1]
    return rotated


def solve_tsp_hillclimb(matrix, max_iter=5, max_eval=50000):
    """Return a tour list like [0, 3, 2, 1, 0]."""
    n = len({i for (i, _) in matrix.keys()})

    def init_tour():
        t = list(range(n))
        random.shuffle(t)
        return t

    fitness = lambda tour: -tour_length_cycle(matrix, tour)

    _, score1, best = hillclimb_and_restart(
        init_tour, reversed_sections, fitness, max_iter, max_eval
    )

    def init_best():
        return best[:]

    _, score2, best2 = hillclimb_and_restart(
        init_best, shift_cities, fitness, 2, max_eval
    )

    if score2 > score1:
        best = best2

    best = normalize_home_first(best, home=0)
    if best[-1] != 0:
        best.append(0)
    return best
