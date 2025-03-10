from typing import List, Optional, Dict, Tuple
from math import inf
import networkx as nx
from src.satisfaction_degree import signed_distance

Constraints = Dict[Tuple[int, str, int], float]


class KripkeStructure:

    def __init__(self, states: List[Tuple[int]], transitions: Dict[int, List[int]], init_states: Optional[List[Tuple[int]]]):
        self.states = states
        self.stg = nx.DiGraph()
        self.init_states = init_states
        self.create_stg(states, transitions)

    def create_stg(self, states: List[Tuple[int]], transitions: Dict[int, List[int]]):
        self.stg.add_nodes_from(range(len(states)))
        self.stg.add_edges_from([(source, target) for source, targets in transitions.items() for target in targets])

    def get_succ_states(self, state: Tuple[int]) -> List[Tuple[int]]:
        return list(map(lambda x: self.states[x], self.get_succ_indices(state)))

    def get_succ_indices(self, state: Tuple[int]) -> List[int]:
        return self.stg.successors(self.states.index(state))

    def all_next(self, state: Tuple[int], constraints: Constraints) -> float:
        score = inf
        successors = self.get_succ_states(state)
        for succ in successors:
            score = min(score, signed_distance(succ, constraints))
        return score

    def exists_next(self, state: Tuple[int], constraints: Constraints) -> float:
        score = -inf
        successors = self.get_succ_states(state)
        for succ in successors:
            score = max(score, signed_distance(succ, constraints))
        return score

    def all_future(self, state: Tuple[int], constraints: Constraints) -> float:
        result = inf
        self.visited[self.states.index(state)] = True
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                result = min(result, self.all_future_rec(n, constraints))

        self.reset_exploration()
        return result

    def all_future_rec(self, state: Tuple[int], constraints: Constraints) -> float:
        self.visited[self.states.index(state)] = True
        best_sd = signed_distance(state, constraints)

        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                neighbour_sd = self.all_future_rec(n, constraints)
                best_sd = min(best_sd, neighbour_sd)

            else:
                pass  # this was already visited, how to use already computed satisf. degree???
        return best_sd

    def exists_future(self, state: Tuple[int], constraints: Constraints) -> float:
        self.visited[self.states.index(state)] = True
        m = -inf
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                m = max(m, self.exists_future_rec(n, constraints))
        return m

    def exists_future_rec(self, state: Tuple[int], constraints: Constraints) -> float:
        m = signed_distance(state, constraints)
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                m = max(m, self.exists_future_rec(n, constraints))
            else:
                m = max(m, self.best_reachable_future[self.states.index(n)])
        self.best_reachable_future[self.states.index(state)] = m
        return m

    def all_global(self, state: Tuple[int], constraints: Constraints) -> float:
        """Nefunguje, treba cez bottom sccs
        Zohladnit aj tie cesty, ktore nefunguju?
        """

        self.visited[self.states.index(state)] = True
        lst = []
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                lst.append(self.all_global_rec(n, constraints))

        lst.append(signed_distance(state, constraints))
        return sum(lst) / len(lst)

    def all_global_rec(self, state: Tuple[int], constraints: Constraints) -> float:
        lst = []
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                lst.append(self.all_global_rec(n, constraints))

        lst.append(signed_distance(state, constraints))
        return sum(lst) / len(lst)

    def exists_global(self, state: Tuple[int], constraints: Constraints) -> float:
        """Nefunguje, treba cez bottom sccs
        Najst najlepsie laso?"""

        self.visited[self.states.index(state)] = True
        lst = []
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                lst.append(self.all_global_rec(n, constraints))

        lst.append(signed_distance(state, constraints))
        return sum(lst) / len(lst)

    def exists_global_rec(self, state: Tuple[int], constraints: Constraints) -> float:
        lst = []
        for n in self.get_succ_states(state):
            if not self.visited[self.states.index(n)]:
                self.visited[self.states.index(n)] = True
                lst.append(self.all_global_rec(n, constraints))

    def find_attractors(self):
        sccs = list(nx.strongly_connected_components(self.stg))
        bottom_sccs = []
        for scc in sccs:
            for node in scc:
                if any(neighbor not in scc for neighbor in self.stg.successors(node)):
                    break
            else:
                bottom_sccs.append(scc)

        return bottom_sccs


def model_check(stg, formula, init_states):
    pass
