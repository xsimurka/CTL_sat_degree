from typing import List, Optional, Dict, Tuple
from math import inf
import networkx as nx
from src.satisfaction_degree import weighted_signed_distance, find_extreme_state


class KripkeStructure:

    def __init__(self, stg, init_states: Optional[List[Tuple[int]]]):
        self.stg = stg
        self.g = nx.DiGraph()
        self.init_states = init_states

    def get_succ_states(self, state: Tuple[int]) -> List[Tuple[int]]:
        pass

    def get_succ_indices(self, state: Tuple[int]) -> List[int]:
        pass

    def all_next(self, state: Tuple[int]) -> float:
        pass

    def exists_next(self, state: Tuple[int]) -> float:
        pass

    def all_future(self, state: Tuple[int]) -> float:
        pass

    def all_future_rec(self, state: Tuple[int]) -> float:
        pass

    def exists_future(self, state: Tuple[int]) -> float:
        pass

    def exists_future_rec(self, state: Tuple[int]) -> float:
        pass

    def all_global(self, state: Tuple[int]) -> float:
        pass

    def all_global_rec(self, state: Tuple[int]) -> float:
        pass

    def exists_global(self, state: Tuple[int]) -> float:
        pass

    def exists_global_rec(self, state: Tuple[int]) -> float:
        pass


def model_check(ks, formula):
    pass
