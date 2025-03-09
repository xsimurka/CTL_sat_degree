from typing import List, Optional, Dict, Tuple
from math import inf
import networkx as nx
from diplomka.src.satisfaction_degree import signed_distance

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


stg1 = KripkeStructure([(0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (3, 0, 0, 0, 0), (4, 0, 0, 0, 0), (1, 1, 0, 0, 0),
                        (2, 1, 0, 0, 0), (3, 1, 0, 0, 0), (4, 1, 0, 0, 0), (0, 1, 0, 0, 0), (2, 0, 1, 0, 0), (3, 0, 1, 0, 0),
                        (4, 0, 1, 0, 0), (0, 0, 1, 0, 0), (1, 0, 1, 0, 0), (2, 1, 1, 0, 0), (3, 1, 1, 0, 0), (4, 1, 1, 0, 0),
                        (1, 1, 1, 0, 0), (0, 1, 1, 0, 0), (3, 0, 0, 1, 0), (4, 0, 0, 1, 0), (0, 0, 0, 1, 0), (1, 0, 0, 1, 0),
                        (2, 0, 0, 1, 0), (3, 1, 0, 1, 0), (4, 1, 0, 1, 0), (1, 1, 0, 1, 0), (2, 1, 0, 1, 0), (0, 1, 0, 1, 0),
                        (3, 0, 1, 1, 0), (4, 0, 1, 1, 0), (2, 0, 1, 1, 0), (0, 0, 1, 1, 0), (1, 0, 1, 1, 0), (3, 1, 1, 1, 0),
                        (4, 1, 1, 1, 0), (2, 1, 1, 1, 0), (1, 1, 1, 1, 0), (0, 1, 1, 1, 0), (4, 0, 0, 0, 1), (0, 0, 0, 0, 1),
                        (1, 0, 0, 0, 1), (2, 0, 0, 0, 1), (3, 0, 0, 0, 1), (4, 1, 0, 0, 1), (1, 1, 0, 0, 1), (2, 1, 0, 0, 1),
                        (3, 1, 0, 0, 1), (0, 1, 0, 0, 1), (4, 0, 1, 0, 1), (2, 0, 1, 0, 1), (3, 0, 1, 0, 1), (0, 0, 1, 0, 1),
                        (1, 0, 1, 0, 1), (4, 1, 1, 0, 1), (2, 1, 1, 0, 1), (3, 1, 1, 0, 1), (1, 1, 1, 0, 1), (0, 1, 1, 0, 1),
                        (4, 0, 0, 1, 1), (3, 0, 0, 1, 1), (0, 0, 0, 1, 1), (1, 0, 0, 1, 1), (2, 0, 0, 1, 1), (4, 1, 0, 1, 1),
                        (3, 1, 0, 1, 1), (1, 1, 0, 1, 1), (2, 1, 0, 1, 1), (0, 1, 0, 1, 1), (4, 0, 1, 1, 1), (3, 0, 1, 1, 1),
                        (2, 0, 1, 1, 1), (0, 0, 1, 1, 1), (1, 0, 1, 1, 1), (4, 1, 1, 1, 1), (3, 1, 1, 1, 1), (2, 1, 1, 1, 1),
                        (1, 1, 1, 1, 1), (0, 1, 1, 1, 1)],
                       {0: [1], 1: [5, 2], 2: [10, 6, 3], 3: [20, 11, 7, 4], 4: [40, 21, 12, 8], 5: [6], 6: [15, 7], 7: [25, 16, 8],
            8: [45, 26, 17], 9: [0, 5], 10: [15, 11], 11: [30, 16, 12], 12: [50, 31, 17], 13: [0, 14], 14: [1, 18, 10],
            15: [16], 16: [35, 17], 17: [55, 36], 18: [5, 15], 19: [9, 13, 18], 20: [30, 25, 21], 21: [60, 31, 26],
            22: [0, 23], 23: [1, 27, 24], 24: [2, 32, 28, 20], 25: [35, 26], 26: [65, 36], 27: [5, 28], 28: [6, 37, 25],
            29: [9, 22, 27], 30: [35, 31], 31: [70, 36], 32: [10, 37, 30], 33: [13, 22, 34], 34: [14, 23, 38, 32],
            35: [36], 36: [75], 37: [15, 35], 38: [18, 27, 37], 39: [19, 29, 33, 38], 40: [60, 50, 45], 41: [0, 42],
            42: [1, 46, 43], 43: [2, 51, 47, 44], 44: [3, 61, 52, 48, 40], 45: [65, 55], 46: [5, 47], 47: [6, 56, 48],
            48: [7, 66, 57, 45], 49: [9, 41, 46], 50: [70, 55], 51: [10, 56, 52], 52: [11, 71, 57, 50],
            53: [13, 41, 54], 54: [14, 42, 58, 51], 55: [75], 56: [15, 57], 57: [16, 76, 55], 58: [18, 46, 56],
            59: [19, 49, 53, 58], 60: [70, 65], 61: [20, 71, 66, 60], 62: [22, 41, 63], 63: [23, 42, 67, 64],
            64: [24, 43, 72, 68, 61], 65: [75], 66: [25, 76, 65], 67: [27, 46, 68], 68: [28, 47, 77, 66],
            69: [29, 49, 62, 67], 70: [75], 71: [30, 76, 70], 72: [32, 51, 77, 71], 73: [33, 53, 62, 74],
            74: [34, 54, 63, 78, 72], 76: [35, 75], 77: [37, 56, 76], 78: [38, 58, 67, 77], 79: [39, 59, 69, 73, 78]}
                       )

stg2 = KripkeStructure([(0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (2, 0, 0, 0, 0), (3, 0, 0, 0, 0), (4, 0, 0, 0, 0), (1, 1, 0, 0, 0),
                        (0, 1, 0, 0, 0), (2, 1, 0, 0, 0), (3, 1, 0, 0, 0), (4, 1, 0, 0, 0), (2, 0, 1, 0, 0), (0, 0, 1, 0, 0),
                        (1, 0, 1, 0, 0), (3, 0, 1, 0, 0), (4, 0, 1, 0, 0), (2, 1, 1, 0, 0), (1, 1, 1, 0, 0), (0, 1, 1, 0, 0),
                        (3, 1, 1, 0, 0), (4, 1, 1, 0, 0), (3, 0, 0, 1, 0), (0, 0, 0, 1, 0), (1, 0, 0, 1, 0), (2, 0, 0, 1, 0),
                        (4, 0, 0, 1, 0), (1, 1, 0, 1, 0), (0, 1, 0, 1, 0), (3, 1, 0, 1, 0), (2, 1, 0, 1, 0), (4, 1, 0, 1, 0),
                        (3, 0, 1, 1, 0), (0, 0, 1, 1, 0), (2, 0, 1, 1, 0), (1, 0, 1, 1, 0), (4, 0, 1, 1, 0), (3, 1, 1, 1, 0),
                        (2, 1, 1, 1, 0), (1, 1, 1, 1, 0), (0, 1, 1, 1, 0), (4, 1, 1, 1, 0), (4, 0, 0, 0, 1), (0, 0, 0, 0, 1),
                        (1, 0, 0, 0, 1), (2, 0, 0, 0, 1), (3, 0, 0, 0, 1), (1, 1, 0, 0, 1), (0, 1, 0, 0, 1), (2, 1, 0, 0, 1),
                        (4, 1, 0, 0, 1), (3, 1, 0, 0, 1), (0, 0, 1, 0, 1), (2, 0, 1, 0, 1), (1, 0, 1, 0, 1), (4, 0, 1, 0, 1),
                        (3, 0, 1, 0, 1), (2, 1, 1, 0, 1), (1, 1, 1, 0, 1), (0, 1, 1, 0, 1), (4, 1, 1, 0, 1), (3, 1, 1, 0, 1),
                        (4, 0, 0, 1, 1), (0, 0, 0, 1, 1), (1, 0, 0, 1, 1), (3, 0, 0, 1, 1), (2, 0, 0, 1, 1), (1, 1, 0, 1, 1),
                        (0, 1, 0, 1, 1), (4, 1, 0, 1, 1), (3, 1, 0, 1, 1), (2, 1, 0, 1, 1), (4, 0, 1, 1, 1), (0, 0, 1, 1, 1),
                        (3, 0, 1, 1, 1), (2, 0, 1, 1, 1), (1, 0, 1, 1, 1), (4, 1, 1, 1, 1), (3, 1, 1, 1, 1), (2, 1, 1, 1, 1),
                        (1, 1, 1, 1, 1), (0, 1, 1, 1, 1)]
                       , {1: [5, 0], 2: [10, 7, 1], 3: [20, 13, 8, 2], 4: [40, 24, 14, 9, 3], 5: [6], 6: [0], 7: [15, 5],
              8: [27, 18, 7], 9: [48, 29, 19, 8], 10: [15, 12], 11: [0], 12: [1, 16, 11], 13: [30, 18, 10],
              14: [53, 34, 19, 13], 15: [16], 16: [5, 17], 17: [6, 11], 18: [35, 15], 19: [58, 39, 18],
              20: [30, 27, 23], 21: [0], 22: [1, 25, 21], 23: [2, 32, 28, 22], 24: [60, 34, 29, 20], 25: [5, 26],
              26: [6, 21], 27: [35, 28], 28: [7, 36, 25], 29: [67, 39, 27], 30: [35, 32], 31: [11, 21],
              32: [10, 36, 33], 33: [12, 22, 37, 31], 34: [70, 39, 30], 35: [36], 36: [15, 37], 37: [16, 25, 38],
              38: [17, 26, 31], 39: [75, 35], 40: [60, 53, 48, 44], 41: [0], 42: [1, 45, 41], 43: [2, 51, 47, 42],
              44: [3, 63, 54, 49, 43], 45: [5, 46], 46: [6, 41], 47: [7, 55, 45], 48: [67, 58, 49], 49: [8, 68, 59, 47],
              50: [11, 41], 51: [10, 55, 52], 52: [12, 42, 56, 50], 53: [70, 58, 54], 54: [13, 72, 59, 51],
              55: [15, 56], 56: [16, 45, 57], 57: [17, 46, 50], 58: [75, 59], 59: [18, 76, 55], 60: [70, 67, 63],
              61: [21, 41], 62: [22, 42, 65, 61], 63: [20, 72, 68, 64], 64: [23, 43, 73, 69, 62], 65: [25, 45, 66],
              66: [26, 46, 61], 67: [75, 68], 68: [27, 76, 69], 69: [28, 47, 77, 65], 70: [75, 72], 71: [31, 50, 61],
              72: [30, 76, 73], 73: [32, 51, 77, 74], 74: [33, 52, 62, 78, 71], 75: [76], 76: [35, 77],
              77: [36, 55, 78], 78: [37, 56, 65, 79], 79: [38, 57, 66, 71]}
                       )


# hamming dst na viac rozmernom priestre
# zanorene EF

# CTL fairness
# precitat Fageho, exqmple 4
# skusit spravit EF zanorene tak, ze budem postupovat v back reachability len zo stavov kde je constr. splneny
# a nakonci vybrat len najlepsiu z ciest kde su vsetky splnene nie zo vsetkych ciest
# spisat metriku
