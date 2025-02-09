import time
from typing import Any

from app.error import Return

from . import environment

class Callable:
    def call(self, argumnets) -> Any: ...
    def arity(self) -> int: ...
    def __str__(self) -> str: return '<native fn>'


class Clock(Callable):
    def call(self, argumnets):
        return time.time_ns() / 1_000_000_000

    def arity(self):
        return 0

class LoxFunction(Callable):
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, argumnets):
        with environment.enclosing(self.closure):
            for i, param in enumerate(self.declaration.params):
                environment.set_env(param.lexeme, argumnets[i])

            try:
                self.declaration.body.evaluate()
            except Return as e:
                return e.value

    def arity(self):
        return len(self.declaration.params)

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
