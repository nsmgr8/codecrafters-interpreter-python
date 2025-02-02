import sys
import string


LEXER = {
    '(': 'LEFT_PAREN ( null',
    ')': 'RIGHT_PAREN ) null',
    '{': 'LEFT_BRACE { null',
    '}': 'RIGHT_BRACE } null',
    '*': 'STAR * null',
    '/': 'SLASH / null',
    '.': 'DOT . null',
    ',': 'COMMA , null',
    '+': 'PLUS + null',
    '-': 'MINUS - null',
    ';': 'SEMICOLON ; null',
    '=': 'EQUAL = null',
    '!': 'BANG ! null',
    '<': 'LESS < null',
    '>': 'GREATER > null',
    '==': 'EQUAL_EQUAL == null',
    '!=': 'BANG_EQUAL != null',
    '<=': 'LESS_EQUAL <= null',
    '>=': 'GREATER_EQUAL >= null',
}

maybe_two = '=!<>'



class Tokenizer:
    def __init__(self, code):
        self.scan(code)

    def scan(self, code):
        def next_match(char):
            if col_no < len(line) and (c := line[col_no]) == char:
                return c

        self.tokens = []
        self.has_errors = False
        for line_no, line in enumerate(code.splitlines(), 1):
            skip = 0
            for col_no, c in enumerate(line, 1):
                if c in string.whitespace:
                    continue
                if skip:
                    skip -= 1
                    continue

                if c in maybe_two and (next_c := next_match('=')):
                    c = c + next_c
                    skip += 1

                if c == '/' and (next_c := next_match('/')):
                    break

                if c == '"':
                    end = line.find('"', col_no)
                    s = line[col_no:end]
                    skip += end - col_no
                    self.tokens.append(f'STRING "{s}" {s}')
                    continue

                if (token := LEXER.get(c)) is None:
                    self.has_errors = True
                    sys.stderr.write(f'[line {line_no}] Error: Unexpected character: {c}\n')
                else:
                    self.tokens.append(token)

        self.tokens.append('EOF  null')


def get_code():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        return file.read().strip()

def main():
    code = get_code()
    tokenizer = Tokenizer(code)
    for token in tokenizer.tokens:
        print(token)

    if tokenizer.has_errors:
        raise SystemExit(65)



if __name__ == "__main__":
    main()
