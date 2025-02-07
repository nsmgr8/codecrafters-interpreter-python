from dataclasses import dataclass
from . import utils, environment
from .expressions import Expr
from .tokenizer import Token


class Statement:
    def evaluate(self): ...

    def is_truthy(self, value):
        return bool(value)

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
        environment.env.set(self.name, self.initializer.evaluate())


@dataclass
class Block(Statement):
    statements: list[Statement]

    def evaluate(self):
        previous_env = environment.env
        try:
            environment.env = environment.Environment(environment.env)
            for stmt in self.statements:
                stmt.evaluate()
        finally:
            environment.env = previous_env


@dataclass
class If(Statement):
    condition: Expr
    thenBranch: Statement
    elseBranch: Statement | None

    def evaluate(self):
        if self.is_truthy(self.condition.evaluate()):
            self.thenBranch.evaluate()
        elif self.elseBranch:
            self.elseBranch.evaluate()
