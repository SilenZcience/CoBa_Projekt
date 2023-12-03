"""
Type Checker for:
- Creating a Symbol Table of
- - Functions
- - Local Variables
"""

from src.JuliaParserListener import JuliaParserListener
from typeCheckerHelper import *


class TypeCheckerA(JuliaParserListener):
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table: SymbolTable = symbol_table

    def exitFunction_header(self, ctx):
        name = ctx.IDENTIFIER().getText()
        return_type = ctx.type_assignement().type_spec().getText() if ctx.type_assignement() is not None else None
        # if ctx.type_assignement():
        #     if ctx.type_assignement().type_spec().K_INTEGER():
        #         return_type = ValidTypes.Integer
        #     elif ctx.type_assignement().type_spec().K_FLOAT64():
        #         return_type = ValidTypes.Float64
        #     elif ctx.type_assignement().type_spec().K_BOOL():
        #         return_type = ValidTypes.Boolean
        #     elif ctx.type_assignement().type_spec().K_STRING():
        #         return_type = ValidTypes.String

        parameter_types = []
        current_parameter = ctx.function_parameter()
        while current_parameter is not None:
            parameter_types.append(current_parameter.type_assignement().type_spec().getText())
            current_parameter = current_parameter.function_parameter()

        self.symbol_table.add_function(name, return_type, parameter_types)
        # TODO: add parameters to local vars!


def create_def_helper(name):
    def print_self(self, ctx):
        print("DEBUG:", name)
    return print_self

possible_method_list = [method for method in dir(JuliaParserListener) if
                        (method.startswith('enter') or method.startswith('exit'))]
implemented_method_list = [method for method in dir(TypeCheckerA) if
                           (method.startswith('enter') or method.startswith('exit'))]
for method in possible_method_list:
    if getattr(JuliaParserListener, method) != getattr(TypeCheckerA, method, None):
        continue
    # setattr(JuliaTypeChecker, method, create_def_helper(method))
