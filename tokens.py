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
    K_EQUAL,
    K_LT,
    K_GT,
    K_EQ,
    K_NOTEQ,
    K_PLUS,
    K_PLUS_PLUS,
    K_MINUS_MINUS,
)


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
