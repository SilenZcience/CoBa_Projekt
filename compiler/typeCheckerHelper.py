
import sys

class ValidTypes():
    Integer = 'Integer'
    Float64 = 'Float64'
    String  = 'String'
    Boolean = 'Boolean'

def err_print(ctx, *args, **kwargs):
    """
    print to stderr.
    """
    print(f"line {ctx.start.line}:{ctx.start.column} ", end='', file=sys.stderr, **kwargs)
    print(*args, file=sys.stderr, flush=True, **kwargs)

class FunctionSymbol:
    def __init__(self, name: str, return_type: str, parameter_types: list[str]):
        self.name: str = name
        self.return_type: str = return_type
        self.parameter_types: list[str] = parameter_types
        self.local_variables: dict = {}

    def add_local():
        pass


class SymbolTable:
    def __init__(self):
        self.has_errors = False
        self.functions: dict[str, FunctionSymbol] = {}

    def add_function(self, name: str, return_type: str, parameter_types: list[str]):
        if name in self.functions:
            self.has_errors = True
            return
        self.functions[name] = FunctionSymbol(name, return_type, parameter_types)

    def get_function(self, name):
        return self.functions.get(name)


