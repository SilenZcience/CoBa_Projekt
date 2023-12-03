"""
Type Checker for:
- (Boolsche) Expressions (on function_call check return_type of function in symbol_table)
- Declarations
- Assignements
- Function Calls (Check arguments against parameters)
- function return types ?!
"""
import sys
from src.JuliaParserListener import JuliaParserListener
from typeCheckerHelper import *


class TypeCheckerB(JuliaParserListener):
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table: SymbolTable = symbol_table
        self.type_stack = []

    def exitExpression(self, ctx):
        t_plus = ctx.T_PLUS()
        t_minus = ctx.T_MINUS()
        t_exclamation = ctx.T_EXCLAMATION()

        t_star = ctx.T_STAR()
        t_slash = ctx.T_SLASH()
        t_percent = ctx.T_PERCENT()

        t_notequal = ctx.T_NOTEQUAL()
        t_d_equal = ctx.T_D_EQUAL()
        t_less = ctx.T_LESS()
        t_greater = ctx.T_GREATER()
        t_lessequal = ctx.T_LESSEQUAL()
        t_greaterequal = ctx.T_GREATEREQUAL()

        t_d_and = ctx.T_D_AND()
        t_d_vbar = ctx.T_D_VBAR()

        identifier = ctx.IDENTIFIER()

        # TODO: on exit_function_call -> append function return type
        if t_plus is not None:
            a = self.type_stack.pop()
            if ctx.UNARY is not None:
                if a in [ValidTypes.Integer, ValidTypes.Float64]:
                    self.type_stack.append(a)
                else:
                    err_print(ctx, f"unsupported operand type(s) for +: '{a.name}'.")
                    sys.exit(1)
                return
            b = self.type_stack.pop()
            if a == b == ValidTypes.Integer:
                self.type_stack.append(ValidTypes.Integer)
            elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Float64)
            else:
                err_print(ctx, f"unsupported operand type(s) for +: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_minus is not None:
            a = self.type_stack.pop()
            if ctx.UNARY is not None:
                if a in [ValidTypes.Integer, ValidTypes.Float64]:
                    self.type_stack.append(a)
                else:
                    err_print(ctx, f"unsupported operand type(s) for -: '{a.name}'.")
                    sys.exit(1)
                return
            b = self.type_stack.pop()
            if a == b == ValidTypes.Integer:
                self.type_stack.append(ValidTypes.Integer)
            elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Float64)
            else:
                err_print(ctx, f"unsupported operand type(s) for -: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_exclamation is not None:
            a = self.type_stack.pop()
            # if ctx.UNARY is not None:
            if a == ValidTypes.Boolean:
                self.type_stack.append(a)
            else:
                err_print(ctx, f"unsupported operand type(s) for !: '{a.name}'.")
                sys.exit(1)
        elif t_star is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a == b == ValidTypes.Integer:
                self.type_stack.append(ValidTypes.Integer)
            elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
                b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Float64)
            else:
                err_print(ctx, f"unsupported operand type(s) for *: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_slash is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
                b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Float64)
            else:
                err_print(ctx, f"unsupported operand type(s) for /: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_percent is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a == b == ValidTypes.Integer:
                self.type_stack.append(ValidTypes.Integer)
            elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
                b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Float64)
            else:
                err_print(ctx, f"unsupported operand type(s) for %: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_notequal is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64] or \
                   a == b == ValidTypes.String:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for !=: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_d_equal is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64] or \
                   a == b == ValidTypes.String:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for ==: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_less is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for <: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_greater is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for >: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_lessequal is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for <=: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_greaterequal is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a in [ValidTypes.Integer, ValidTypes.Float64] and \
               b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for >=: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_d_and is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a == b == ValidTypes.Boolean:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for &&: '{b.name}' and '{a.name}'.")
                sys.exit(1)
        elif t_d_vbar is not None:
            a = self.type_stack.pop()
            b = self.type_stack.pop()
            if a == b == ValidTypes.Boolean:
                self.type_stack.append(ValidTypes.Boolean)
            else:
                err_print(ctx, f"unsupported operand type(s) for ||: '{b.name}' and '{a.name}'.")
                sys.exit(1)






    def exitType_element(self, ctx):
        number = ctx.NUMBER()
        string = ctx.STRING()
        boolean = ctx.K_TRUE()
        if boolean is None:
            boolean = ctx.K_FALSE()
        if number is not None:
            if number.getSymbol().text.isdigit():
                self.type_stack.append(ValidTypes.Integer)
            else:
                self.type_stack.append(ValidTypes.Float64)
        elif string is not None:
            self.type_stack.append(ValidTypes.String)
        elif boolean is not None:
            self.type_stack.append(ValidTypes.Boolean)





def create_def_helper(name):
    def print_self(self, ctx):
        print("DEBUG:", name)
    return print_self

possible_method_list = [method for method in dir(JuliaParserListener) if
                        (method.startswith('enter') or method.startswith('exit'))]
implemented_method_list = [method for method in dir(TypeCheckerB) if
                           (method.startswith('enter') or method.startswith('exit'))]
for method in possible_method_list:
    if getattr(JuliaParserListener, method) != getattr(TypeCheckerB, method, None):
        continue
    # setattr(JuliaTypeChecker, method, create_def_helper(method))
