import string
import sys
from typing import NamedTuple


has_errors = False

RESERVED_WORDS = (
    'and',
    'class',
    'else',
    'false',
    'for',
    'fun',
    'if',
    'nil',
    'or',
    'print',
    'return',
    'super',
    'this',
    'true',
    'var',
    'while',
)

ONE_OR_TWO_CHAR_TOKENS = {
    '(': 'LEFT_PAREN',
    ')': 'RIGHT_PAREN',
    '{': 'LEFT_BRACE',
    '}': 'RIGHT_BRACE',
    '*': 'STAR',
    '/': 'SLASH',
    '.': 'DOT',
    ',': 'COMMA',
    '+': 'PLUS',
    '-': 'MINUS',
    ';': 'SEMICOLON',
    '=': 'EQUAL',
    '!': 'BANG',
    '<': 'LESS',
    '>': 'GREATER',
    '==': 'EQUAL_EQUAL',
    '!=': 'BANG_EQUAL',
    '<=': 'LESS_EQUAL',
    '>=': 'GREATER_EQUAL',
}

COMPARISON_TOKEN_START = '=!<>'
NUMBER_TOKEN_CHARS = '.' + string.digits
IDENTIFIER_TOKEN_START = string.ascii_letters + '_'
IDENTIFIER_TOKEN_CHARS = IDENTIFIER_TOKEN_START + string.digits
RESERVED_WORDS_START = set(w[0] for w in RESERVED_WORDS)


def set_error(line_no, msg):
    global has_errors
    has_errors = True
    sys.stderr.write(f'[line {line_no}] Error: {msg}\n')


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
        return file.read()


class Token(NamedTuple):
    token_type: str
    lexeme: str
    literal: str
    line: int = 0

    def __str__(self) -> str:
        return f'{self.token_type} {self.lexeme} {self.literal}'

class Tokenizer:
    def __init__(self, code):
        self.scan(code)

    def add_token(self, token_type, lexeme, literal, line=0):
        token = Token(token_type, lexeme, literal, line)
        self.tokens.append(token)
        print(token)


    def scan(self, code):
        def next_match(char):
            if col_no < len(line) and (c := line[col_no]) == char:
                return c

        def string_literal():
            end = line.find('"', col_no)
            if end > 0:
                s = line[col_no:end]
                self.add_token('STRING', f"{s}", s, line_no)
                return len(s) + 1
            set_error(line_no, 'Unterminated string.')

        def number():
            i = 0
            for i, cc in enumerate(line[col_no:]):
                if cc not in NUMBER_TOKEN_CHARS:
                    break
            n = line[col_no-1:col_no+i]
            if n.endswith('.') or len([x for x in n if x == '.']) > 1:
                set_error(line_no, f'Invalid number {n}')
            else:
                self.add_token('NUMBER', n, float(n), line_no)
            return len(n) - 1

        def idetifier():
            i = 0
            for i, cc in enumerate(line[col_no:]):
                if cc not in IDENTIFIER_TOKEN_CHARS:
                    break
            n = line[col_no-1:col_no+i]
            self.add_token('IDENTIFIER', n, 'null')
            return len(n) - 1

        def reserved():
            rest = line[col_no-1:]
            for w in RESERVED_WORDS:
                if rest.startswith(w):
                    self.add_token(w.upper(), w, 'null')
                    return len(w) - 1


        self.tokens = []
        self.has_errors = False
        for line_no, line in enumerate(code.splitlines(), 1):
            line += '\n'
            skip = 0
            for col_no, c in enumerate(line, 1):
                if c in string.whitespace:
                    continue
                if skip:
                    skip -= 1
                    continue

                if c in COMPARISON_TOKEN_START and (next_c := next_match('=')):
                    c = c + next_c
                    skip = 1

                if c == '/' and (next_c := next_match('/')):
                    break

                if c == '"':
                    if skip := string_literal():
                        continue
                    else:
                        break

                if c in string.digits:
                    skip = number()
                    continue

                if c in RESERVED_WORDS_START:
                    if skip := reserved():
                        continue

                if c in IDENTIFIER_TOKEN_START:
                    skip = idetifier()
                    continue

                if (token := ONE_OR_TWO_CHAR_TOKENS.get(c)) is None:
                    set_error(line_no, f'Unexpected character: {c}')
                else:
                    self.add_token(token, c, 'null')

        self.add_token('EOF', '',  'null', -1)



def main():
    code = get_code()
    tokenizer = Tokenizer(code)
    for token in tokenizer.tokens:
        print(token)

    if has_errors:
        raise SystemExit(65)



if __name__ == "__main__":
    main()
