import unittest
from diplomka.src.ctl_parser import CTLParser, Conjunction, Disjunction, AX, EX, AG, EF, AtomicProposition


class CTLParserTest(unittest.TestCase):

    def test_deeply_nested_formula(self):
        parser = CTLParser()
        formula = "AG (AX (a >= 5 & (EF (b <= 3 | (EX (c >= 7 & d <= 2))))))"
        result = parser.parse(formula)

        # Assert AG
        self.assertIsInstance(result, AG)
        self.assertIsInstance(result.operand, AX)

        # Assert AX
        ax_inner = result.operand
        self.assertIsInstance(ax_inner.operand, Conjunction)

        # Conjunction inside AX
        conjunction = ax_inner.operand
        self.assertIsInstance(conjunction.left, AtomicProposition)
        self.assertEqual(conjunction.left.variable, "a")
        self.assertEqual(conjunction.left.operator, ">=")
        self.assertEqual(conjunction.left.value, 5)
        self.assertIsInstance(conjunction.right, EF)

        # EF
        ef_inner = conjunction.right
        self.assertIsInstance(ef_inner.operand, Disjunction)

        # Disjunction inside EF
        disjunction = ef_inner.operand
        self.assertIsInstance(disjunction.left, AtomicProposition)
        self.assertEqual(disjunction.left.variable, "b")
        self.assertEqual(disjunction.left.operator, "<=")
        self.assertEqual(disjunction.left.value, 3)
        self.assertIsInstance(disjunction.right, EX)

        # EX
        ex_inner = disjunction.right
        self.assertIsInstance(ex_inner.operand, Conjunction)

        # Conjunction inside EX
        ex_conjunction = ex_inner.operand
        self.assertIsInstance(ex_conjunction.left, AtomicProposition)
        self.assertEqual(ex_conjunction.left.variable, "c")
        self.assertEqual(ex_conjunction.left.operator, ">=")
        self.assertEqual(ex_conjunction.left.value, 7)
        self.assertIsInstance(ex_conjunction.right, AtomicProposition)
        self.assertEqual(ex_conjunction.right.variable, "d")
        self.assertEqual(ex_conjunction.right.operator, "<=")
        self.assertEqual(ex_conjunction.right.value, 2)


if __name__ == '__main__':
    unittest.main()
