import json
import itertools


json_string = '''
{
  "variables": {
    "gene1": 3,
    "gene2": 3,
    "gene3": 2,
    "gene4": 3
  },
  "regulations": [
    {
      "target": "gene1",
      "regulators": [
        { "variable": "gene2", "thresholds": [1, 2] },
        { "variable": "gene3", "thresholds": [1, 2] }
      ],
      "contexts": [
        { "intervals": [2, 1], "target_value": 0 },
        { "intervals": [1, 1], "target_value": 1 },
        { "intervals": [1, 2], "target_value": 2 },
        { "intervals": [2, 2], "target_value": 2 },
        { "intervals": ["*", "*"], "target_value": 2 }
      ]
    },
    {
      "target": "gene2",
      "regulators": [
        { "variable": "gene1", "thresholds": [1, 2] },
        { "variable": "gene4", "thresholds": [1] }
      ],
      "contexts": [
        { "intervals": [1, "*"], "target_value": 2 },
        { "intervals": [2, "*"], "target_value": 1 },
        { "intervals": ["*", 1], "target_value": 1 },
        { "intervals": ["*", 2], "target_value": 0 },
        { "intervals": [1, 1], "target_value": 2 },
        { "intervals": [2, 1], "target_value": 1 }
      ]
    },
    {
      "target": "gene3",
      "regulators": [
        { "variable": "gene1", "thresholds": [1, 2] },
        { "variable": "gene4", "thresholds": [2] }
      ],
      "contexts": [
        { "intervals": [1, "*"], "target_value": 0 },
        { "intervals": [2, "*"], "target_value": 2 },
        { "intervals": ["*", 2], "target_value": 1 },
        { "intervals": [3, 2], "target_value": 0 },
        { "intervals": ["*", 1], "target_value": 0 }
      ]
    },
    {
      "target": "gene4",
      "regulators": [
        { "variable": "gene2", "thresholds": [2] },
        { "variable": "gene3", "thresholds": [1] }
      ],
      "contexts": [
        { "intervals": [1, 1], "target_value": 2 },
        { "intervals": [2, 2], "target_value": 0 },
        { "intervals": ["*", "*"], "target_value": 1 }
      ]
    }
  ]
}

'''


class MultivaluedGRN:
    def __init__(self, variables, regulations):
        self.variables = variables
        self.regulations = regulations

    def get_parsed_data(self):
        """ Return the validated and parsed data. """
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
        """ Parse and validate the JSON, and return a MultivaluedGRN object if valid. """
        if "variables" not in self.json_data or "regulations" not in self.json_data:
            raise ValueError("Fields 'variables' and 'regulations' both have to be specified.")

        variables = self.json_data.get("variables")
        regulations = self.json_data.get("regulations")

        # Validate JSON
        self.variables = self._validate_variables(variables)
        self.regulations = self._validate_regulations(regulations)

        return MultivaluedGRN(self.variables, self.regulations)

    def _validate_variables(self, variables):
        """ Ensure variables are properly defined with valid max values. """
        if not isinstance(variables, dict):
            raise ValueError("The 'variables' field must be a dictionary.")

        for gene, max_value in variables.items():
            if not isinstance(max_value, int) or max_value <= 0:
                raise ValueError(f"Invalid max activity value for {gene}: {max_value}. Must be an integer > 0.")

        return variables

    def _validate_regulations(self, regulations):
        """ Validate regulations including gene existence, regulator thresholds, and context structure. """
        if not isinstance(regulations, list):
            raise ValueError("The 'regulations' field must be a list.")

        for regulation in regulations:
            self._validate_regulation(regulation)

        return regulations

    def _validate_regulation(self, regulation):
        if "target" not in regulation or "regulators" not in regulation or "contexts" not in regulation:
            raise ValueError("Fields 'target', 'regulators' and 'contexts' all have to be specified.")

        target = regulation.get("target")
        if target not in self.variables:
            raise ValueError(f"Target gene '{target}' is not defined in 'variables'.")

        regulators = regulation.get("regulators")
        self._validate_regulators(regulators)

        contexts = regulation.get("contexts")
        self._validate_contexts(contexts, target, regulators)

    def _validate_regulators(self, regulators):
        """ Ensure regulators exist and have valid thresholds. """
        if not isinstance(regulators, list):
            raise ValueError("The 'regulators' field must be a list.")

        for regulator in regulators:
            self._validate_regulator(regulator)

    def _validate_regulator(self, regulator):
        if "variable" not in regulator or "thresholds" not in regulator:
            raise ValueError("Fields 'variable' and 'thresholds' both have to be specified.")

        gene = regulator.get("variable")
        if gene not in self.variables:
            raise ValueError(f"Regulator gene '{gene}' is not defined in 'variables'.")

        max_value = self.variables[gene]
        thresholds = regulator.get("thresholds")
        if not all(isinstance(t, int) and 0 < t <= max_value for t in thresholds):
            raise ValueError(
                f"Invalid thresholds {thresholds} for '{gene}'. Must be integers within [0, {max_value}].")

    def _validate_contexts(self, contexts, target, regulators):
        """ Ensure contexts align with regulator activity thresholds, allow wildcards, and validate target values. """
        if not isinstance(contexts, list):
            raise ValueError("The 'contexts' field must be a list.")

        target_max_activity_value = self.variables[target]
        expected_length = len(regulators)

        for context in contexts:
            self._validate_context(context, target_max_activity_value, regulators)


    def _validate_context(self, context, target_max_activity_value, regulators):
        if "intervals" not in context or "target_value" not in context:
            raise ValueError("Fields 'intervals' and 'target_value' both have to be specified.")

        intervals = context.get("intervals")
        target_value = context.get("target_value")
        # Check that the target value is within the allowed range
        if not (0 <= target_value <= target_max_activity_value):
            raise ValueError(
                f"Invalid target activity value '{target_value}' for context '{context}'. Must be in range [0, {target_max_activity_value}].")

        # Ensure correct format of intervals (e.g., [1,2.."*"])
        if not (isinstance(intervals, list) and all((x == "*" or isinstance(x, int)) for x in intervals)):
            raise ValueError(f"Invalid context format: {context}. Expected a list of integers or '*'.")

        if len(regulators) != len(intervals):
            raise ValueError(
                f"Context '{context}' length does not match the number of regulators ({len(regulators)}).")

        for idx, value in enumerate(intervals):
            if value == "*":
                continue

            # the n activity levels split the activity of regulator into n + 1 activity intervals
            # the value at idx-th position in context should refer to the index of activity interval of corresponding regulator
            if value < 1:
                raise ValueError(f"Invalid context value '{value}' at position {idx} in context '{context}'.")

            # the value should refer to the index of activity interval defined by 'regulators' activity thresholds
            if value > len(regulators[idx].get("thresholds")) + 1:
                raise ValueError(f"Invalid context value '{value}' at position {idx} in context '{context}'.")


class StateTransitionGraph:
    def __init__(self, grn):
        """ Initialize the state transition graph using an instance of MultivaluedGRN. """
        self.variables = grn.variables
        self.regulations = {reg["target"]: reg for reg in grn.regulations}
        self.states = list(self._generate_all_states())  # Generate all possible states
        self.graph = self._build_transition_graph()  # Compute transitions

    def _generate_all_states(self):
        """ Generate all possible states as tuples. """
        ranges = [range(v + 1) for v in self.variables.values()]
        return itertools.product(*ranges)  # Cartesian product of all variable values

    def _build_transition_graph(self):
        """ Create the state transition graph where each state has possible successors. """
        graph = {}

        for state in self.states:
            successors = self._get_successors(state)
            if not successors:
                successors = [state]  # Add a self-loop if there are no successors
            graph[state] = successors

        return graph

    def _get_successors(self, state):
        """ Find all valid successor states for a given state. """
        successors = []
        variable_list = list(self.variables.keys())

        for i, gene in enumerate(variable_list):
            current_value = state[i]
            regulation = self.regulations.get(gene)

            if not regulation:
                continue  # No regulation means no transitions

            regulators = [reg["variable"] for reg in regulation["regulators"]]
            regulator_indices = [variable_list.index(reg) for reg in regulators]

            # Construct the current regulatory context
            regulator_state = [state[idx] for idx in regulator_indices]

            # Find the first satisfied context
            for context in regulation["contexts"]:
                context_intervals = context["intervals"]
                target_value = context["target_value"]

                # Check if this context matches the regulator state
                if self._context_matches(context_intervals, regulator_state):
                    # Determine the new value of the gene
                    if current_value < target_value:
                        new_value = current_value + 1
                    elif current_value > target_value:
                        new_value = current_value - 1
                    else:
                        new_value = current_value  # No change

                    if new_value != current_value:
                        new_state = list(state)
                        new_state[i] = new_value
                        successors.append(tuple(new_state))

                    break  # Stop at the first matching context

        return successors

    def _context_matches(self, context_intervals, regulator_state):
        """ Check if a given regulatory context matches the current regulator state. """
        for context_val, state_val in zip(context_intervals, regulator_state):
            if context_val != "*" and context_val != state_val:
                return False
        return True

    def get_transition_graph(self):
        """ Return the computed transition graph. """
        return self.graph


x = MvGRNParser(json.loads(json_string)).parse()
s = StateTransitionGraph(x)
print(s)
