from typing import List, Dict, Tuple, Optional, Set


DomainType = List[int]
StateType = Tuple[int, ...]
DomainOfValidityType = Set[StateType]
MaxActivitiesType = Dict[str, int]
FormulaEvaluationType = Dict[Tuple[int], Dict[str, Optional[float]]]
