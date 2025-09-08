#!/usr/bin/env python3
import os
import random
import subprocess
import hashlib
import sys

program_name = sys.argv[0]

if len(sys.argv) != 2:
    print(f'usage: {program_name} program.sas')
    exit(1)

input_file = sys.argv[1]

CHARS_ARRAY = (
    ['_'] +
    [c for c in 'asdfghjklqwertyuiopzxcvbnm'] +
    [c for c in 'ASDFGHJKLQWERTYUIOPZXCVBNM']
)
CHARS = set(
    CHARS_ARRAY
)
NUMBERS = '0123456789'
K_EOF = 'eof'
K_SYMBOL = 'sym'
K_LEFT_PAREN = 'lparen'
K_RIGHT_PAREN = 'rparen'
K_LEFT_BRACKET = 'lbracket'
K_RIGHT_BRACKET = 'rbracket'
K_STRING = 'str'
K_NUMBER = 'int'
K_SEMI_COLON = 'semicol'
K_EQUAL = 'equal'
K_LT = 'lt'
K_GT = 'gt'
K_EQ = 'eq'
K_NOTEQ = 'neq'
K_PLUS = 'plus'
K_PLUS_PLUS = 'plusplus'
K_MINUS_MINUS = 'minusminus'

NK_FUNCTION_CALL = 'funcall'
NK_FOR_LOOP = 'for_loop'
NK_IF_STATEMENT = 'if'


def get_program_without_extension():
    name = input_file.strip()

    if name.endswith('.sas'):
        return name[:-4]

    return name


def generate_random_string(length):
    random_string = ''.join(random.choice(CHARS_ARRAY) for _ in range(length))
    return random_string


def error(text):
    sys.stderr.write(text + '\n')
    exit(1)


class T:
    def __init__(self):
        self.name: str
        self.kind: str


class T_EOF(T):
    def __init__(self):
        self.name = 'EOF'
        self.kind = K_EOF


class T_SYMBOL(T):
    def __init__(self, name):
        self.name = name
        self.kind = K_SYMBOL


class T_LEFT_PAREN(T):
    def __init__(self):
        self.name = '('
        self.kind = K_LEFT_PAREN


class T_RIGHT_PAREN(T):
    def __init__(self):
        self.name = '('
        self.kind = K_RIGHT_PAREN


class T_LEFT_BRACKET(T):
    def __init__(self):
        self.name = '{'
        self.kind = K_LEFT_BRACKET


class T_RIGHT_BRACKET(T):
    def __init__(self):
        self.name = '}'
        self.kind = K_RIGHT_BRACKET


class T_STRING(T):
    def __init__(self, name):
        self.name = name
        self.kind = K_STRING


class T_NUMBER(T):
    def __init__(self, value):
        self.name = int(value)
        self.kind = K_NUMBER


class T_SEMI_COLON(T):
    def __init__(self):
        self.name = ';'
        self.kind = K_SEMI_COLON


class T_EQUAL(T):
    def __init__(self):
        self.name = '='
        self.kind = K_EQUAL


class T_LT(T):
    def __init__(self):
        self.name = '<'
        self.kind = K_LT


class T_GT(T):
    def __init__(self):
        self.name = '>'
        self.kind = K_GT


class T_NOTEQ(T):
    def __init__(self):
        self.name = '!='
        self.kind = K_NOTEQ


class T_EQ(T):
    def __init__(self):
        self.name = '=='
        self.kind = K_EQ


class T_PLUS(T):
    def __init__(self):
        self.name = '+'
        self.kind = K_PLUS


class T_PLUS_PLUS(T):
    def __init__(self):
        self.name = '++'
        self.kind = K_PLUS_PLUS


class T_MINUS_MINUS(T):
    def __init__(self):
        self.name = '--'
        self.kind = K_MINUS_MINUS


class Tokenizer:
    def __init__(self, content):
        self.content = content
        self.cursor = 0
        self.size = len(self.content)
        self.bot = 0
        self.tokens = []

    def chr(self):
        if self.cursor >= self.size:
            return None

        return self.content[self.cursor]

    def nchr(self):
        if self.cursor + 1 >= self.size:
            return None

        return self.content[self.cursor + 1]

    def advance_cursor(self):
        if self.cursor < self.size:
            self.cursor += 1

    def is_space(self, chr):
        return chr in ' \r\n\t'

    def is_symbol(self, chr):
        return chr in CHARS

    def is_number(self, chr):
        return chr in NUMBERS

    def trim_whitespaces(self):
        while self.chr() is not None and self.is_space(self.chr()):
            self.advance_cursor()

    def tokenize_symbol(self):
        while self.is_symbol(self.chr()):
            self.advance_cursor()

        self.tokens.append(T_SYMBOL(self.content[self.bot:self.cursor]))

    def tokenize_single(self):
        match self.chr():
            case '(': self.tokens.append(T_LEFT_PAREN())
            case ')': self.tokens.append(T_RIGHT_PAREN())
            case ';': self.tokens.append(T_SEMI_COLON())
            case '=':
                if self.nchr() == '=':
                    self.tokens.append(T_EQ())
                    self.advance_cursor()
                else:
                    self.tokens.append(T_EQUAL())
            case '<': self.tokens.append(T_LT())
            case '>': self.tokens.append(T_GT())
            case '!':
                if self.nchr() == '=':
                    self.tokens.append(T_NOTEQ())
                    self.advance_cursor()
                else:
                    error(f'unrecognized character {self.chr()}')
            case '{': self.tokens.append(T_LEFT_BRACKET())
            case '}': self.tokens.append(T_RIGHT_BRACKET())
            case '-':
                if self.nchr() == '-':
                    self.tokens.append(T_MINUS_MINUS())
                    self.advance_cursor()
                else:
                    error(f'unrecognized character {self.chr()}')
            case '+':
                if self.nchr() == '+':
                    self.tokens.append(T_PLUS_PLUS())
                    self.advance_cursor()
                else:
                    self.tokens.append(T_PLUS())
            case _: error(f'unrecognized single token {self.chr()}')

        self.advance_cursor()

    def tokenize_string(self):
        self.advance_cursor()

        while self.chr() is not None and self.chr() != "'":
            self.advance_cursor()

        if self.chr() != "'":
            error(f'unterminated string at position {self.bot + 1}')

        self.tokens.append(T_STRING(self.content[self.bot+1:self.cursor]))

        self.advance_cursor()

    def tokenize_number(self):
        while self.chr() is not None and self.is_number(self.chr()):
            self.advance_cursor()

        self.tokens.append(T_NUMBER(self.content[self.bot:self.cursor]))

    def trim_comment(self):
        while self.chr() is not None and self.chr() != '\n':
            self.advance_cursor()

    def tokenize(self):
        while True:
            self.trim_whitespaces()

            self.bot = self.cursor

            if self.chr() is None:
                self.tokens.append(T_EOF())
                break
            elif self.chr() == '#':
                self.trim_comment()
            elif self.is_number(self.chr()):
                self.tokenize_number()
            elif self.is_symbol(self.chr()):
                self.tokenize_symbol()
            elif self.chr() in '();=<>+{}!-':
                self.tokenize_single()
            elif self.chr() == "'":
                self.tokenize_string()
            else:
                error(f'unrecognized char {self.chr()}')

        return self.tokens


class N_FUNCTION_CALL_ARG:
    def __init__(self, value, kind):
        self.value = value
        self.kind = kind


class N_FUNCTION_CALL:
    def __init__(self, name, arguments: list[N_FUNCTION_CALL_ARG]):
        self.name = name
        self.kind = NK_FUNCTION_CALL
        self.arguments = arguments


class N_FOR_LOOP:
    def __init__(self, var_name, start, condition, end, update, body=[]):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.condition = condition
        self.update = update
        self.kind = NK_FOR_LOOP
        self.body = body


class N_IF_STATEMENT:
    def __init__(self, var_name, operator, value, body):
        self.kind = NK_IF_STATEMENT
        self.var_name = var_name
        self.operator = operator
        self.value = value
        self.body = body


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

        return N_IF_STATEMENT(
            var_name.name,
            operator.kind,
            value.name,
            body
        )

    def parse_symbol(self):
        token = self.token()

        if token.name == 'for':
            return self.parse_for_loop()
        if token.name == 'if':
            return self.parse_if()

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


class Compiler:
    def __init__(self, nodes):
        self.code = [
            'global _start',
            'section .text',
            '_start:',
        ]
        self.data = [
            'section .data'
        ]
        self.nodes = nodes
        self.data_references = {}
        self.var_to_reg = {}

    def get_string_reference(self, string, linebreak):
        string_hash = string
        if linebreak:
            string_hash = string_hash + '<br/>'

        hash = '_' + hashlib.sha1(string_hash.encode('utf-8')).hexdigest()[:12]

        if hash in self.data_references:
            return self.data_references[hash]

        string_data_name = hash.replace('-', '')

        if linebreak:
            self.data.append(f'{string_data_name} db "{string}", 0x0A')
        else:
            self.data.append(f'{string_data_name} db "{string}"')

        self.data_references[hash] = string_data_name

        return string_data_name

    def compile_function_call(self, fn: N_FUNCTION_CALL, scope):
        # builtin functions
        if fn.name == 'println':
            if len(fn.arguments) != 1:
                error(f'print expects only one argument but got {len(fn.arguments)}')
            if fn.arguments[0].kind != K_STRING:
                error(f'print expects one argument as string but got {fn.arguments[0].kind}')

            string_data_name = self.get_string_reference(
                fn.arguments[0].value,
                True
            )

            self.code.append('mov rax,0x01')
            self.code.append('mov rdi,0x01')
            self.code.append(f'mov rsi,{string_data_name}')
            self.code.append(f'mov rdx,{len(fn.arguments[0].value) + 1}')
            self.code.append('syscall')
        elif fn.name == 'print':
            if len(fn.arguments) != 1:
                error(f'print expects only one argument but got {len(fn.arguments)}')
            if fn.arguments[0].kind != K_STRING:
                error(f'print expects one argument as string but got {fn.arguments[0].kind}')

            string_data_name = self.get_string_reference(
                fn.arguments[0].value,
                False
            )

            self.code.append('mov rax,0x01')
            self.code.append('mov rdi,0x01')
            self.code.append(f'mov rsi,{string_data_name}')
            self.code.append(f'mov rdx,{len(fn.arguments[0].value)}')
            self.code.append('syscall')
        elif fn.name == 'exit':
            if len(fn.arguments) != 1:
                error(f'exit expects only one argument but got {len(fn.arguments)}')
            if fn.arguments[0].kind != K_NUMBER:
                error(f'exit expects one argument as number but got {fn.arguments[0].kind}')

            self.code.append('mov rax,0x3c')
            self.code.append(f'mov rdi,{fn.arguments[0].value}')
            self.code.append('syscall')
        else:
            error(f'function "{fn.name}" does not exists')

    def compile_for_loop(self, loop: N_FOR_LOOP, scope):
        loop_label = generate_random_string(10)

        if loop_label not in self.var_to_reg:
            self.var_to_reg[loop_label] = {}

        if loop.var_name is not None:
            self.var_to_reg[loop_label][loop.var_name] = 'rcx'

        self.code.append(f'push {loop.start}')
        self.code.append(f'{loop_label}:')
        self.code.append('pop rcx')
        self.code.append('push rcx')
        for node in loop.body:
            self.compile_node(node, loop_label)
        self.code.append('pop rbx')
        if loop.update == K_PLUS_PLUS:
            self.code.append('inc rbx')
        elif loop.update == K_MINUS_MINUS:
            self.code.append('dec rbx')
        self.code.append('push rbx')
        self.code.append(f'cmp rbx,{loop.end}')
        if loop.condition == K_EQ:
            self.code.append(f'je {loop_label}')
        elif loop.condition == K_NOTEQ:
            self.code.append(f'jne {loop_label}')
        elif loop.condition == K_LT:
            self.code.append(f'jl {loop_label}')
        elif loop.condition == K_GT:
            self.code.append(f'jg {loop_label}')
        else:
            error(f'invalid condition {loop.condition}')
        self.code.append('pop rbx')

    def compile_if(self, node: N_IF_STATEMENT, scope):
        if node.var_name not in self.var_to_reg[scope]:
            error(f'variable "{node.var_name}" not found')

        reg = self.var_to_reg[scope][node.var_name]

        end_if_label = generate_random_string(10)

        self.code.append(f'cmp {reg},{node.value}')
        if node.operator == K_LT:
            self.code.append(f'jge {end_if_label}')
        elif node.operator == K_GT:
            self.code.append(f'jle {end_if_label}')
        for node in node.body:
            self.compile_node(node, scope)
        self.code.append(f'{end_if_label}:')

    def exit(self):
        self.code.append('mov rax,0x3c')
        self.code.append('mov rdi,0x00')
        self.code.append('syscall')

    def compile_node(self, node, scope):
        if node.kind == NK_FUNCTION_CALL:
            self.compile_function_call(node, scope)
        elif node.kind == NK_FOR_LOOP:
            self.compile_for_loop(node, scope)
        elif node.kind == NK_IF_STATEMENT:
            self.compile_if(node, scope)
        else:
            error(f'unhandled node kind {node.kind}')

    def compile(self):
        for node in self.nodes:
            self.compile_node(node, 'root')

        self.exit()

        tmp_file_name = generate_random_string(12)
        tmp_file_path = f'/tmp/{tmp_file_name}'
        tmp_out_file_path = f'/tmp/{tmp_file_name}.o'
        compiled_name = get_program_without_extension()

        with open(tmp_file_path, 'w') as f:
            for line in self.code:
                f.write(line)
                f.write('\n')
            for line in self.data:
                f.write(line)
                f.write('\n')
            f.close()

        compile_code = subprocess.call([
            'nasm',
            '-felf64',
            f'{tmp_file_path}',
            '-o',
            f'{tmp_out_file_path}'
        ])

        if compile_code != 0:
            error(f'compilation failed with return code {compile_code}')

        link_code = subprocess.call([
            'ld',
            f'{tmp_out_file_path}',
            '-o',
            f'./{compiled_name}'
        ])

        if link_code != 0:
            error(f'linking failed with return code {link_code}')

        os.remove(tmp_file_path)
        os.remove(tmp_out_file_path)


content = open(input_file, 'r').read()

tokenizer = Tokenizer(content)

tokens = tokenizer.tokenize()

parser = Parser(tokens)

nodes = parser.parse()

compiler = Compiler(nodes)

compiler.compile()
