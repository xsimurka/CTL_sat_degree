import json
from src.multivalued_network import StateTransitionGraph, MvGRNParser
from src.lark_ctl_parser import parse_formula
from src.quantitative_ctl import model_check

json_string = '''
{
  "network": {
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
  },
  "formula": "AG (gene1 <= 3 && gene2 >= 1)",
  "initial_states": {
    "gene1": 1,
    "gene2": 2,
    "gene3": 0,
    "gene4": 1
  }
}
'''


def main(json_file):
    with open(json_file, 'r') as file:
        json_data = json.load(file)

    formula = json_data.get("formula")
    parsed_formula = parse_formula(formula)

    network_data = json_data.get("network")
    mvgrn = MvGRNParser(network_data).parse()

    stg = StateTransitionGraph(mvgrn)

    initial_states = json_data.get("initial_states")

    result = model_check(stg, parsed_formula, initial_states)

    print("Model Checking Result:", result)


if __name__ == "__main__":
    json_file = "path_to_your_json_file.json"  # Update this path to your JSON file
    main(json_file)
