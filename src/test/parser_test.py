import unittest
from lark_ctl_parser import parse_formula
from ctl_formulae import AtomicProposition, Negation, Union, Intersection, Conjunction, Disjunction, EX, EF, AF, EG, AG, AU, EW
from lark.exceptions import UnexpectedToken


class TestFormulaParser(unittest.TestCase):

    def test_nested_conjunctions_and_disjunctions(self):
        formula = "(AG(x >= 5)) && (EF(y <= 3 | z >= 10))"
        result = parse_formula(formula)
        self.assertIsInstance(result, Conjunction)
        self.assertIsInstance(result.left, AG)
        self.assertIsInstance(result.right, EF)
        self.assertIsInstance(result.right.operand, Union)

    def test_combined_temporal_and_logical_operators(self):
        formula = "(AF(x >= 5)) || (EG(A (y <= 3) U (z >= 10)))"
        result = parse_formula(formula)
        self.assertIsInstance(result, Disjunction)
        self.assertIsInstance(result.left, AF)
        self.assertIsInstance(result.right, EG)
        self.assertIsInstance(result.right.operand, AU)

    def test_deeply_nested_temporal_logic(self):
        formula = "AG(A (x >= 5 & y <= 3) U (EF(z >= 10)))"
        result = parse_formula(formula)
        self.assertIsInstance(result, AG)
        self.assertIsInstance(result.operand, AU)
        self.assertIsInstance(result.operand.left, Intersection)
        self.assertIsInstance(result.operand.right, EF)

    def test_mixed_negation_and_weak_until(self):
        formula = "EX(E (!(x >= 5)) W (AG(y <= 3)))"
        result = parse_formula(formula)
        self.assertIsInstance(result, EX)
        self.assertIsInstance(result.operand, EW)
        self.assertIsInstance(result.operand.left, Negation)
        self.assertIsInstance(result.operand.right, AG)

    def test_long_complex_formula(self):
        formula = "AG(A (x >= 5) U ((AF(y <= 3)) && (EF(z >= 10 & w <= 2))))"
        result = parse_formula(formula)
        self.assertIsInstance(result, AG)
        self.assertIsInstance(result.operand, AU)
        self.assertIsInstance(result.operand.right, Conjunction)
        self.assertIsInstance(result.operand.right.left, AF)
        self.assertIsInstance(result.operand.right.right, EF)
        self.assertIsInstance(result.operand.right.right.operand, Intersection)

    def test_temporal_with_multiple_levels_of_nesting(self):
        formula = "AF(AG(EX((x >= 5) && (EF(y <= 3)))))"
        result = parse_formula(formula)
        self.assertIsInstance(result, AF)
        self.assertIsInstance(result.operand, AG)
        self.assertIsInstance(result.operand.operand, EX)
        self.assertIsInstance(result.operand.operand.operand, Conjunction)
        self.assertIsInstance(result.operand.operand.operand.right, EF)

    def test_parsing_fails_for_invalid_syntax(self):
        with self.assertRaises(Exception):  # Adjust exception type if needed
            parse_formula("AF x >= 5 &&")

    def test_large_expression(self):
        formula = "(AG(A (x >= 5) U (AF(y <= 3) && (EF(z >= 10 | w <= 2))))) || (EX(!(p >= 4) && (EG(q <= 8))))"
        result = parse_formula(formula)
        self.assertIsInstance(result, Disjunction)
        self.assertIsInstance(result.left, AG)
        self.assertIsInstance(result.left.operand, AU)
        self.assertIsInstance(result.left.operand.left, AtomicProposition)
        self.assertIsInstance(result.left.operand.right, AF)

        self.assertIsInstance(result.right, EX)
        self.assertIsInstance(result.right.operand, Conjunction)
        self.assertIsInstance(result.right.operand.left, Negation)
        self.assertIsInstance(result.right.operand.right, EG)


    def test_not_left_aligned_formula(self):
        formula = "(EG (x >=3)) && (x <=3)"
        try:
            parse_formula(formula)
        except Exception as e:
            self.assertIsInstance(e, UnexpectedToken)


if __name__ == '__main__':
    unittest.main()
