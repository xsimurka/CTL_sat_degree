import itertools
import networkx as nx


class MultivaluedGRN:
    def __init__(self, variables, regulations):
        self.variables = variables
        self.regulations = regulations

    def get_parsed_data(self):
        """Return the validated and parsed GRN data."""
        return {
            "variables": self.variables,
            "regulations": self.regulations
        }


class MvGRNParser:
    def __init__(self, json_data):
        self.json_data = json_data
        self.variables = None
        self.regulations = None

    def parse(self):
        """
        Parse and validate JSON data. Return a MultivaluedGRN object.
        """
        required_fields = {"variables", "regulations"}
        if not required_fields.issubset(self.json_data):
            raise ValueError("Both 'variables' and 'regulations' fields must be specified.")

        self.variables = self._validate_variables(self.json_data["variables"])
        self.regulations = self._validate_regulations(self.json_data["regulations"])

        return MultivaluedGRN(self.variables, self.regulations)

    def _validate_variables(self, variables):
        """Validate variables are a dict and each has a positive integer max value."""
        if not isinstance(variables, dict):
            raise ValueError("'variables' must be a dictionary.")

        for gene, max_value in variables.items():
            if not isinstance(max_value, int) or max_value <= 0:
                raise ValueError(f"Invalid max activity value for '{gene}': {max_value}. Must be an integer > 0.")
        return variables

    def _validate_regulations(self, regulations):
        """Validate regulations structure and contents."""
        if not isinstance(regulations, list):
            raise ValueError("'regulations' must be a list.")

        for regulation in regulations:
            self._validate_regulation(regulation)
        return regulations

    def _validate_regulation(self, regulation):
        """Validate an individual regulation structure."""
        required_fields = {"target", "regulators", "contexts"}
        if not required_fields.issubset(regulation):
            raise ValueError("Each regulation must have 'target', 'regulators', and 'contexts' fields.")

        target = regulation["target"]
        if target not in self.variables:
            raise ValueError(f"Target gene '{target}' is not defined in 'variables'.")

        regulators = regulation["regulators"]
        self._validate_regulators(regulators)

        contexts = regulation["contexts"]
        self._validate_contexts(contexts, target, regulators)

    def _validate_regulators(self, regulators):
        """Validate all regulators in the regulation."""
        if not isinstance(regulators, list):
            raise ValueError("'regulators' must be a list.")

        for regulator in regulators:
            self._validate_regulator(regulator)

    def _validate_regulator(self, regulator):
        """Validate an individual regulator and its thresholds."""
        required_fields = {"variable", "thresholds"}
        if not required_fields.issubset(regulator):
            raise ValueError("Each regulator must have 'variable' and 'thresholds' fields.")

        gene = regulator["variable"]
        thresholds = regulator["thresholds"]

        if gene not in self.variables:
            raise ValueError(f"Regulator gene '{gene}' is not defined in 'variables'.")

        max_value = self.variables[gene]
        if not all(isinstance(t, int) and 0 < t <= max_value for t in thresholds):
            raise ValueError(f"Invalid thresholds {thresholds} for '{gene}'. Must be within [1, {max_value}].")

    def _validate_contexts(self, contexts, target, regulators):
        """Validate all contexts in the regulation."""
        if not isinstance(contexts, list):
            raise ValueError("'contexts' must be a list.")

        target_max = self.variables[target]

        for context in contexts:
            self._validate_context(context, target_max, regulators)

    def _validate_context(self, context, target_max, regulators):
        """Validate an individual context."""
        required_fields = {"intervals", "target_value"}
        if not required_fields.issubset(context):
            raise ValueError("Each context must have 'intervals' and 'target_value' fields.")

        intervals = context["intervals"]
        target_value = context["target_value"]

        if not (0 <= target_value <= target_max):
            raise ValueError(f"Target value '{target_value}' must be in range [0, {target_max}].")

        if not (isinstance(intervals, list) and all(isinstance(x, int) or x == "*" for x in intervals)):
            raise ValueError(f"Intervals {intervals} must be a list of integers or '*'.")

        if len(intervals) != len(regulators):
            raise ValueError("Length of 'intervals' does not match number of regulators.")

        for idx, val in enumerate(intervals):
            if val == "*":
                continue

            thresholds_count = len(regulators[idx]["thresholds"])
            if val < 1 or val > thresholds_count + 1:
                raise ValueError(
                    f"Context value '{val}' at position {idx} is invalid. Must be within [1, {thresholds_count + 1}]."
                )


class StateTransitionGraph:
    def __init__(self, grn):
        """
        Initialize the state transition graph from a MultivaluedGRN object.
        """
        self.variables = grn.variables
        self.regulations = {reg["target"]: reg for reg in grn.regulations}
        self.states = list(self._generate_all_states())
        self.graph = self._construct_graph()

    def _generate_all_states(self):
        """
        Generate all possible states of the GRN.

        @return: Iterator over state tuples.
        """
        domains = [range(max_value + 1) for max_value in self.variables.values()]
        return itertools.product(*domains)

    def _construct_graph(self):
        """
        Build the directed state transition graph.

        @return: networkx.DiGraph object.
        """
        G = nx.DiGraph()
        G.add_nodes_from(self.states)

        for state in self.states:
            successors = self._compute_state_successors(state)
            if not successors:
                successors = [state]  # Self-loop for stable states

            for succ in successors:
                G.add_edge(state, succ)

        return G

    def _compute_state_successors(self, state):
        """
        Compute all valid successor states from a given state.

        @param state: Tuple of gene activity levels.
        @return: List of successor states.
        """
        successors = []
        variable_names = list(self.variables.keys())

        for idx, gene in enumerate(variable_names):
            current_val = state[idx]
            regulation = self.regulations.get(gene)

            if not regulation:
                continue  # No regulation → no transitions for this gene

            regulator_names = [r["variable"] for r in regulation["regulators"]]
            regulator_indices = [variable_names.index(rn) for rn in regulator_names]
            regulator_state = [state[i] for i in regulator_indices]

            for context in regulation["contexts"]:
                if is_context_satisfied(context["intervals"], regulator_state):
                    target_val = context["target_value"]
                    delta = target_val - current_val

                    if delta == 0:
                        break

                    next_state = list(state)
                    next_state[idx] = current_val + (1 if delta > 0 else -1)
                    successors.append(tuple(next_state))
                    break  # First matching context determines transition

        return successors


def is_context_satisfied(context_intervals, regulator_state):
    """
    Check whether a context's intervals are satisfied by the given regulator state.

    @param context_intervals: List of intervals (integers or "*").
    @param regulator_state: List of current regulator activity levels.
    @return: True if context is satisfied, False otherwise.
    """
    return all(
        ci == "*" or ci == rs
        for ci, rs in zip(context_intervals, regulator_state)
    )
