import sys


LEXER = {
    '(': 'LEFT_PAREN ( null',
    ')': 'RIGHT_PAREN ) null',
    '{': 'LEFT_BRACE { null',
    '}': 'RIGHT_BRACE } null',
    '*': 'STAR * null',
    '.': 'DOT . null',
    ',': 'COMMA , null',
    '+': 'PLUS + null',
    '-': 'MINUS + null',
    ';': 'SEMICOLON + null',
    None: 'EOF  null',
}


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.read()

    for c in file_contents:
        print(LEXER.get(c))

    print("EOF  null")


if __name__ == "__main__":
    main()
