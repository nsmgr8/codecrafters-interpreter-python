from dataclasses import dataclass

from . import utils, environment, error
from .expressions import Expr
from .tokenizer import Token
from .function import LoxFunction


class Statement:
    def evaluate(self): ...

@dataclass
class Print(Statement):
    expression: Expr

    def evaluate(self):
        value = self.expression.evaluate()
        print(utils.to_str(value, True))

@dataclass
class Expression(Statement):
    expression: Expr

    def evaluate(self):
        self.expression.evaluate()


@dataclass
class Var(Statement):
    name: Token
    initializer: Expr

    def evaluate(self):
        environment.set_env(self.name.lexeme, self.initializer.evaluate())


@dataclass
class Block(Statement):
    statements: list[Statement]

    def evaluate(self):
        with environment.enclosing():
            for stmt in self.statements:
                stmt.evaluate()


@dataclass
class If(Statement):
    condition: Expr
    thenBranch: Statement
    elseBranch: Statement | None

    def evaluate(self):
        if utils.is_truthy(self.condition.evaluate()):
            self.thenBranch.evaluate()
        elif self.elseBranch:
            self.elseBranch.evaluate()


@dataclass
class While(Statement):
    condition: Expr
    body: Statement

    def evaluate(self):
        while utils.is_truthy(self.condition.evaluate()):
            self.body.evaluate()


@dataclass
class Function(Statement):
    name: Token
    params: list[Token]
    body: Block

    def evaluate(self):
        environment.set_env(self.name.lexeme, LoxFunction(self, environment.env))

@dataclass
class Return(Statement):
    value: Expr | None

    def evaluate(self):
        if self.value:
            value = self.value.evaluate()
        else:
            value = None
        raise error.Return(value)
