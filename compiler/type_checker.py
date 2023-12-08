"""
define a type checker
"""
import sys
from antlr4.ParserRuleContext import ParserRuleContext

try:
    from compiler.src.JuliaParser import JuliaParser
    from compiler.src.JuliaParserListener import JuliaParserListener
    from compiler.type_checker_helper import ValidTypes, SymbolTable
except ModuleNotFoundError:
    from src.JuliaParser import JuliaParser
    from src.JuliaParserListener import JuliaParserListener
    from type_checker_helper import ValidTypes, SymbolTable


class TypeStack:
    """
    define a stack containing the types of the traversed nodes
    """
    def __init__(self) -> None:
        self.type_stack: list[str] = []

    def push(self, new_type: str) -> None:
        self.type_stack.append(new_type)

    def pop(self) -> str:
        return self.type_stack.pop() if self.type_stack else None

    def __str__(self) -> str:
        return str(self.type_stack)


class TypeChecker(JuliaParserListener):
    """
    Type Checker for:
    - (Boolsche) Expressions
    - Function Calls (Checks arguments against parameters)
    - Declarations
    - Assignements
    - Function return types
    """
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table: SymbolTable = symbol_table
        self.type_stack: TypeStack = TypeStack()
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


    def exitReturn_statement(self, ctx: JuliaParser.Return_statementContext):
        r_type: str = self.type_stack.pop()
        f_type: str = self.symbol_table.get_function(self.current_function).f_type
        if r_type != f_type:
            self.err_print(ctx, f"invalid return type of function: '{self.current_function}', " + \
                f"expected: '{f_type}', got: '{r_type}'.")

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
        if len(argument_type_list) < len(f_table.parameter_types):
            return self.err_print(ctx, f"too few arguments provided at function call: '{f_name}'")

        current_argument_count: int = 0
        current_argument = ctx.function_argument()
        while current_argument is not None:
            a_type: str = argument_type_list[current_argument_count]
            p_type: str = f_table.parameter_types[current_argument_count]
            if p_type != a_type and (p_type != ValidTypes.Float64 or a_type != ValidTypes.Integer):
                self.err_print(current_argument, f"wrong argument type: '{a_type}', " + \
                    f"expected: '{p_type}'")
            current_argument_count += 1
            current_argument = current_argument.function_argument()

        self.type_stack.push(f_table.f_type)

    def exitDeclaration(self, ctx):
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = ctx.type_assignement().type_spec().getText()
        assigned_type: str = self.type_stack.pop()
        if v_type != assigned_type and \
            (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', " + \
                f"expected: '{v_type}', got: '{assigned_type}'")

    def exitAssignement(self, ctx):
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = self.symbol_table.get_local_variable(self.current_function, v_name)
        assigned_type: str = self.type_stack.pop()
        if v_type is None:
            return self.err_print(ctx, f"used variable without declaration: '{v_name}'")
        if v_type != assigned_type and \
            (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', " + \
                f"expected: '{v_type}', got: '{assigned_type}'")

    def exitBool_expression(self, ctx):
        ex_type: str = self.type_stack.pop()
        if ex_type != ValidTypes.Boolean:
            self.err_print(ctx, "expression must evaluate to bool type.")

    def exitExpression(self, ctx):
        if ctx.UNARY is not None:
            ex_type: str = self.type_stack.pop()
            if (ctx.T_PLUS() or ctx.T_MINUS()) is not None:
                if ex_type in [ValidTypes.Integer, ValidTypes.Float64]:
                    self.type_stack.push(ex_type)
                else:
                    self.err_print(ctx, 'unsupported operand type(s) for ' + \
                        f"{ctx.T_PLUS() or ctx.T_MINUS()}: '{ex_type}'.")
            elif ctx.T_EXCLAMATION() is not None:
                if ex_type == ValidTypes.Boolean:
                    self.type_stack.push(ex_type)
                else:
                    self.err_print(ctx, 'unsupported operand type(s) for ' + \
                        f"{ctx.T_EXCLAMATION()}: '{ex_type}'.")
            else:
                self.err_print(ctx, 'Fatal Error: unknown unary operation.')
        elif (ctx.T_STAR() or ctx.T_SLASH() or ctx.T_PERCENT() or ctx.T_PLUS() or ctx.T_MINUS()) is not None:
            ex_type_a: str = self.type_stack.pop()
            ex_type_b: str = self.type_stack.pop()
            if ex_type_a == ex_type_b == ValidTypes.Integer:
                self.type_stack.push(ValidTypes.Integer)
            elif ex_type_a in [ValidTypes.Integer, ValidTypes.Float64] and \
                ex_type_b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.push(ValidTypes.Float64)
            else:
                self.err_print(ctx, 'unsupported operand type(s) for ' + \
                    f"{ctx.T_STAR() or ctx.T_SLASH() or ctx.T_PERCENT() or ctx.T_PLUS() or ctx.T_MINUS()}: " + \
                    f"'{ex_type_b}' and '{ex_type_a}'.")
        elif (ctx.T_NOTEQUAL() or ctx.T_D_EQUAL()) is not None:
            ex_type_a: str = self.type_stack.pop()
            ex_type_b: str = self.type_stack.pop()
            if ex_type_a in [ValidTypes.Integer, ValidTypes.Float64] and \
               ex_type_b in [ValidTypes.Integer, ValidTypes.Float64] or \
                   ex_type_a == ex_type_b == ValidTypes.String:
                self.type_stack.push(ValidTypes.Boolean)
            else:
                self.err_print(ctx, 'unsupported operand type(s) for ' + \
                    f"{ctx.T_NOTEQUAL() or ctx.T_D_EQUAL()}: '{ex_type_b}' and '{ex_type_a}'.")
        elif (ctx.T_LESS() or ctx.T_GREATER() or ctx.T_LESSEQUAL() or ctx.T_GREATEREQUAL()) is not None:
            ex_type_a: str = self.type_stack.pop()
            ex_type_b: str = self.type_stack.pop()
            if ex_type_a in [ValidTypes.Integer, ValidTypes.Float64] and \
               ex_type_b in [ValidTypes.Integer, ValidTypes.Float64]:
                self.type_stack.push(ValidTypes.Boolean)
            else:
                self.err_print(ctx, 'unsupported operand type(s) for ' + \
                    f"{ctx.T_LESS() or ctx.T_GREATER() or ctx.T_LESSEQUAL() or ctx.T_GREATEREQUAL()}: " + \
                    f"'{ex_type_b}' and '{ex_type_a}'.")
        elif (ctx.T_D_AND() or ctx.T_D_VBAR()) is not None:
            ex_type_a = self.type_stack.pop()
            ex_type_b = self.type_stack.pop()
            if ex_type_a == ex_type_b == ValidTypes.Boolean:
                self.type_stack.push(ValidTypes.Boolean)
            else:
                self.err_print(ctx, 'unsupported operand type(s) for ' + \
                    f"{ctx.T_D_AND() or ctx.T_D_VBAR()}: '{ex_type_b}' and '{ex_type_a}'.")
        elif (ctx.atom() or ctx.function_call()) is not None:
            pass
        else:
            self.err_print(ctx, 'Fatal Error: unknown expresion.')

    def exitAtom(self, ctx):
        if ctx.IDENTIFIER() is not None:
            self.type_stack.push(self.symbol_table.get_local_variable(
                self.current_function, ctx.IDENTIFIER().getText()))

    def exitType_element(self, ctx):
        if ctx.INTEGER_NUMBER() is not None:
            self.type_stack.push(ValidTypes.Integer)
        elif ctx.FLOAT_NUMBER() is not None:
            self.type_stack.push(ValidTypes.Float64)
        elif ctx.STRING() is not None:
            self.type_stack.push(ValidTypes.String)
        elif (ctx.K_TRUE() or ctx.K_FALSE()) is not None:
            self.type_stack.push(ValidTypes.Boolean)





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