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
