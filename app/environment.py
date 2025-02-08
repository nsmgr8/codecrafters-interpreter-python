from app.function import Clock
from .error import EvaluationError

class Environment:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.values = {}

    def __str__(self):
        return str(self.values) + ' <- ' + str(self.enclosing)

    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing:
            return self.enclosing.get(name)

        raise EvaluationError(name.line, f"Undefined variable '{name.lexeme}'.")

    def set(self, name, value):
        self.values[name] = value

    def update(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return value
        if self.enclosing:
            return self.enclosing.update(name, value)

        raise EvaluationError(name.line, f"Undefined variable '{name.lexeme}'.")


env = Environment()
env.set('clock', Clock())
