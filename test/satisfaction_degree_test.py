import unittest
from src.satisfaction_degree import weighted_distance, find_extreme_depth, get_border_states
from itertools import product


class TestDistanceFunctions(unittest.TestCase):
    def setUp(self):
        self.max_activities = [4, 10, 8]
        self.state_space = set(product(*(range(a + 1) for a in self.max_activities)))

        self.simple_dov = {(x, y, z) for x in [2, 3, 4] for y in [5, 6, 7, 8] for z in [3, 4, 5, 6]}
        self.simple_dov_border, self.simple_dov_co_border = get_border_states(self.simple_dov, self.max_activities)

        self.intersect_dov = {(x, y, z) for x in [0, 1, 2, 3] for y in [0, 1, 2, 3, 4] for z in [0, 1, 2, 3]}.union(
            {(x, y, z) for x in [2, 3, 4] for y in [2, 3, 4, 5] for z in [2, 3, 4, 5]})
        self.intersect_dov_border, self.intersect_dov_co_border = get_border_states(self.intersect_dov, self.max_activities)

        self.union_dov = {(x, y, z) for x in [0, 1] for y in [0, 1, 2] for z in [0, 1, 2]}.union(
            {(x, y, z) for x in [3, 4] for y in [6, 7, 8] for z in [6, 7, 8]})
        self.union_dov_border, self.union_dov_co_border = get_border_states(self.union_dov, self.max_activities)

    def test_weighted_signed_distance_inside(self):
        state1 = (3, 6, 4)
        wd = weighted_distance(state1, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.2, wd)

        state2 = (3, 6, 3)
        wd = weighted_distance(state2, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.125, wd)

        state3 = (2, 6, 4)
        wd = weighted_distance(state3, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.2, wd)

        state4 = (2, 3, 2)

        wd = weighted_distance(state4, self.intersect_dov_co_border, self.max_activities)
        self.assertAlmostEqual(0.3, wd)

        state5 = (0, 0, 0)
        wd = weighted_distance(state5, self.union_dov_co_border, self.max_activities)
        self.assertAlmostEqual(0.3, wd)

    def test_weighted_signed_distance_boundary(self):
        state1 = (4, 5, 3)
        wd = weighted_distance(state1, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.1, wd)

        state2 = (2, 6, 4)
        wd = weighted_distance(state2, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.2, wd)

        state3 = (4, 6, 3)
        wd = weighted_distance(state3, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(0.125, wd)

    def test_find_extreme_depth_simple_dov(self):
        depth = find_extreme_depth(self.simple_dov, self.simple_dov_co_border, self.max_activities)
        self.assertEqual(depth, 0.0)

    def test_find_extreme_depth_intersect_dov(self):
        depth = find_extreme_depth(self.intersect_dov, self.intersect_dov_co_border, self.max_activities)
        self.assertEqual(depth, 0.0)

    def test_find_extreme_depth_union_dov(self):
        depth = find_extreme_depth(self.union_dov, self.union_dov_co_border, self.max_activities)
        self.assertEqual(depth, 0.0)

    def test_find_extreme_depth_simple_dov_complement(self):
        """Test depth in the complement of simple_dov using dov_border as reference."""
        co_dov = self.state_space - self.simple_dov
        depth = find_extreme_depth(co_dov, self.simple_dov_border, self.max_activities)
        self.assertEqual(depth, 0.0)

    def test_find_extreme_depth_intersect_dov_complement(self):
        """Test depth in the complement of intersect_dov using dov_border as reference."""
        co_dov = self.state_space - self.intersect_dov
        depth = find_extreme_depth(co_dov, self.intersect_dov_border, self.max_activities)
        self.assertEqual(depth, 0.0)

    def test_find_extreme_depth_union_dov_complement(self):
        """Test depth in the complement of union_dov using dov_border as reference."""
        co_dov = self.state_space - self.union_dov
        depth = find_extreme_depth(co_dov, self.union_dov_border, self.max_activities)
        self.assertEqual(depth, 0.0)


if __name__ == '__main__':
    unittest.main()
