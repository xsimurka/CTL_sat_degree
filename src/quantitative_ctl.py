from typing import Optional
from src.ctl_formulae import *


class KripkeStructure:

    def __init__(self, stg, init_states: Optional[List[State]]):
        self.stg = stg
        self.init_states = init_states if init_states is not None else stg.states


def model_check(ks: KripkeStructure, formula: StateFormula):
    subformulae = formula.get_subformulae()
    mc_data = init_mc_data(ks, [repr(sf) for sf in subformulae])
    for sf in subformulae:
        sf.evaluate(ks, mc_data)


def init_mc_data(ks: KripkeStructure, labels):
    mc_data = {}
    for state in ks.stg.states:
        mc_data[state] = {label: None for label in labels}

    return mc_data

