from typing import List, Tuple
import bisect
from math import inf

Domain = List[int]
DomainOfValidity = List[Domain]
State = Tuple[int]


def weighted_signed_distance(dov: DomainOfValidity, state: State, max_act_values: List[int]) -> float:
    """
    Computes the weighted signed distance of a given state from the domain of values (dov).

    If the state lies inside the admissible values in all dimensions, it returns the minimum
    weighted depth (how deep the state is inside the region). If the state lies outside in any
    dimension, it returns the negative sum of weighted distances from the nearest admissible values.

    @param dov: A list where each element is a sorted list of admissible values for each domain (dimension).
    @param state: A list or tuple of values (one per dimension) representing the state whose distance is being computed.
    @param max_act_values: A list of the maximum values for each dimension.

    @return: The weighted signed distance.
             - Positive = minimum weighted depth (inside all regions)
             - Negative = sum of weighted distances (outside one or more regions)
    """
    weighted_depths = []
    weighted_dists = []

    for admissible_values, s_val, max_act_val in zip(dov, state, max_act_values):
        weight = 1 / (1 + max_act_val)
        pos = bisect.bisect_left(admissible_values, s_val)

        if is_inside_dov(admissible_values, s_val, pos):
            dimension_depth = compute_dimension_depth(admissible_values, s_val, pos, max_act_val)
            weighted_depths.append(weight * dimension_depth)
        else:
            dimension_dist = compute_dimension_dist(admissible_values, s_val, pos)
            weighted_dists.append(weight * dimension_dist)

    if not weighted_dists:
        return min(weighted_depths)

    return -sum(weighted_dists)


def is_inside_dov(admissible_values: Domain, s_val: int, pos: int) -> bool:
    """
    Checks whether a given value s is inside the admissible values for a dimension.

    @param admissible_values: Sorted list of admissible values for a dimension.
    @param s_val: The state value.
    @param pos: Position where s would be inserted to maintain order.

    @return: True if s is inside admissible_values, False otherwise.
    """
    return pos < len(admissible_values) and admissible_values[pos] == s_val


def compute_dimension_depth(admissible_values: Domain, s_val: int, pos: int, max_act_val: int) -> int:
    """
    Computes the distance of the given state from the nearest boundary (gap) within a dimension,
    assuming the state is inside the admissible values.

    @param admissible_values: Sorted list of admissible values for a dimension.
    @param s_val: The state value.
    @param pos: Position of s in admissible_values.
    @param max_act_val: Maximum activity value in this dimension.

    @return: The minimum distance to the nearest gap/boundary.
    """
    left = pos
    while left > 0 and admissible_values[left] - admissible_values[left - 1] == 1:
        left -= 1
    left_gap = s_val - admissible_values[left] if admissible_values[left] != 0 else inf

    right = pos
    while right < len(admissible_values) - 1 and admissible_values[right + 1] - admissible_values[right] == 1:
        right += 1
    right_gap = admissible_values[right] - s_val if admissible_values[right] != max_act_val else inf

    return min(left_gap, right_gap)


def compute_dimension_dist(admissible_values: Domain, s_val: int, pos: int) -> int:
    """
    Computes the distance from a state that lies outside the admissible values
    to the nearest admissible value in a dimension.

    @param admissible_values: Sorted list of admissible values for a dimension.
    @param s_val: The state value.
    @param pos: Position where s would be inserted to maintain order.

    @return: The distance to the nearest admissible value.
    """
    if pos == 0:
        dist = abs(admissible_values[0] - s_val)
    elif pos >= len(admissible_values):
        dist = abs(admissible_values[-1] - s_val)
    else:
        dist = min(
            abs(admissible_values[pos - 1] - s_val),
            abs(admissible_values[pos] - s_val)
        )
    return dist


def find_extreme_state(dov: DomainOfValidity, max_values: List[int], is_inside: bool) -> Tuple[State, float]:
    """
    Finds an extreme state (either the most inside or the furthest outside) and its associated distance.

    If inside=True, finds the state with the maximum depth inside dov.
    If inside=False, finds the state with the maximum distance outside dov.

    @param dov: A list where each element is a sorted list of admissible values for each domain (dimension).
    @param max_values: A list of the maximum values for each dimension.
    @param is_inside: Flag determining if we look for the best inside state or worst outside state.

    @return: A tuple containing:
             - best_state: The state found.
             - total_distance: The associated distance:
                 * Minimum weighted depth if inside=True
                 * Sum of weighted distances if inside=False
    """
    best_state = []
    best_distances = []

    for admissible_values, max_act_val in zip(dov, max_values):
        weight = 1 / (1 + max_act_val)

        full_set = set(range(max_act_val + 1))
        admissible_set = set(admissible_values)
        complement_values = sorted(full_set - admissible_set)

        if is_inside:
            s_val, d_val = find_max_depth_state(admissible_values, admissible_values, max_act_val)
        else:
            s_val, d_val = find_max_dist_state(admissible_values, complement_values)

        best_state.append(s_val)
        best_distances.append(weight * d_val)

    total_distance = min(best_distances) if is_inside else sum(best_distances)
    return tuple(best_state), total_distance


def find_max_depth_state(admissible_values: Domain, candidates: List[int], max_act_val: int) -> Tuple[int, int]:
    """
    Finds the candidate state with the maximum depth (inside region).

    @param admissible_values: Sorted list of admissible values for a dimension.
    @param candidates: List of candidate values to evaluate.
    @param max_act_val: Maximum possible value in this dimension.

    @return: A tuple containing:
             - best_v: The candidate with maximum depth.
             - best_d: The depth value.
    """
    best_v, best_d = None, -inf
    for s in candidates:
        pos = bisect.bisect_left(admissible_values, s)
        contribution = compute_dimension_depth(admissible_values, s, pos, max_act_val)
        if contribution > best_d:
            best_v = s
            best_d = contribution

    return best_v, best_d


def find_max_dist_state(admissible_values: Domain, candidates: List[int]) -> Tuple[int, int]:
    """
    Finds the candidate state with the maximum distance (outside region).

    @param admissible_values: Sorted list of admissible values for a dimension.
    @param candidates: List of candidate values to evaluate.

    @return: A tuple containing:
             - best_v: The candidate with maximum distance.
             - best_d: The distance value.
    """
    best_v, best_d = None, -inf
    for s in candidates:
        pos = bisect.bisect_left(admissible_values, s)
        contribution = compute_dimension_dist(admissible_values, s, pos)
        if contribution > best_d:
            best_v = s
            best_d = contribution

    return best_v, best_d
