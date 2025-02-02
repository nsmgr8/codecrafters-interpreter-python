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
    '-': 'MINUS - null',
    ';': 'SEMICOLON ; null',
}

class Tokenizer:
    def __init__(self, code):
        self.scan(code)

    def scan(self, code):
        self.tokens = []
        for line_no, line in enumerate(code.splitlines(), 1):
            for _col_no, c in enumerate(line, 1):
                self.tokens.append(LEXER.get(c, f'[line {line_no}] Error: Unexpected character: {c}'))
        self.tokens.append('EOF null')


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
        code = file.read()

    tokenizer = Tokenizer(code)
    for token in tokenizer.tokens:
        print(token)



if __name__ == "__main__":
    main()
