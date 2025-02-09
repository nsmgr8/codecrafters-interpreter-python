from .interpreter import Interpreter
from . import error, utils


def main():
    command, code = utils.get_code()
    match command:
        case 'tokenize':
            Interpreter(code).tokenize(True)
        case 'parse':
            with error.handled_error():
                if expression := Interpreter(code).parse():
                    print(expression)
        case 'evaluate':
            with error.handled_error():
                if (tree := Interpreter(code).parse()) is not None:
                    print(utils.to_str(tree.evaluate(), True))
        case 'run':
            with error.handled_error():
                Interpreter(code).interpret()

    if error.error_code:
        raise SystemExit(error.error_code)



if __name__ == "__main__":
    main()
