#!/usr/bin/env python3
import os
import subprocess
import hashlib
import sys
from nodes import (
    N_FUNCTION_CALL,
    N_IF_STATEMENT,
    N_FOR_LOOP
)
from constants import (
    K_STRING,
    K_NUMBER,
    K_LT,
    K_GT,
    K_EQ,
    K_NOTEQ,
    K_PLUS_PLUS,
    K_MINUS_MINUS,

    NK_IF_STATEMENT,
    NK_FOR_LOOP,
    NK_FUNCTION_CALL
)
from utils import error, generate_random_string
from lexer import Tokenizer
from parser import Parser

arg_index = 0


def shift():
    global arg_index
    if arg_index >= len(sys.argv):
        return None

    arg_index += 1

    return sys.argv[arg_index - 1]


program_name = shift()
input_file = shift()

if input_file is None:
    print(f'usage: {program_name} <filename> [flags]')
    print('  -o         output filename')
    exit(1)

flags = {}


def get_flag(name):
    if name in flags:
        return flags[name]

    return None


while True:
    flag = shift()

    if flag is None:
        break

    match flag:
        case "-o":
            value = shift()

            if value is None:
                print('missing value for flag -o')
                exit(1)

            flags['-o'] = value
        case _:
            print(f'unrecognized flag "{flag}"')


def get_program_without_extension():
    name = input_file.strip()

    if name.endswith('.sas'):
        return name[:-4]

    return name


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
        for child in node.body:
            self.compile_node(child, scope)

        if len(node.elze_block) > 0:
            end_else_label = generate_random_string(10)

            self.code.append(f'jmp {end_else_label}')
            self.code.append(f'{end_if_label}:')
            for child in node.elze_block:
                self.compile_node(child, scope)
            self.code.append(f'{end_else_label}:')
        else:
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
        compiled_name = get_flag('-o') or get_program_without_extension()

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
