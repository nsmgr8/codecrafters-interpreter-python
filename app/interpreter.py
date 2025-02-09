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

    # statements
    def declaration(self):
        try:
            if self.match(TokenType.FUN):
                return self.function('function')
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except error.ParseError:
            self.synchronize()
            raise

    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error("Can't have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return statements.Function(name, parameters, body)

    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        else:
            initializer = expressions.Literal()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return statements.Var(name, initializer)

    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        return self.expression_statement()

    def return_statement(self):
        if self.check(TokenType.SEMICOLON):
            value = None
        else:
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return statements.Return(value)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = expressions.Literal(True)
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        else:
            increment = None
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after loop condition.")
        body = self.statement()
        if increment:
            body = statements.Block([body, statements.Expression(increment)])
        body = statements.While(condition, body)
        if initializer:
            body = statements.Block([initializer, body])
        return body


    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return statements.While(condition, body)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then = self.statement()
        if self.match(TokenType.ELSE):
            else_ = self.statement()
        else:
            else_ = None

        return statements.If(condition, then, else_)

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

    # expressions
    def expression(self):
        return self.assignment()

    def or_(self):
        expr = self.and_()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.and_()
            expr = expressions.Logical(expr, op, right)
        return expr

    def and_(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = expressions.Logical(expr, op, right)
        return expr

    def assignment(self):
        expr = self.or_()

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

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee):
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error("Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return expressions.Call(callee, paren, arguments)

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

    # common utils
    def consume(self, type, msg):
        if self.check(type):
            return self.advance()

        raise self.error(msg)

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

    # error utils
    def error(self, msg):
        token = self.peek()
        if token.type == TokenType.EOF:
            where = " at end"
        else:
            where = f" at '{token.lexeme}'"
        raise error.ParseError(token.line, msg, where)

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

