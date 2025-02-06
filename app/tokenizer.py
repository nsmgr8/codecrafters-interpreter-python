from enum import StrEnum, auto
import string
import sys
from typing import NamedTuple
from app import error


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


class Token(NamedTuple):
    type: TokenType
    lexeme: str
    literal: str | float | bool | None
    line: int = 0

    def __str__(self) -> str:
        return f'{self.type} {self.lexeme} {self.literal}'

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
            error.set_error(line_no, 'Unterminated string.')

        def number():
            i = current_idx
            while i < n_code and code[i] in NUMBER_TOKEN_CHARS:
                i += 1
            num = code[current_idx:i]
            if num.endswith('.') or len([x for x in num if x == '.']) > 1:
                error.set_error(line_no, f'Invalid number {num}')
            else:
                self.add_token(TokenType.NUMBER, num, float(num), line_no)
            return len(num)

        def idetifier():
            i = current_idx
            while i < n_code and code[i] in IDENTIFIER_TOKEN_CHARS:
                i += 1
            ident = code[current_idx:i]
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
                error.set_error(line_no, f'Unexpected character: {c}')
                current_idx += 1
            else:
                self.add_token(token, c, 'null', line_no)
                current_idx += len(c)

        self.add_token(TokenType.EOF, '',  'null', -1)
        return self.tokens
