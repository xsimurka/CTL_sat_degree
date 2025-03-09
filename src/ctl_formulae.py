class AtomicFormula:
    def __init__(self, formula):
        self.formula = formula

    def __repr__(self):
        return f"{self.formula}"

    def eval(self):
        pass


class AtomicProposition:
    def __init__(self, variable, operator, value):
        self.variable = variable
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"{self.variable} {self.operator} {self.value}"


class Negation:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"!({repr(self.operand)})"  # Properly represent negation

    def eval(self):
        pass  # Placeholder for evaluation logic


class Union:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} | {repr(self.right)})"  # Corrected operator for Union

    def eval(self):
        pass  # Placeholder for evaluation logic


class Intersection:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} & {repr(self.right)})"  # Corrected operator for Intersection

    def eval(self):
        pass  # Placeholder for evaluation logic


class Boolean:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def eval(self):
        pass  # Placeholder for evaluation logic


class Conjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} & {repr(self.right)})"  # Corrected formatting for Conjunction

    def eval(self):
        pass  # Placeholder for evaluation logic


class Disjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} | {repr(self.right)})"  # Corrected formatting for Disjunction

    def eval(self):
        pass  # Placeholder for evaluation logic


class AG:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AG ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class AF:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AF ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class AX:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AX ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class AU:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"A ({repr(self.left)}) U ({repr(self.right)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class EG:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EG ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class EF:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EF ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class EX:
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EX ({repr(self.operand)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class EU:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"E ({repr(self.left)}) U ({repr(self.right)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class AW:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"A ({repr(self.left)}) W ({repr(self.right)})"

    def eval(self):
        pass  # Placeholder for evaluation logic


class EW:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"E ({repr(self.left)}) W ({repr(self.right)})"

    def eval(self):
        pass  # Placeholder for evaluation logic
