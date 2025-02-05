from enum import StrEnum, auto
import string
import sys
from dataclasses import dataclass
from typing import Any, NamedTuple


error_code = 0

class ParseError(Exception):
    ...

class EvaluationError(Exception):
    def __init__(self, line_no, msg):
        self.line_no = line_no
        self.msg = msg


class StrUpperEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.upper()

class TokenType(StrUpperEnum):
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
    global error_code
    error_code = 65
    sys.stderr.write(f'[line {line_no}] Error{where}: {msg}\n')


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


class Token(NamedTuple):
    type: TokenType
    lexeme: str
    literal: str | float | bool | None
    line: int = 0

    def __str__(self) -> str:
        return f'{self.type} {self.lexeme} {self.literal}'

class Expr:
    def evaluate(self) -> Any:
        return ''

    def is_truthy(self, value):
        return bool(value)

    def is_equal(self, left, right):
        return left == right

@dataclass
class Literal(Expr):
    value: Any = None

    def evaluate(self):
        return self.value

    def __str__(self):
        return to_str(self.value)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def evaluate(self):
        right = self.right.evaluate()
        match self.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                if not isinstance(right, float):
                    raise EvaluationError(self.operator.line, "Operand must be a number.")
                return -right

    def __str__(self):
        return parenthesize(self.operator.lexeme, str(self.right))


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def evaluate(self):
        left = self.left.evaluate()
        right = self.right.evaluate()
        match self.operator.type:
            case TokenType.MINUS:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left - right
            case TokenType.PLUS:
                if not either_numbers_or_strings_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be two numbers or two strings.")
                return left + right
            case TokenType.SLASH:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left / right
            case TokenType.STAR:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left * right
            case TokenType.GREATER:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left > right
            case TokenType.GREATER_EQUAL:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left >= right
            case TokenType.LESS:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left < right
            case TokenType.LESS_EQUAL:
                if not are_number_operands(left, right):
                    raise EvaluationError(self.operator.line, "Operands must be number.")
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)

    def __str__(self):
        return parenthesize(self.operator.lexeme, str(self.left), str(self.right))

@dataclass
class Grouping(Expr):
    expression: Expr

    def evaluate(self):
        return self.expression.evaluate()

    def __str__(self):
        return parenthesize('group', str(self.expression))


class Statement: ...

@dataclass
class Print(Statement):
    expression: Expr

    def evaluate(self):
        value = self.expression.evaluate()
        print(to_str(value, True))

@dataclass
class Expression(Statement):
    expression: Expr

    def evaluate(self):
        self.expression.evaluate()

class AST:
    def __init__(self, expression):
        self.expression = expression

    def print(self):
        if self.expression:
            print(self.expression)

class Tokenizer:
    def __init__(self, debug=False):
        self.debug = debug

    def add_token(self, token_type, lexeme, literal, line):
        token = Token(token_type, lexeme, literal, line)
        self.tokens.append(token)
        if self.debug:
            print(token)


    def scan(self, code):
        def next_match(char):
            next_idx = current_idx + 1
            if next_idx < n_code and (next_c := code[next_idx]) == char:
                return next_c

        def string_literal():
            end = code.find('"', current_idx+1)
            if end > 0:
                s = code[current_idx+1:end]
                self.add_token(TokenType.STRING, f'"{s}"', s, line_no)
                return len(s) + 2
            set_error(line_no, 'Unterminated string.')

        def number():
            i = 0
            for i, cc in enumerate(code[current_idx:]):
                if cc not in NUMBER_TOKEN_CHARS:
                    break
            num = code[current_idx:current_idx+i]
            if num.endswith('.') or len([x for x in num if x == '.']) > 1:
                set_error(line_no, f'Invalid number {num}')
            else:
                try:
                    self.add_token(TokenType.NUMBER, num, float(num), line_no)
                except ValueError:
                    print(num, current_idx, code[current_idx:])
                    for i, cc in enumerate(code[current_idx:]):
                        print('find digit', i, repr(cc))
                        if cc not in NUMBER_TOKEN_CHARS:
                            break
                    for t in self.tokens:
                        print(t)
                    raise
            return len(num)

        def idetifier():
            i = 0
            for i, cc in enumerate(code[current_idx:]):
                if cc not in IDENTIFIER_TOKEN_CHARS:
                    break
            ident = code[current_idx:current_idx+i]
            self.add_token(TokenType.IDENTIFIER, ident, 'null', line_no)
            return len(ident)

        def reserved():
            rest = code[current_idx:]
            for w in RESERVED_WORDS:
                if rest.startswith(w):
                    self.add_token(RESERVED_WORDS[w], w, 'null', line_no)
                    return len(w)


        self.tokens = []
        line_no, current_idx = 1, 0
        n_code = len(code)
        while 0 <= current_idx < n_code:
            c = code[current_idx]
            if c == '\n':
                line_no += 1

            if c in string.whitespace:
                current_idx += 1
                continue

            if c in COMPARISON_TOKEN_START and (next_c := next_match('=')):
                c = c + next_c

            if c == '/' and (next_c := next_match('/')):
                c = c + next_c
                current_idx = code.find('\n', current_idx)
                continue

            if c == '"':
                if skip := string_literal():
                    current_idx += skip
                    continue
                else:
                    break

            if c in string.digits:
                current_idx += number()
                continue

            if c in RESERVED_WORDS_START:
                if skip := reserved():
                    current_idx += skip
                    continue
            if c in IDENTIFIER_TOKEN_START:
                current_idx += idetifier()
                continue

            if (token := ONE_OR_TWO_CHAR_TOKENS.get(c)) is None:
                set_error(line_no, f'Unexpected character: {c}')
                current_idx += 1
            else:
                self.add_token(token, c, 'null', line_no)
                current_idx += len(c)

        self.add_token(TokenType.EOF, '',  'null', -1)
        return self.tokens

def execute(statement):
    statement.evaluate()

class Interpreter:
    def __init__(self, code):
        self.code = code

    def interpret(self):
        for statement in self.parse():
            execute(statement)

    def parse(self, parse_only=False):
        self.tokens = Tokenizer().scan(self.code)
        self.current = 0
        if parse_only:
            try:
                return self.expression()
            except ParseError:
                return

        statements = []
        try:
            while not self.is_at_end():
                statements.append(self.statement())
            return statements
        except ParseError:
            return []

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Print(value)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(value)

    def expression(self):
        return self.equality()

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

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

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
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)


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


def main():
    global error_code
    command, code = get_code()
    match command:
        case 'tokenize':
            Tokenizer(True).scan(code)
        case 'parse':
            AST(Interpreter(code).parse(True)).print()
        case 'evaluate':
            try:
                if (tree := Interpreter(code).parse(True)) is not None:
                    print(to_str(tree.evaluate(), True))
            except EvaluationError as e:
                sys.stderr.write(f'{e.msg}\n[line {e.line_no}]\n')
                error_code = 70
        case 'run':
            Interpreter(code).interpret()

    if error_code:
        raise SystemExit(error_code)



if __name__ == "__main__":
    main()
