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

comp_start = '=!<>'
num_chars = '.' + string.digits
ident_start = string.ascii_letters + '_'
ident_chars = ident_start + string.digits


class Tokenizer:
    def __init__(self, code):
        self.scan(code)

    def scan(self, code):
        def next_match(char):
            if col_no < len(line) and (c := line[col_no]) == char:
                return c

        def string_literal():
            end = line.find('"', col_no)
            if end > 0:
                s = line[col_no:end]
                self.tokens.append(f'STRING "{s}" {s}')
                return len(s) + 1
            self.set_error(line_no, 'Unterminated string.')

        def number():
            i = 0
            for i, cc in enumerate(line[col_no:]):
                if cc not in num_chars:
                    break
            n = line[col_no-1:col_no+i]
            if n.endswith('.') or len([x for x in n if x == '.']) > 1:
                self.set_error(line_no, f'Invalid number {n}')
            else:
                self.tokens.append(f'NUMBER {n} {float(n)}')
            return len(n) - 1

        def idetifier():
            i = 0
            for i, cc in enumerate(line[col_no:]):
                if cc not in ident_chars:
                    break
            n = line[col_no-1:col_no+i]
            self.tokens.append(f'IDENTIFIER {n} null')
            return len(n) - 1


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

                if c in comp_start and (next_c := next_match('=')):
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

                if c in ident_start:
                    skip = idetifier()
                    continue

                if (token := LEXER.get(c)) is None:
                    self.set_error(line_no, f'Unexpected character: {c}')
                else:
                    self.tokens.append(token)

        self.tokens.append('EOF  null')

    def set_error(self, line_no, msg):
        self.has_errors = True
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

def main():
    code = get_code()
    tokenizer = Tokenizer(code)
    for token in tokenizer.tokens:
        print(token)

    if tokenizer.has_errors:
        raise SystemExit(65)



if __name__ == "__main__":
    main()
