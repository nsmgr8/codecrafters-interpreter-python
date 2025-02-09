from .interpreter import Interpreter
from . import error, utils


def main():
    command, code = utils.get_code()
    interpreter = Interpreter(code)
    match command:
        case 'tokenize':
            interpreter.tokenize(True)
        case 'parse':
            with error.handled_error():
                if expression := interpreter.parse():
                    print(expression)
        case 'evaluate':
            with error.handled_error():
                if (tree := interpreter.parse()) is not None:
                    print(utils.to_str(tree.evaluate(), True))
        case 'run':
            with error.handled_error():
                interpreter.interpret()

    if error.error_code:
        raise SystemExit(error.error_code)



if __name__ == "__main__":
    main()
