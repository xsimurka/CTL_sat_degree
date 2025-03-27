from typing import Dict, List


class DomainOfValidity:
    """Represents domain of validity for given atomic formula that has union,
    intersection or atomic propositions (format: variable >=/<= value)"""

    def __init__(self, max_activities):
        # Each dict represent convex subspace, key is variable name, value is list of admissible values
        self.subspaces: List[Dict[str, List[int]]] = []
        self.max_activities: Dict[str, int] = max_activities

    def add_subspace(self, new: Dict[str, List[int]]):
        """Adds new subspace while performing checks on merge."""
        for i in range(len(self.subspaces)):
            if self.is_subspace(new, self.subspaces[i]):
                return  # no change made so no merge possible
            if self.is_superspace(new, self.subspaces[i]):
                self.subspaces.pop(i)  # pop the subspace that will be replaced
                break  # merge is possible as we updated some subspace
        merge_performed = True
        merging_subspace = new
        while merge_performed:  # do while some merge was done in previous iteration (and at least once)
            merge_performed = False
            for i in range(len(self.subspaces)):
                if self.check_merge(self.subspaces[i], merging_subspace):  # merge possible
                    self.merge_subspaces(self.subspaces[i], merging_subspace)  # merge second into existing
                    merging_subspace = self.subspaces.pop(i)  # pop it as it candidate for merging with another
                    merge_performed = True
        self.subspaces.append(merging_subspace)  # finally append the merged subspace

    def is_subspace(self, new: Dict[str, List[int]], existing: Dict[str, List[int]]) -> bool:
        """Checks whether newly added subspace is subspace of some existing"""
        for var in self.max_activities.keys():
            existing_dom = set(existing.get(var, range(self.max_activities.get(var) + 1)))
            new_dom = set(new.get(var, range(self.max_activities.get(var) + 1)))
            if not new_dom.issubset(existing_dom):
                return False
        return True

    def is_superspace(self, new: Dict[str, List[int]], existing: Dict[str, List[int]]) -> bool:
        """Checks whether newly added subspace is superspace of some existing"""
        for var in self.max_activities.keys():
            existing_dom = set(existing.get(var, range(self.max_activities.get(var) + 1)))
            new_dom = set(new.get(var, range(self.max_activities.get(var) + 1)))
            if not new_dom.issuperset(existing_dom):
                return False
        return True

    def check_merge(self, existing: Dict[str, List[int]], new: Dict[str, List[int]]) -> bool:
        """Checks all existing subspaces if one of them cannot be merged with existing subspace to one convex subspace
        Returns subspace to be merged with, or None if not possible."""
        def is_consecutive(lst):
            return all(lst[i] + 1 == lst[i + 1] for i in range(len(lst) - 1))

        joker = True
        for var in self.max_activities.keys():
            existing_dom = set(existing.get(var, range(self.max_activities.get(var) + 1)))
            new_dom = set(new.get(var, range(self.max_activities.get(var) + 1)))
            if existing_dom != new_dom:
                if not joker or not is_consecutive(sorted(existing_dom | new_dom)):
                    return False
                joker = False
        return True


    def merge_subspaces(self, subspace1: Dict[str, List[int]], subspace2: Dict[str, List[int]]):
        """Merges second subspace into first one in place"""
        for var in self.max_activities.keys():
            if var in subspace1 and var in subspace2:
                subspace1[var] = sorted(set(subspace1[var]) | set(subspace2[var]))



