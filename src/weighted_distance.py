from typing import List, Tuple
from math import inf
from custom_types import SubspaceType, StateType
from priority_queue import MinPriorityQueue


def get_hamming_neighbors(state: StateType, max_activities: List[int], weights=None, visited=None):
    """
    Yield valid and unvisited Hamming neighbors in order of increasing weighted distance.

    The algorithm works by iterating over each dimension of the state, adjusting each value by ±1 (delta).
    It checks if the resulting neighbor is within the allowed bounds (max_activities) and has not been visited.
    Neighbors are yielded in order of increasing weight, which is determined by the given weights or default uniform weights.

    @param state: The current state represented as a tuple of integers.
    @param max_activities: A list of maximum allowed values for each activity dimension.
    @param weights: (Optional) A list of weights for each dimension, defaulting to uniform weights.
    @param visited: (Optional) A set of already visited states to avoid revisits.
    @return: A generator yielding tuples (step_size, neighbor_state).
    """
    if weights is None:
        weights = [1 for _ in range(len(state))]
    if visited is None:
        visited = set()
    indices = sorted(range(len(state)), key=lambda i: weights[i])

    # Generate neighbors by iterating over state dimensions and adjusting each by ±1
    for i in indices:
        for delta in [-1, 1]:
            neighbor = list(state)
            neighbor[i] += delta
            neighbor = tuple(neighbor)

            # Check if neighbor is valid and unvisited
            if 0 <= neighbor[i] <= max_activities[i] and neighbor not in visited:
                yield weights[i], neighbor


def get_border_states(dov: SubspaceType, max_activities: List[int]) -> Tuple[SubspaceType, SubspaceType]:
    """
    Identify border states for both DoV and its complement.

    A state in DoV is a border state if it has at least one Hamming neighbor outside DoV (i.e., in co-DoV).
    Conversely, a neighbor in co-DoV is also a border state for co-DoV.

    @param dov: The domain of validity.
    @param max_activities: A list of maximum allowed values for each activity dimension.
    @return: A tuple (dov_border, co_dov_border) where each is a set of border states.
    """
    dov_border = set()
    co_dov_border = set()

    for state in dov:
        for _, neighbor in get_hamming_neighbors(state, max_activities):
            if neighbor not in dov:
                dov_border.add(state)
                co_dov_border.add(neighbor)

    return dov_border, co_dov_border


def weighted_distance(state: StateType, border: SubspaceType, max_activities: List[int]) -> float:
    """
    Compute the shortest weighted Hamming distance from a given state to the border of the state set.

    The algorithm uses a priority queue to perform a modified Dijkstra's algorithm for weighted Hamming distances.
    It iteratively updates the shortest distances from the starting state to neighboring states and checks if any state
    reaches the border. The distance to the first border state found is returned.

    @param state: The starting state for distance computation.
    @param border: The set of border states.
    @param max_activities: A list of maximum allowed values for each activity dimension.
    @return: The shortest weighted Hamming distance to the border.
    """
    weights = [1 / max_activity for max_activity in max_activities]
    queue = MinPriorityQueue()
    queue.decrease_priority(state, 0.0)  # Start with the initial state
    visited = set()

    while not queue.is_empty():
        current, dist = queue.extract_min()
        if current in border:
            return dist  # Return the distance when a border state is found
        visited.add(current)

        # Iterate over neighbors and update distances
        for step, neighbor in get_hamming_neighbors(current, max_activities, weights, visited):
            neighbor_dst = dist + step
            queue.decrease_priority(neighbor, neighbor_dst)

    return float('inf')  # If no border state is found, return infinity


def find_extreme_depth(dov: SubspaceType, co_border: SubspaceType, max_act_values: List[int]) -> float:
    """
    Find the state with the maximum minimal weighted distance to the border of the state set.

    The algorithm applies a multi-source shortest path search from all border states, updating the minimum distances
    for each state in the domain of validity (`dov`). After processing, the state with the maximum of these minimal
    distances is returned.

    @param dov: The domain of validity.
    @param co_border: The set of border states.
    @param max_act_values: A list of maximum allowed values for each activity dimension.
    @return: The maximal minimal weighted distance to the border among states.
    """
    weights = [1 / max_activity for max_activity in max_act_values]
    distances = {state: inf for state in dov.union(co_border)}
    queue = MinPriorityQueue()

    for state in co_border:
        distances[state] = 0  # Distance of border states is 0
        queue.decrease_priority(state, 0)

    while not queue.is_empty():
        current_state, current_distance = queue.extract_min()
        for step_size, neighbor in get_hamming_neighbors(current_state, max_act_values, weights):
            if neighbor not in dov:
                continue
            new_distance = current_distance + step_size
            if distances[neighbor] > new_distance:
                distances[neighbor] = new_distance
                queue.decrease_priority(neighbor, new_distance)

    extreme = max(distances[state] for state in dov)  # opravit nekonecno
    return extreme
