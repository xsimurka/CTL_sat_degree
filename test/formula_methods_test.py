import unittest
from src.ctl_formulae import AtomicProposition, Negation, Union, Intersection, Conjunction, Disjunction, EX, AX, EF, AF, EG, AG, EU, AU, EW, AW
from copy import deepcopy


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


class TestYieldDov(unittest.TestCase):
    def setUp(self):
        self.max_activities = {"x": 10, "y": 5}
        self.dov = [list(range(v + 1)) for v in self.max_activities.values()]

    def test_atomic_proposition_ge(self):
        formula = AtomicProposition("x", ">=", 5)
        expected_dov = [list(range(5, 11)), list(range(6))]
        self.assertEqual(formula.yield_dov(deepcopy(self.dov), self.max_activities), expected_dov)

    def test_atomic_proposition_le(self):
        formula = AtomicProposition("y", "<=", 3)
        expected_dov = [list(range(11)), list(range(4))]
        self.assertEqual(formula.yield_dov(deepcopy(self.dov), self.max_activities), expected_dov)

    def test_union(self):
        formula1 = AtomicProposition("x", ">=", 7)
        formula2 = AtomicProposition("x", "<=", 3)
        union_formula = Union(formula1, formula2)
        expected_dov = [sorted(set(range(7, 11)).union(set(range(4)))), list(range(6))]
        self.assertEqual(union_formula.yield_dov(deepcopy(self.dov), self.max_activities), expected_dov)

    def test_intersection(self):
        formula1 = AtomicProposition("x", ">=", 3)
        formula2 = AtomicProposition("x", "<=", 7)
        intersection_formula = Intersection(formula1, formula2)
        expected_dov = [sorted(set(range(3, 8))), list(range(6))]
        self.assertEqual(intersection_formula.yield_dov(deepcopy(self.dov), self.max_activities), expected_dov)

    def test_complex_union_intersection(self):
        formula1 = AtomicProposition("x", ">=", 7)
        formula2 = AtomicProposition("x", "<=", 3)
        formula3 = AtomicProposition("y", "<=", 4)
        formula4 = AtomicProposition("y", ">=", 2)
        union_formula1 = Union(formula1, formula2)
        union_formula2 = Intersection(formula3, formula4)
        complex_formula = Intersection(union_formula1, union_formula2)
        expected_dov = [[0, 1, 2, 3, 7, 8, 9, 10], [2, 3, 4]]
        self.assertEqual(complex_formula.yield_dov(deepcopy(self.dov), self.max_activities), expected_dov)


if __name__ == '__main__':
    unittest.main()
