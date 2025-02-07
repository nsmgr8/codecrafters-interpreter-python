import sys

def get_code():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ("tokenize", "parse", "evaluate", "run"):
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        return command, file.read()

def parenthesize(name, *args):
    return f'({name}' + (' ' if args else '') + ' '.join(map(str, args)) + ')'

def to_str(value, preserve_int=False):
    if value is None:
        return 'nil'
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    if preserve_int and isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)

def are_number_operands(left, right):
    return isinstance(left, float) and isinstance(right, float)

def either_numbers_or_strings_operands(left, right):
    if isinstance(left, float) and isinstance(right, float):
        return True
    if isinstance(left, str) and isinstance(right, str):
        return True
    return False

def is_truthy(value):
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    return True

def is_equal(left, right):
    return left == right
