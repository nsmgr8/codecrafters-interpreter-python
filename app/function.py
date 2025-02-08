import time
from typing import Any


class Callable:
    def call(self, interpreter, argumnets) -> Any: ...
    def arity(self) -> int: ...
    def __str__(self): return '<native fn>'


class Clock(Callable):
    def call(self, interpreter, argumnets):
        return time.time_ns() / 1_000_000_000

    def arity(self):
        return 0
