"""
Type Checker for:
- (Boolsche) Expressions (on function_call check return_type of function in symbol_table)
- Function Calls (Check arguments against parameters)
- Declarations
- Assignements
- function return types ?!
"""
import sys
from antlr4.ParserRuleContext import ParserRuleContext
from src.JuliaParserListener import JuliaParserListener
from typeCheckerHelper import *


class TypeChecker(JuliaParserListener):
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table: SymbolTable = symbol_table
        self.type_stack: list[str] = []
        self.current_function: str = None
        self.has_errors: bool = False

    def err_print(self, ctx: ParserRuleContext, *args, **kwargs) -> None:
        """
        print to stderr.
        """
        print(f"line {ctx.start.line}:{ctx.start.column} ", end='', file=sys.stderr, **kwargs)
        print(*args, file=sys.stderr, flush=True, **kwargs)
        self.has_errors = True

    def exitMain_function_header(self, ctx):
        f_name: str = ctx.K_MAIN().getText()
        self.current_function = f_name

    def exitFunction_header(self, ctx):
        f_name: str = ctx.IDENTIFIER().getText()
        self.current_function = f_name
        print(self.type_stack)

    # def exitExpression(self, ctx):
    #     t_plus = ctx.T_PLUS()
    #     t_minus = ctx.T_MINUS()
    #     t_exclamation = ctx.T_EXCLAMATION()

    #     t_star = ctx.T_STAR()
    #     t_slash = ctx.T_SLASH()
    #     t_percent = ctx.T_PERCENT()

    #     t_notequal = ctx.T_NOTEQUAL()
    #     t_d_equal = ctx.T_D_EQUAL()
    #     t_less = ctx.T_LESS()
    #     t_greater = ctx.T_GREATER()
    #     t_lessequal = ctx.T_LESSEQUAL()
    #     t_greaterequal = ctx.T_GREATEREQUAL()

    #     t_d_and = ctx.T_D_AND()
    #     t_d_vbar = ctx.T_D_VBAR()

    #     identifier = ctx.IDENTIFIER()

    #     # TODO: on exit_function_call -> append function return type
    #     if t_plus is not None:
    #         a = self.type_stack.pop()
    #         if ctx.UNARY is not None:
    #             if a in [ValidTypes.Integer, ValidTypes.Float64]:
    #                 self.type_stack.append(a)
    #             else:
    #                 err_print(ctx, f"unsupported operand type(s) for +: '{a.name}'.")
    #                 sys.exit(1)
    #             return
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Integer:
    #             self.type_stack.append(ValidTypes.Integer)
    #         elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Float64)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for +: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_minus is not None:
    #         a = self.type_stack.pop()
    #         if ctx.UNARY is not None:
    #             if a in [ValidTypes.Integer, ValidTypes.Float64]:
    #                 self.type_stack.append(a)
    #             else:
    #                 err_print(ctx, f"unsupported operand type(s) for -: '{a.name}'.")
    #                 sys.exit(1)
    #             return
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Integer:
    #             self.type_stack.append(ValidTypes.Integer)
    #         elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Float64)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for -: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_exclamation is not None:
    #         a = self.type_stack.pop()
    #         # if ctx.UNARY is not None:
    #         if a == ValidTypes.Boolean:
    #             self.type_stack.append(a)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for !: '{a.name}'.")
    #             sys.exit(1)
    #     elif t_star is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Integer:
    #             self.type_stack.append(ValidTypes.Integer)
    #         elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #             b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Float64)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for *: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_slash is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #             b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Float64)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for /: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_percent is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Integer:
    #             self.type_stack.append(ValidTypes.Integer)
    #         elif a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #             b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Float64)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for %: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_notequal is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64] or \
    #                a == b == ValidTypes.String:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for !=: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_d_equal is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64] or \
    #                a == b == ValidTypes.String:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for ==: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_less is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for <: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_greater is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for >: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_lessequal is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for <=: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_greaterequal is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a in [ValidTypes.Integer, ValidTypes.Float64] and \
    #            b in [ValidTypes.Integer, ValidTypes.Float64]:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for >=: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_d_and is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Boolean:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for &&: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)
    #     elif t_d_vbar is not None:
    #         a = self.type_stack.pop()
    #         b = self.type_stack.pop()
    #         if a == b == ValidTypes.Boolean:
    #             self.type_stack.append(ValidTypes.Boolean)
    #         else:
    #             err_print(ctx, f"unsupported operand type(s) for ||: '{b.name}' and '{a.name}'.")
    #             sys.exit(1)

    def exitFunction_call(self, ctx):
        f_name: str = ctx.IDENTIFIER().getText()
        
        f_table = self.symbol_table.get_function(f_name)
        if f_table is None:
            return self.err_print(ctx, f"unknown function called: '{f_name}'")

        argument_type_list: list[str] = []
        current_argument = ctx.function_argument()
        while current_argument is not None:
            argument_type_list.insert(0, self.type_stack.pop())
            current_argument = current_argument.function_argument()
        
        if len(argument_type_list) > len(f_table.parameter_types):
            return self.err_print(ctx, f"too many arguments provided at function call: '{f_name}'")
        elif len(argument_type_list) < len(f_table.parameter_types):
            return self.err_print(ctx, f"too few arguments provided at function call: '{f_name}'")
        
        current_argument_count: int = 0
        current_argument = ctx.function_argument()
        while current_argument is not None:
            a_type: str = argument_type_list[current_argument_count]
            p_type: str = f_table.parameter_types[current_argument_count]
            if p_type != a_type and (p_type != ValidTypes.Float64 or a_type != ValidTypes.Integer):
                self.err_print(current_argument, f"wrong argument type: '{a_type}', expected: '{p_type}'")
            current_argument_count += 1
            current_argument = current_argument.function_argument()
        
        self.type_stack.append(f_table.return_type)

    def exitDeclaration(self, ctx):
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = ctx.type_assignement().type_spec().getText()
        assigned_type: str = self.type_stack.pop()
        if v_type != assigned_type and (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', expected: '{v_type}', got: '{assigned_type}'")

    def exitAssignement(self, ctx):
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = self.symbol_table.get_local_variable(self.current_function, v_name)
        assigned_type: str = self.type_stack.pop()
        if v_type is None:
            return self.err_print(ctx, f"used variable without declaration: '{v_name}'")
        if v_type != assigned_type and (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', expected: '{v_type}', got: '{assigned_type}'")

    def exitType_element(self, ctx):
        if ctx.INTEGER_NUMBER() is not None:
            self.type_stack.append(ValidTypes.Integer)
        elif ctx.FLOAT_NUMBER() is not None:
            self.type_stack.append(ValidTypes.Float64)
        elif ctx.STRING() is not None:
            self.type_stack.append(ValidTypes.String)
        elif ctx.K_TRUE() is not None or ctx.K_FALSE() is not None:
            self.type_stack.append(ValidTypes.Boolean)





# def create_def_helper(name):
#     def print_self(self, ctx):
#         print("DEBUG:", name)
#     return print_self

# possible_method_list = [method for method in dir(JuliaParserListener) if
#                         (method.startswith('enter') or method.startswith('exit'))]
# implemented_method_list = [method for method in dir(TypeCheckerB) if
#                            (method.startswith('enter') or method.startswith('exit'))]
# for method in possible_method_list:
#     if getattr(JuliaParserListener, method) != getattr(TypeCheckerB, method, None):
#         continue
    # setattr(JuliaTypeChecker, method, create_def_helper(method))
