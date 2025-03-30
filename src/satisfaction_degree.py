from typing import List
from math import inf
from src.custom_types import DomainOfValidityType, StateType
from heapq import heappop, heappush


def get_hamming_neighbors(state, max_activities, weights, visited):
    """Yield valid and unvisited Hamming neighbors in order of increasing weighted distance."""
    indices = sorted(range(len(state)), key=lambda i: weights[i])

    for i in indices:
        for delta in [-1, 1]:
            neighbor = list(state)
            neighbor[i] += delta
            neighbor = tuple(neighbor)

            if 0 <= neighbor[i] <= max_activities[i] and neighbor not in visited:
                yield weights[i], neighbor


def get_border_states(dov, max_activities) -> DomainOfValidityType:
    """Returns states that have at least one missing Hamming neighbor."""
    border_states = set()
    for state in dov:
        for _, neighbor in get_hamming_neighbors(state, max_activities, [1 for _ in range(len(max_activities))], set()):
            if neighbor not in dov:  # If any neighbor is missing, mark as border state
                border_states.add(state)
                break  # No need to check further for this state

    return border_states


def weighted_distance(state, border, max_activities):
    """
    Compute the shortest weighted Hamming distance from start_state to the border of state set.
    """
    weights = [1 / max_activity for max_activity in max_activities]
    pq = [(0, state)]
    visited = set()

    while pq:
        dist, current = heappop(pq)
        visited.add(current)

        for step, neighbor in get_hamming_neighbors(current, max_activities, weights, visited):
            neighbor_dst = dist + step
            if neighbor in border:
                return neighbor_dst
            heappush(pq, (neighbor_dst, neighbor))

    return float('inf')


def find_extreme_state(dov: DomainOfValidityType, border, max_act_values: List[int]) -> float:
    weights = [1 / max_activity for max_activity in max_act_values]
    dp = {state: inf for state in dov}
    queue = []

    for state in border:
        dp[state] = 0
        heappush(queue, (0, state))

    while queue:
        current_distance, current_state = heappop(queue)

        for step_size, neighbor in get_hamming_neighbors(current_state, max_act_values, weights, set()):
            if neighbor not in dov:
                continue

            new_distance = current_distance + step_size
            if dp[neighbor] > new_distance:
                dp[neighbor] = new_distance
                heappush(queue, (new_distance, neighbor))

    extreme = max(dp[state] for state in dov)
    return extreme
