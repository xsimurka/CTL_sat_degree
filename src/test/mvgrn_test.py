import unittest
from multivalued_grn import MvGRNParser, StateTransitionGraph, MultivaluedGRN


class TestStateTransitionGraph(unittest.TestCase):

    def setUp(self):
        self.incoherent_ffl = {
            "network": {
                "variables": {
                    "X": 4,
                    "Y": 4,
                    "Z": 4
                },
                "regulations": [
                    {
                        "target": "X",
                        "regulators": [],
                        "contexts": [
                            {"intervals": [], "target_value": 4}
                        ]
                    },
                    {
                        "target": "Y",
                        "regulators": [{"variable": "X", "thresholds": [1, 2, 3, 4]}],
                        "contexts": [
                            {"intervals": [3], "target_value": 1},
                            {"intervals": [4], "target_value": 2},
                            {"intervals": [5], "target_value": 3},
                            {"intervals": ["*"], "target_value": 0}
                        ]
                    },
                    {
                        "target": "Z",
                        "regulators": [
                            {"variable": "X", "thresholds": [1, 3]},
                            {"variable": "Y", "thresholds": [1, 2, 4]}
                        ],
                        "contexts": [
                            {"intervals": [3, 3], "target_value": 1},
                            {"intervals": [1, 1], "target_value": 2},
                            {"intervals": [2, 1], "target_value": 3},
                            {"intervals": [3, 1], "target_value": 4},
                            {"intervals": [3, 2], "target_value": 2},
                            {"intervals": ["*", 2], "target_value": 1},
                            {"intervals": ["*", 3], "target_value": 0},
                            {"intervals": ["*", 4], "target_value": 0}
                        ]
                    }
                ]
            },
            "formula": "",
            "init_states": {}
        }
        self.toggle_switch = {
            "network":
                {
                    "variables": {
                        "A": 2,
                        "B": 2
                    },
                    "regulations": [
                        {
                            "target": "A",
                            "regulators": [
                                {"variable": "A", "thresholds": [1]},
                                {"variable": "B", "thresholds": [1]}
                            ],
                            "contexts": [
                                {"intervals": [1, 1], "target_value": 1},
                                {"intervals": [2, 1], "target_value": 2},
                                {"intervals": [1, 2], "target_value": 0},
                                {"intervals": [2, 2], "target_value": 1}
                            ]
                        },
                        {
                            "target": "B",
                            "regulators": [
                                {"variable": "B", "thresholds": [1]},
                                {"variable": "A", "thresholds": [1]}
                            ],
                            "contexts": [
                                {"intervals": [1, 1], "target_value": 1},
                                {"intervals": [2, 1], "target_value": 2},
                                {"intervals": [1, 2], "target_value": 0},
                                {"intervals": [2, 2], "target_value": 1}
                            ]
                        }
                    ]
                }
            }

        self.grn = None
        self.stg = None

    def test_parse_valid_data(self):
        parser = MvGRNParser(self.incoherent_ffl.get("network"))
        self.incoherent_ffl = parser.parse()
        self.assertIsInstance(self.incoherent_ffl, MultivaluedGRN)
        self.assertEqual(set(self.incoherent_ffl.variables.keys()), {"X", "Y", "Z"})

    def test_successor_generation_consistency(self):
        parser = MvGRNParser(self.toggle_switch.get("network"))
        self.grn = parser.parse()
        self.assertIsInstance(self.grn, MultivaluedGRN)
        self.assertEqual(set(self.grn.variables.keys()), {"A", "B"})
        successors = {
            (0, 0): {(1, 0), (0, 1)},
            (0, 1): {(0, 2)},
            (0, 2): {(0, 2)},
            (1, 0): {(2, 0)},
            (1, 1): {(1, 1)},
            (1, 2): {(1, 1)},
            (2, 0): {(2, 0)},
            (2, 1): {(1, 1)},
            (2, 2): {(2, 1), (1, 2)},
        }

        self.stg = StateTransitionGraph(self.grn)

        for node, expected_successors in successors.items():
            actual_successors = set(self.stg.graph.successors(node))
            assert actual_successors == expected_successors, \
                f"Node {node}: expected {expected_successors}, got {actual_successors}"

        # Also make sure all expected nodes are in the graph
        assert set(self.stg.graph.nodes) == set(successors.keys()), \
            "Mismatch in expected and actual nodes in the state transition graph"



if __name__ == '__main__':
    unittest.main()
