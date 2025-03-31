from typing import Dict, Tuple, Optional, Set


StateType = Tuple[int, ...]
SubspaceType = Set[StateType]
MaxActivitiesType = Dict[str, int]
QuantLabelingFnType = Dict[Tuple[int], Dict[str, Optional[float]]]
