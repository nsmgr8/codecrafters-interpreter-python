import sys
from contextlib import contextmanager

error_code = 0

class ParseError(Exception):
    ...

class EvaluationError(Exception):
    def __init__(self, line_no, msg):
        self.line_no = line_no
        self.msg = msg


def set_error(line_no, msg, where=""):
    global error_code
    error_code = 65
    sys.stderr.write(f'[line {line_no}] Error{where}: {msg}\n')


@contextmanager
def handled_parse_error():
    try:
        yield
    except ParseError:
        ...


@contextmanager
def evaluation_error():
    global error_code
    try:
        yield
    except EvaluationError as e:
        sys.stderr.write(f'{e.msg}\n[line {e.line_no}]\n')
        error_code = 70
