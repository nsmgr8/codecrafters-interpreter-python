from dataclasses import dataclass
from typing import Any
from . import utils, tokenizer, error, environment 

class Expr:
    def evaluate(self) -> Any:
        return ''

    def is_truthy(self, value):
        return bool(value)

    def is_equal(self, left, right):
        return left == right

@dataclass
class Literal(Expr):
    value: Any = None

    def evaluate(self):
        return self.value

    def __str__(self):
        return utils.to_str(self.value)

@dataclass
class Unary(Expr):
    operator: tokenizer.Token
    right: Expr

    def evaluate(self):
        right = self.right.evaluate()
        match self.operator.type:
            case tokenizer.TokenType.BANG:
                return not self.is_truthy(right)
            case tokenizer.TokenType.MINUS:
                if not isinstance(right, float):
                    raise error.EvaluationError(self.operator.line, "Operand must be a number.")
                return -right

    def __str__(self):
        return utils.parenthesize(self.operator.lexeme, str(self.right))


@dataclass
class Binary(Expr):
    left: Expr
    operator: tokenizer.Token
    right: Expr

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        match self.operator.type:
            case tokenizer.TokenType.MINUS:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left - right
            case tokenizer.TokenType.PLUS:
                if not utils.either_numbers_or_strings_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be two numbers or two strings.")
                return left + right
            case tokenizer.TokenType.SLASH:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left / right
            case tokenizer.TokenType.STAR:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left * right
            case tokenizer.TokenType.GREATER:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left > right
            case tokenizer.TokenType.GREATER_EQUAL:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left >= right
            case tokenizer.TokenType.LESS:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left < right
            case tokenizer.TokenType.LESS_EQUAL:
                if not utils.are_number_operands(left, right):
                    raise error.EvaluationError(self.operator.line, "Operands must be number.")
                return left <= right
            case tokenizer.TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case tokenizer.TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

    def __str__(self):
        return utils.parenthesize(self.operator.lexeme, str(self.left), str(self.right))

@dataclass
class Grouping(Expr):
    expression: Expr

    def evaluate(self):
        return self.expression.evaluate()

    def __str__(self):
        return utils.parenthesize('group', str(self.expression))

@dataclass
class Variable(Expr):
    name: tokenizer.Token

    def evaluate(self):
        return environment.env.get(self.name)


@dataclass
class Assignment(Expr):
    name: tokenizer.Token
    value: Expr

    def evaluate(self):
        return environment.env.update(self.name, self.value.evaluate())
