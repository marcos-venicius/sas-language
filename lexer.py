from constants import CHARS, NUMBERS
from utils import error
from tokens import (
    T_EOF,
    T_SYMBOL,
    T_LEFT_PAREN,
    T_RIGHT_PAREN,
    T_LEFT_BRACKET,
    T_RIGHT_BRACKET,
    T_STRING,
    T_NUMBER,
    T_SEMI_COLON,
    T_EQUAL,
    T_LT,
    T_GT,
    T_NOTEQ,
    T_EQ,
    T_PLUS,
    T_PLUS_PLUS,
    T_MINUS_MINUS,
)


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
