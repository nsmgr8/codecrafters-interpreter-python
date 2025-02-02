from enum import StrEnum, auto
import string
import sys
from dataclasses import dataclass
from typing import Any, NamedTuple


has_errors = False

class ParseError(Exception):
    ...

class TokenType(StrEnum):
    @staticmethod
    def _generate_next_value_(name, *_args):
        return name.upper()

    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    STAR = auto()
    SLASH = auto()
    DOT = auto()
    COMMA = auto()
    PLUS = auto()
    MINUS = auto()
    SEMICOLON = auto()
    EQUAL = auto()
    BANG = auto()
    LESS = auto()
    GREATER = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    EOF = auto()
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FOR = auto()
    FUN = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()


RESERVED_WORDS = {
    'and': TokenType.AND,
    'class': TokenType.CLASS,
    'else': TokenType.ELSE,
    'false': TokenType.FALSE,
    'for': TokenType.FOR,
    'fun': TokenType.FUN,
    'if': TokenType.IF,
    'nil': TokenType.NIL,
    'or': TokenType.OR,
    'print': TokenType.PRINT,
    'return': TokenType.RETURN,
    'super': TokenType.SUPER,
    'this': TokenType.THIS,
    'true': TokenType.TRUE,
    'var': TokenType.VAR,
    'while': TokenType.WHILE,
}

ONE_OR_TWO_CHAR_TOKENS = {
    '(': TokenType.LEFT_PAREN,
    ')': TokenType.RIGHT_PAREN,
    '{': TokenType.LEFT_BRACE,
    '}': TokenType.RIGHT_BRACE,
    '*': TokenType.STAR,
    '/': TokenType.SLASH,
    '.': TokenType.DOT,
    ',': TokenType.COMMA,
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    ';': TokenType.SEMICOLON,
    '=': TokenType.EQUAL,
    '!': TokenType.BANG,
    '<': TokenType.LESS,
    '>': TokenType.GREATER,
    '==': TokenType.EQUAL_EQUAL,
    '!=': TokenType.BANG_EQUAL,
    '<=': TokenType.LESS_EQUAL,
    '>=': TokenType.GREATER_EQUAL,
}

COMPARISON_TOKEN_START = '=!<>'
NUMBER_TOKEN_CHARS = '.' + string.digits
IDENTIFIER_TOKEN_START = string.ascii_letters + '_'
IDENTIFIER_TOKEN_CHARS = IDENTIFIER_TOKEN_START + string.digits
RESERVED_WORDS_START = set(w[0] for w in RESERVED_WORDS)


def set_error(line_no, msg, where=""):
    global has_errors
    has_errors = True
    sys.stderr.write(f'[line {line_no}] Error{where}: {msg}\n')


def get_code():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command not in ("tokenize", "parse"):
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        return command, file.read()

def parenthesize(name, *args):
    return f'({name}' + (' ' if args else '') + ' '.join(args) + ')'


class Token(NamedTuple):
    type: TokenType
    lexeme: str
    literal: str | float | bool | None
    line: int = 0

    def __str__(self) -> str:
        return f'{self.type} {self.lexeme} {self.literal}'

class Expr:
    def accept(self) -> str:
        return ''

@dataclass
class Literal(Expr):
    value: Any = None

    def accept(self):
        return 'nil' if self.value is None else str(self.value)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self):
        return parenthesize(self.operator.lexeme, self.right.accept())


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self):
        return parenthesize(self.operator.lexeme, self.left.accept(), self.right.accept())

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self):
        return parenthesize('group', self.expression.accept())

class AST:
    def print(self, expression):
        return expression and expression.accept()

class Tokenizer:
    def __init__(self, code, log=False):
        self.log = log
        self.scan(code)

    def add_token(self, token_type, lexeme, literal, line):
        token = Token(token_type, lexeme, literal, line)
        self.tokens.append(token)
        if self.log:
            print(token)


    def scan(self, code):
        def next_match(char):
            if col_no < len(line) and (c := line[col_no]) == char:
                return c

        def string_literal():
            end = line.find('"', col_no)
            if end > 0:
                s = line[col_no:end]
                self.add_token(TokenType.STRING, f'"{s}"', s, line_no)
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
                self.add_token(TokenType.NUMBER, n, float(n), line_no)
            return len(n) - 1

        def idetifier():
            i = 0
            for i, cc in enumerate(line[col_no:]):
                if cc not in IDENTIFIER_TOKEN_CHARS:
                    break
            n = line[col_no-1:col_no+i]
            self.add_token(TokenType.IDENTIFIER, n, 'null', line_no)
            return len(n) - 1

        def reserved():
            rest = line[col_no-1:]
            for w in RESERVED_WORDS:
                if rest.startswith(w):
                    self.add_token(RESERVED_WORDS[w], w, 'null', line_no)
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
                    self.add_token(token, c, 'null', line_no)

        self.add_token(TokenType.EOF, '',  'null', -1)


class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens

    def parse(self):
        self.current = 0
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True

    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def is_at_end(self):
        return self.peek().type == 'EOF'

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self):
        return self.tokens[self.current - 1]

    def peek(self):
        return self.tokens[self.current]

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal('false')
        if self.match(TokenType.TRUE):
            return Literal('true')
        if self.match(TokenType.NIL):
            return Literal('nil')

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        # self.synchronize()
        raise self.error("Expect expression.")

    def consume(self, type, msg):
        if self.check(type):
            return self.advance()

        raise self.error(msg)

    def error(self, msg):
        token = self.peek()
        if token.type == TokenType.EOF:
            where = " at end"
        else:
            where = f" at '{token.lexeme}'"
        set_error(token.line, msg, where)

        return ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return

            self.advance()


def _test():
    expression = Binary(
        left=Unary(
            operator=Token(TokenType.MINUS, "-", 'null', 1),
            right=Literal(123)
        ),
        operator=Token(TokenType.STAR, "*", 'null', 1),
        right=Grouping(Literal(45.67))
    )

    print(AST().print(expression))



def main():
    command, code = get_code()
    tokenizer = Tokenizer(code, command == 'tokenize')
    if command == 'parse':
        tree = Parser(tokenizer.tokens).parse()
        print(AST().print(tree))

    if has_errors:
        raise SystemExit(65)



if __name__ == "__main__":
    main()
