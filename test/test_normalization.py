import unittest
from diplomka.src.ctl_parser import CTLParser, Negation, Conjunction, Disjunction, EX, AG, EF, AU, EU, AtomicProposition, Boolean


class CTLNormalizationTest(unittest.TestCase):

    def test_nested_negation_normalization(self):
        parser = CTLParser()
        formula = "!(AG (!(EF (a >= 5 | !(AX (b <= 3))))) & !(AF (c >= 7)))"
        result = parser.parse(formula).to_pnf()

        # Assert Conjunction
        self.assertIsInstance(result, Conjunction)

        # EF part
        self.assertIsInstance(result.left, EF)
        self.assertIsInstance(result.left.operand, Negation)
        self.assertIsInstance(result.left.operand.operand, AtomicProposition)

        # EG part
        self.assertIsInstance(result.right, EG)
        self.assertIsInstance(result.right.operand, Negation)
        self.assertIsInstance(result.right.operand.operand, AtomicProposition)

    def test_complex_formula_to_pnf(self):
        parser = CTLParser()
        formula = "AG (!(a >= 5) & EF ((b <= 3) | EX (c >= 7 & d <= 2)))"
        result = parser.parse(formula).to_pnf()

        # Check structure after normalization
        self.assertIsInstance(result, Conjunction)
        self.assertIsInstance(result.left, Negation)
        self.assertIsInstance(result.left.operand, AtomicProposition)

        # EF part
        self.assertIsInstance(result.right, EF)
        self.assertIsInstance(result.right.operand, Disjunction)

        # Disjunction inside EF
        disjunction = result.right.operand
        self.assertIsInstance(disjunction.left, AtomicProposition)
        self.assertIsInstance(disjunction.right, EX)

        # EX inside EF
        ex_inner = disjunction.right
        self.assertIsInstance(ex_inner.operand, Conjunction)

        # Conjunction inside EX
        ex_conjunction = ex_inner.operand
        self.assertIsInstance(ex_conjunction.left, AtomicProposition)
        self.assertIsInstance(ex_conjunction.right, AtomicProposition)

    def test_multiple_until_and_future(self):
        parser = CTLParser()
        formula = "EF (AG (a >= 5 U EF (b <= 3 & !c >= 7)))"
        result = parser.parse(formula).to_pnf()

        # Check EU structure
        self.assertIsInstance(result, EU)
        self.assertIsInstance(result.left, Boolean)

        # AG part
        ag_inner = result.right
        self.assertIsInstance(ag_inner, AG)
        self.assertIsInstance(ag_inner.operand, AU)

        # AU inside AG
        au_inner = ag_inner.operand
        self.assertIsInstance(au_inner.left, AtomicProposition)
        self.assertIsInstance(au_inner.right, EF)


if __name__ == '__main__':
    unittest.main()
