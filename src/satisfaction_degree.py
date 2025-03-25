from bisect import bisect_left
from typing import List, Tuple
from math import inf
from src.custom_types import DomainType, DomainOfValidityType, StateType


def weighted_signed_distance(dov: DomainOfValidityType, state: StateType, max_act_values: List[int]) -> float:
    """
    Computes the weighted signed distance of a state from the domain of admissible values.

    - If the state is inside the admissible region in all dimensions, returns the minimum weighted depth.
    - If the state is outside in any dimension, returns the negative sum of weighted distances from the nearest admissible values.

    @param dov: List of sorted lists, where each sublist contains the admissible values for a dimension.
    @param state: A tuple or list representing the state (one value per dimension).
    @param max_act_values: List of maximum possible values for each dimension.

    @return: Weighted signed distance:
             - Positive → Minimum weighted depth (state is inside).
             - Negative → Sum of weighted distances (state is outside).
    """
    weighted_depths = []
    weighted_dists = []

    for admissible_values, s_val, max_act_val in zip(dov, state, max_act_values):
        weight = 1 / (1 + max_act_val)
        pos = bisect_left(admissible_values, s_val)

        if is_inside_dov(admissible_values, s_val, pos):
            weighted_depths.append(weight * compute_dimension_depth(admissible_values, s_val, pos, max_act_val))
        else:
            weighted_dists.append(weight * compute_dimension_dist(admissible_values, s_val, pos))

    return min(weighted_depths) if not weighted_dists else -sum(weighted_dists)


def is_inside_dov(admissible_values: DomainType, s_val: int, pos: int) -> bool:
    """
    Checks if a state value is inside the admissible range for a dimension.

    @param admissible_values: Sorted list of admissible values for the dimension.
    @param s_val: The state value.
    @param pos: Index where s_val would be inserted in admissible_values.

    @return: True if s_val is inside, False otherwise.
    """
    return pos < len(admissible_values) and admissible_values[pos] == s_val


def compute_dimension_depth(admissible_values: DomainType, s_val: int, pos: int, max_act_val: int) -> int:
    """
    Computes how deep a state is inside the admissible range in a given dimension.

    @param admissible_values: Sorted list of admissible values.
    @param s_val: The state value.
    @param pos: Position of s_val in admissible_values.
    @param max_act_val: Maximum possible value in this dimension.

    @return: Minimum distance to the nearest boundary (gap).
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


def compute_dimension_dist(admissible_values: DomainType, s_val: int, pos: int) -> int:
    """
    Computes the shortest distance from a state outside the admissible region to the nearest valid value.

    @param admissible_values: Sorted list of admissible values.
    @param s_val: The state value.
    @param pos: Index where s_val would be inserted.

    @return: Distance to the closest admissible value.
    """
    if pos == 0:
        return abs(admissible_values[0] - s_val)
    if pos >= len(admissible_values):
        return abs(admissible_values[-1] - s_val)
    return min(abs(admissible_values[pos - 1] - s_val), abs(admissible_values[pos] - s_val))


def find_extreme_state(dov: DomainOfValidityType, max_values: List[int], is_inside: bool) -> Tuple[StateType, float]:
    """
    Finds an extreme state—either the most deeply inside or the farthest outside the Domain of Validity.

    @param dov: List of sorted lists, each containing the admissible values for a dimension.
    @param max_values: List of maximum possible values for each dimension.
    @param is_inside: If True, finds the state with the maximum depth inside.
                      If False, finds the state with the maximum distance outside.

    @return: Tuple containing:
             - best_state: The identified state.
             - total_distance: Depth if inside=True, distance if inside=False.
    """
    best_state = []
    best_distances = []

    for admissible_values, max_act_val in zip(dov, max_values):
        weight = 1 / (1 + max_act_val)

        full_set = set(range(max_act_val + 1))
        admissible_set = set(admissible_values)
        complement_values = sorted(full_set - admissible_set)

        s_val, d_val = (
            find_max_depth_state(admissible_values, admissible_values, max_act_val)
            if is_inside else
            find_max_dist_state(admissible_values, complement_values)
        )

        best_state.append(s_val)
        best_distances.append(weight * d_val)

    return tuple(best_state), (min(best_distances) if is_inside else sum(best_distances))


def find_max_depth_state(admissible_values: DomainType, candidates: List[int], max_act_val: int) -> Tuple[int, int]:
    """
    Finds the state with the greatest depth within the admissible range.

    @param admissible_values: Sorted list of admissible values.
    @param candidates: List of candidate values to evaluate.
    @param max_act_val: Maximum possible value in this dimension.

    @return: Tuple (best_state, max_depth).
    """
    best_v, best_d = None, -inf
    for s in candidates:
        pos = bisect_left(admissible_values, s)
        depth = compute_dimension_depth(admissible_values, s, pos, max_act_val)
        if depth > best_d:
            best_v, best_d = s, depth

    return best_v, best_d


def find_max_dist_state(admissible_values: DomainType, candidates: List[int]) -> Tuple[int, int]:
    """
    Finds the state with the greatest distance outside the admissible range.

    @param admissible_values: Sorted list of admissible values.
    @param candidates: List of candidate values to evaluate.

    @return: Tuple (best_state, max_distance).
    """
    best_v, best_d = None, -inf
    for s in candidates:
        pos = bisect_left(admissible_values, s)
        distance = compute_dimension_dist(admissible_values, s, pos)
        if distance > best_d:
            best_v, best_d = s, distance

    return best_v, best_d
