from typing import List, Dict, Tuple, Optional


DomainType = List[int]
DomainOfValidityType = List[DomainType]
StateType = Tuple[int, ...]
MaxActivitiesType = Dict[str, int]
FormulaEvaluationType = Dict[Tuple[int], Dict[str, Optional[float]]]
