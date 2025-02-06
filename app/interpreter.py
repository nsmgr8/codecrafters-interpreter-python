from .tokenizer import Tokenizer, TokenType
from . import error, statements, expressions

class Interpreter:
    def __init__(self, code):
        self.code = code

    def tokenize(self, debug=False):
        self.tokens = Tokenizer(debug).scan(self.code)
        self.current = 0

    def parse(self):
        self.tokenize()
        return self.expression()

    def interpret(self):
        self.tokenize()
        while not self.is_at_end():
            if stmt := self.declaration():
                stmt.evaluate()

    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except error.ParseError:
            self.synchronize()

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        else:
            initializer = expressions.Literal()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return statements.Var(name, initializer)

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        return self.expression_statement()

    def block(self):
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmts.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements.Block(stmts)

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return statements.Print(value)

    def expression_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return statements.Expression(value)

    def expression(self):
        return self.assignment()

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

    def assignment(self):
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, expressions.Variable):
                name = expr.name
                return expressions.Assignment(name, value)
            raise error.EvaluationError(equals.line_no, 'Invalid assignment target.')
        return expr

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = expressions.Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = expressions.Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = expressions.Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = expressions.Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expressions.Unary(operator, right)

        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return expressions.Literal(False)
        if self.match(TokenType.TRUE):
            return expressions.Literal(True)
        if self.match(TokenType.NIL):
            return expressions.Literal(None)


        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expressions.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return expressions.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expressions.Grouping(expr)

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
        error.set_error(token.line, msg, where)

        return error.ParseError()

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

