from dataclasses import dataclass
from typing import Any

from app.function import Callable
from . import utils, tokenizer, error, environment

class Expr:
    def evaluate(self) -> Any: ...

@dataclass
class Literal(Expr):
    value: Any = None

    def evaluate(self):
        return self.value

    def __str__(self):
        return utils.to_str(self.value)

@dataclass
class Logical(Expr):
    left: Expr
    operator: tokenizer.Token
    right: Expr

    def evaluate(self):
        left = self.left.evaluate()

        if self.operator.type == tokenizer.TokenType.OR:
            if utils.is_truthy(left):
                return left
        else:
            if not utils.is_truthy(left):
                return left
        return self.right.evaluate()

@dataclass
class Unary(Expr):
    operator: tokenizer.Token
    right: Expr

    def evaluate(self):
        right = self.right.evaluate()
        match self.operator.type:
            case tokenizer.TokenType.BANG:
                return not utils.is_truthy(right)
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
                return left != right
            case tokenizer.TokenType.EQUAL_EQUAL:
                return left == right

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
        return environment.get_env(self.name)


@dataclass
class Assignment(Expr):
    name: tokenizer.Token
    value: Expr

    def evaluate(self):
        return environment.update_env(self.name, self.value.evaluate())

@dataclass
class Call(Expr):
    callee: Expr
    paren: tokenizer.Token
    arguments: list[Expr]

    def evaluate(self):
        callee = self.callee.evaluate()
        if not isinstance(callee, Callable):
            raise error.EvaluationError(self.paren.line, "Can only call functions and classes.")
        arity = callee.arity()
        nargs = len(self.arguments)
        if arity != nargs:
            raise error.EvaluationError(self.paren.line, f"Expected {arity} arguments but got {nargs}.")
        return callee.call([arg.evaluate() for arg in self.arguments])
