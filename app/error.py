import sys
from contextlib import contextmanager

error_code = 0

class ParseError(Exception):
    def __init__(self, line_no, msg, where=""):
        self.line_no = line_no
        self.msg = msg
        self.where = where

class EvaluationError(Exception):
    def __init__(self, line_no, msg):
        self.line_no = line_no
        self.msg = msg


class Return(Exception):
    def __init__(self, value):
        self.value = value


@contextmanager
def handled_error():
    global error_code
    try:
        yield
    except ParseError as e:
        error_code = 65
        sys.stderr.write(f'[line {e.line_no}] Error{e.where}: {e.msg}\n')
    except EvaluationError as e:
        error_code = 70
        sys.stderr.write(f'{e.msg}\n[line {e.line_no}]\n')
