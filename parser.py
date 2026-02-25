from tokens import T
from constants import (
    K_EOF,
    K_SYMBOL,
    K_LEFT_PAREN,
    K_RIGHT_PAREN,
    K_LEFT_BRACKET,
    K_RIGHT_BRACKET,
    K_STRING,
    K_NUMBER,
    K_SEMI_COLON,
    K_LT,
    K_GT,
    K_EQ,
    K_NOTEQ,
    K_PLUS_PLUS,
    K_MINUS_MINUS,
)
from nodes import (
    N_FUNCTION_CALL,
    N_FUNCTION_CALL_ARG,
    N_IF_STATEMENT,
    N_FOR_LOOP,
    N_FN
)
from utils import error


class Parser:
    def __init__(self, tokens):
        self.tokens: list[T] = tokens
        self.cursor = 0
        self.size = len(self.tokens)
        self.nodes = []

    def token(self):
        if self.cursor < self.size:
            return self.tokens[self.cursor]

        return None

    def ttoken(self):
        return self.tokens[self.cursor + 1]

    def has_next_token(self):
        return self.cursor < self.size - 1

    def next_token(self):
        self.cursor += 1

    def expect_current(self, kind):
        token = self.token()

        if token is None:
            error(f'missing token {kind}')

        if self.token().kind != kind:
            error(f'expected "{kind}" but received "{token.kind}"')

    def expect_next(self, *kinds):
        if self.cursor >= self.size:
            error(f'missing next token {" or ".join(kinds)}')

        nxt = self.tokens[self.cursor + 1]

        found = False
        for kind in kinds:
            if nxt.kind == kind:
                found = True
                break

        if not found:
            error(f'expected "{" or ".join(kinds)}" but received "{nxt.kind}"')

        self.next_token()

        return nxt

    def parse_function_call(self):
        name = self.token()
        self.expect_next(K_LEFT_PAREN)

        self.next_token()

        arguments = []

        while self.token() is not None and self.token().kind != K_RIGHT_PAREN:
            token = self.token()

            if token.kind == K_STRING:
                arguments.append(N_FUNCTION_CALL_ARG(token.name, K_STRING))
            elif token.kind == K_NUMBER:
                arguments.append(N_FUNCTION_CALL_ARG(token.name, K_NUMBER))
            else:
                error(f'unhandled data type {token.kind}')

            self.next_token()

        self.expect_current(K_RIGHT_PAREN)
        self.expect_next(K_SEMI_COLON)

        return N_FUNCTION_CALL(name.name, arguments)

    def parse_for_loop(self):
        start_value = self.expect_next(K_NUMBER)
        az = self.expect_next(K_SEMI_COLON, K_SYMBOL)
        var_name = None
        if az.kind == K_SYMBOL:
            if az.name != 'as':
                error(f'invalid syntax {az.name}')

            var_name = self.expect_next(K_SYMBOL)
            self.expect_next(K_SEMI_COLON)
        # condition. hardcoded for now
        condition = self.expect_next(K_LT, K_GT, K_EQ, K_NOTEQ)
        end_value = self.expect_next(K_NUMBER)
        self.expect_next(K_SEMI_COLON)
        # update. hardcoded for now
        update = self.expect_next(K_PLUS_PLUS, K_MINUS_MINUS)
        self.expect_next(K_LEFT_BRACKET)
        ntoken = self.ttoken()

        var_name = var_name.name if var_name is not None else None

        if ntoken is None:
            error('missing close bracket on for-loop')
        if ntoken.kind == K_RIGHT_BRACKET:
            self.expect_next(K_RIGHT_BRACKET)
            return None

        body = []
        self.next_token()

        while self.token() is not None and self.token().kind != K_RIGHT_BRACKET:
            node = self.parse_expression()
            self.next_token()

            if node is None:
                continue

            body.append(node)

        self.expect_current(K_RIGHT_BRACKET)

        return N_FOR_LOOP(
            var_name,
            int(start_value.name),
            condition.kind,
            int(end_value.name),
            update.kind,
            body
        )

    def parse_if(self):
        # For now, it's hard coded syntax <symbol> <operator> <number>
        var_name = self.expect_next(K_SYMBOL)
        operator = self.expect_next(K_GT, K_LT)
        value = self.expect_next(K_NUMBER)
        self.expect_next(K_LEFT_BRACKET)

        ttoken = self.ttoken()

        if ttoken is None:
            error('missing close bracket on if-statement')
        if ttoken.kind == K_RIGHT_BRACKET:
            self.expect_next(K_RIGHT_BRACKET)

            return None

        body = []

        self.next_token()

        while self.token() is not None and self.token().kind != K_RIGHT_BRACKET:
            node = self.parse_expression()
            self.next_token()

            if node is None:
                continue

            body.append(node)

        self.expect_current(K_RIGHT_BRACKET)

        iv = N_IF_STATEMENT(
            var_name.name,
            operator.kind,
            value.name,
            body
        )

        if self.ttoken().kind == K_SYMBOL and self.ttoken().name == 'else':
            self.expect_next(K_SYMBOL)
            self.expect_next(K_LEFT_BRACKET)

            if self.ttoken().kind == K_RIGHT_BRACKET:
                self.expect_next(K_RIGHT_BRACKET)

                return iv

            self.next_token()

            while self.token() is not None and self.token().kind != K_RIGHT_BRACKET:
                node = self.parse_expression()
                self.next_token()

                if node is None:
                    continue

                iv.elze_block.append(node)

            self.expect_current(K_RIGHT_BRACKET)

        return iv

    def parse_fn(self):
        fn_name = self.expect_next(K_SYMBOL)
        self.expect_next(K_LEFT_PAREN)
        self.expect_next(K_RIGHT_PAREN)
        self.expect_next(K_LEFT_BRACKET)

        if self.ttoken().kind == K_RIGHT_BRACKET:
            self.expect_next(K_RIGHT_BRACKET)

            return N_FN(
                fn_name.name,
                []
            )

        self.next_token()

        body = []

        while self.token() is not None and self.token().kind != K_RIGHT_BRACKET:
            node = self.parse_expression()
            self.next_token()

            if node is None:
                raise Exception('this check should never occur')

            body.append(node)

        self.expect_current(K_RIGHT_BRACKET)

        return N_FN(
            fn_name.name,
            body
        )


    def parse_symbol(self):
        token = self.token()

        if token.name == 'for':
            return self.parse_for_loop()
        if token.name == 'if':
            return self.parse_if()
        if token.name == 'fn':
            return self.parse_fn()

        if not self.has_next_token():
            error(f'invalid use of symbol "{token.name}"')

        ttoken = self.ttoken()

        if ttoken.kind == K_LEFT_PAREN:
            return self.parse_function_call()

        error(f'unexpected syntax "{ttoken.name}"')

    def parse_expression(self):
        token = self.token()

        if token.kind == K_SYMBOL:
            return self.parse_symbol()
        elif token.kind == K_EOF:
            return None
        else:
            error(f'unrecognized symbol {token.kind}')

    def parse(self):
        while self.cursor < self.size:
            node = self.parse_expression()

            self.next_token()

            if node is None:
                continue
            else:
                self.nodes.append(node)

        return self.nodes
