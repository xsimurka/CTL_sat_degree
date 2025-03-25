import unittest
from src.satisfaction_degree import weighted_signed_distance, find_extreme_state


class TestDistanceFunctions(unittest.TestCase):

    def test_weighted_signed_distance_inside_all(self):
        dov = [[0, 1, 2, 3], [4, 5, 6]]
        state = (1, 6)
        max_act_values = [4, 6]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, 2 * 1/7)

    def test_weighted_signed_distance_boundary_multiple(self):
        dov = [[0, 1, 2, 4], [6, 7, 8, 9]]
        state = (2, 6)
        max_act_values = [4, 9]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, 0)

    def test_weighted_signed_distance_boundary_single(self):
        dov = [[0, 1, 2, 4], [6, 7, 8, 9]]
        state = (2, 7)
        max_act_values = [4, 9]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, 0)

    def test_weighted_signed_distance_outside_only(self):
        dov = [[0, 1, 2], [6, 7, 8, 9], [2, 3, 4]]
        state = (4, 1, 0)
        max_act_values = [4, 9, 5]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, -(2 * 0.2 + 5 * 0.1 + 2 * (1/6)))

    def test_weighted_signed_distance_inside_outside(self):
        dov = [[0, 1, 2], [6, 7, 8, 9], [2, 3, 4]]
        state = (0, 0, 0)
        max_act_values = [4, 9, 5]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, -(6 * 0.1 + 2 * (1/6)))

    def test_weighted_signed_distance_state_space_boundary(self):
        dov = [[0, 1, 2], [3, 6, 7, 8, 9]]
        state = (0, 9)
        max_act_values = [4, 9]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, 3 * 0.1)

    def test_weighted_signed_distance_state_space_boundary_missing(self):
        dov = [[0, 1, 2, 3, 4], [5, 6, 7, 8]]
        state = (0, 7)
        max_act_values = [9, 9]
        result = weighted_signed_distance(dov, state, max_act_values)
        self.assertEqual(result, 1 * 0.1)

    def test_find_extreme_state_inside(self):
        dov = [[0, 1, 2, 3], [2, 5, 7, 8]]
        max_values = [4, 8]
        state, distance = find_extreme_state(dov, max_values, is_inside=True)
        self.assertEqual(state, (0, 8))
        self.assertEqual(distance, 1 * (1/9))

    def test_find_extreme_state_inside_ambiguous(self):
        dov = [[1, 2, 3, 4], [2, 5, 6, 7, 8]]
        max_values = [8, 8]
        _, distance = find_extreme_state(dov, max_values, is_inside=True)
        self.assertEqual(distance, 1 * (1/9))

    def test_find_extreme_state_outside_ambiguous(self):
        dov = [[1, 5], [0, 1, 2, 7, 9]]
        max_values = [5, 9]
        state, distance = find_extreme_state(dov, max_values, is_inside=False)
        self.assertEqual(distance, 2 * (1/6) + 2 * 0.1)


if __name__ == '__main__':
    unittest.main()
