from constants import NK_FUNCTION_CALL, NK_FOR_LOOP, NK_IF_STATEMENT


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
        self.elze_block = []
