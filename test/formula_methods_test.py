import unittest
from src.ctl_formulae import AtomicProposition, Negation, Union, Intersection, Conjunction, Disjunction, EX, AX, EF, AF, EG, AG, EU, AU, EW, AW
from itertools import product


class CTLSubformulaeTest(unittest.TestCase):
    def test_get_subformulae_atomic_formula(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        prop_c = AtomicProposition("c", ">=", 1)
        union = Union(prop_a, Intersection(prop_b, prop_c))
        subformulae = union.get_subformulae()
        expected_subformulae = [union]
        self.assertEqual(subformulae, expected_subformulae)

    def test_get_subformulae_temporal(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        prop_c = AtomicProposition("c", ">=", 1)
        prop_d = AtomicProposition("d", "<=", 2)
        ef = EF(prop_d)
        ex = EX(prop_a)
        inter = Intersection(prop_b, prop_c)
        au = AU(ex, inter)
        eg = EG(au)
        formula = Conjunction(eg, ef)

        subformulae = formula.get_subformulae()
        expected_subformulae = [prop_a, ex, inter, au, eg, prop_d, ef, formula]
        self.assertEqual(subformulae, expected_subformulae)


class CTLEliminateNegationTest(unittest.TestCase):
    def test_eliminate_negation_temporal(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        prop_c = AtomicProposition("c", ">=", 1)
        prop_d = AtomicProposition("d", "<=", 2)
        ef = EF(Negation(prop_d))
        ex = EX(prop_a)
        inter = Negation(Intersection(prop_b, prop_c))
        au = AU(ex, inter)
        eg = EG(au)
        formula = Conjunction(eg, ef)
        formula = formula.eliminate_negation()
        self.assertIsInstance(formula.left.operand.right, Union)
        self.assertEqual(formula.left.operand.right.right.operator, "<=")
        self.assertEqual(formula.left.operand.right.right.value, 0)
        self.assertEqual(formula.left.operand.right.left.operator, ">=")
        self.assertEqual(formula.left.operand.right.left.value, 4)
        self.assertIsInstance(formula.right.operand, AtomicProposition)
        self.assertEqual(formula.right.operand.operator, ">=")
        self.assertEqual(formula.right.operand.value, 3)

    def test_eliminate_negation_positive_formula(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        prop_c = AtomicProposition("c", ">=", 1)
        prop_d = AtomicProposition("d", "<=", 2)
        ef = EF(prop_d)
        ex = EX(prop_a)
        inter = Intersection(prop_b, prop_c)
        au = AU(ex, inter)
        eg = EG(au)
        formula = Conjunction(eg, ef)
        formula = formula.eliminate_negation()
        self.assertIsInstance(formula.left.operand.right, Intersection)
        self.assertEqual(formula.left.operand.right.right.operator, ">=")
        self.assertEqual(formula.left.operand.right.right.value, 1)
        self.assertEqual(formula.left.operand.right.left.operator, "<=")
        self.assertEqual(formula.left.operand.right.left.value, 3)
        self.assertIsInstance(formula.right.operand, AtomicProposition)
        self.assertEqual(formula.right.operand.operator, "<=")
        self.assertEqual(formula.right.operand.value, 2)

    def test_eliminate_double_negation(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        formula = Negation(Negation(Union(prop_a, prop_b)))
        formula = formula.eliminate_negation()
        self.assertIsInstance(formula, Union)
        self.assertIsInstance(formula.left, AtomicProposition)
        self.assertEqual(formula.left.operator, ">=")
        self.assertEqual(formula.left.value, 5)

    def test_eliminate_triple_negation(self):
        prop_a = AtomicProposition("a", ">=", 5)
        prop_b = AtomicProposition("b", "<=", 3)
        formula = Negation(Negation(Negation(Union(prop_a, prop_b))))
        formula = formula.eliminate_negation()
        self.assertIsInstance(formula, Intersection)
        self.assertIsInstance(formula.left, AtomicProposition)
        self.assertEqual(formula.left.operator, "<=")
        self.assertEqual(formula.left.value, 4)
        self.assertIsInstance(formula.right, AtomicProposition)
        self.assertEqual(formula.right.operator, ">=")
        self.assertEqual(formula.right.value, 4)


class TestComputeDov(unittest.TestCase):
    def setUp(self):
        self.max_activities = {"x": 3, "y": 2, "z": 2}

    def test_atomic_proposition_ge(self):
        formula = AtomicProposition("x", ">=", 2)
        valid_values = range(2, self.max_activities["x"] + 1)
        expected = set(product(
            valid_values,
            range(self.max_activities["y"] + 1),
            range(self.max_activities["z"] + 1)
        ))
        self.assertEqual(formula.compute_dov(self.max_activities), expected)

    def test_atomic_proposition_le(self):
        formula = AtomicProposition("y", "<=", 1)
        valid_values = range(0, 2)  # 0 and 1
        expected = set(product(
            range(self.max_activities["x"] + 1),
            valid_values,
            range(self.max_activities["z"] + 1)
        ))
        self.assertEqual(formula.compute_dov(self.max_activities), expected)

    def test_union(self):
        formula1 = AtomicProposition("x", "<=", 0)
        formula2 = AtomicProposition("y", "<=", 0)
        union_formula = Union(formula1, formula2)

        expected1 = set(product(
            [0],
            range(self.max_activities["y"] + 1),
            range(self.max_activities["z"] + 1)
        ))

        expected2 = set(product(
            range(self.max_activities["x"] + 1),
            [0],
            range(self.max_activities["z"] + 1)
        ))

        expected = expected1.union(expected2)
        self.assertEqual(union_formula.compute_dov(self.max_activities), expected)

    def test_intersection(self):
        formula1 = AtomicProposition("x", ">=", 2)
        formula2 = AtomicProposition("x", "<=", 3)
        intersection_formula = Intersection(formula1, formula2)

        valid_values = range(2, 4)  # 2 and 3
        expected = set(product(
            valid_values,
            range(self.max_activities["y"] + 1),
            range(self.max_activities["z"] + 1)
        ))
        self.assertEqual(intersection_formula.compute_dov(self.max_activities), expected)

    def test_complex_union_intersection(self):
        formula1 = AtomicProposition("x", ">=", 3)
        formula2 = AtomicProposition("x", "<=", 1)
        formula3 = AtomicProposition("y", "<=", 1)
        formula4 = AtomicProposition("y", ">=", 1)

        union_formula1 = Union(formula1, formula2)
        union_formula2 = Intersection(formula3, formula4)
        complex_formula = Intersection(union_formula1, union_formula2)

        x_values = [0, 1, 3]  # from formula1 and formula2
        y_values = [1]        # y must be exactly 1
        expected = set(product(
            x_values,
            y_values,
            range(self.max_activities["z"] + 1)
        ))
        self.assertEqual(complex_formula.compute_dov(self.max_activities), expected)


if __name__ == '__main__':
    unittest.main()
