"""
define a type checker
"""
import sys
from antlr4.ParserRuleContext import ParserRuleContext

try:
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.CoBaParserListener import CoBaParserListener
    from compiler.src.type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol
except ModuleNotFoundError:
    from .CoBaParser import CoBaParser
    from .CoBaParserListener import CoBaParserListener
    from .type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol


class TypeStack:
    """
    define a stack containing the types of the traversed nodes
    """
    def __init__(self) -> None:
        self.type_stack: list[str] = []

    def push(self, new_type: str) -> None:
        """
        push on top of stack (right side of list)
        """
        self.type_stack.append(new_type)

    def pop(self) -> str:
        """
        pop from top of stack (default is None)
        """
        return self.type_stack.pop() if self.type_stack else None

    def __str__(self) -> str:
        return str(self.type_stack)


class TypeChecker(CoBaParserListener):
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
        self.current_function: FunctionSymbol = None
        self.has_errors: bool = False

    def err_print(self, ctx: ParserRuleContext, *args, **kwargs) -> None:
        """
        print to stderr.
        """
        print(f"line {ctx.start.line}:{ctx.start.column} ", end='', file=sys.stderr, **kwargs)
        print(*args, file=sys.stderr, flush=True, **kwargs)
        self.has_errors = True

    def exitMain_function_header(self, ctx: CoBaParser.Main_function_headerContext) -> None:
        f_name: str = ctx.K_MAIN().getText()
        self.current_function = self.symbol_table.get_function(f_name)

    def exitFunction_header(self, ctx: CoBaParser.Function_headerContext) -> None:
        f_name: str = ctx.IDENTIFIER().getText()
        self.current_function = self.symbol_table.get_function(f_name)

    def exitFunction_body(self, ctx: CoBaParser.Function_bodyContext) -> None:
        if self.current_function.f_type is not None and not self.current_function.has_return:
            self.err_print(ctx, 'invalid control flow in function: ' + \
                f"'{self.current_function.f_name}', missing return statement.")

    def exitReturn_statement(self, ctx: CoBaParser.Return_statementContext) -> None:
        if ctx.expression() is None:
            self.type_stack.push(None)
        r_type: str = self.type_stack.pop()
        self.symbol_table.add_return(self.current_function.f_name)
        if r_type != self.current_function.f_type:
            self.err_print(ctx, 'invalid return type of function: ' + \
                f"'{self.current_function.f_name}', expected: '{self.current_function.f_type}', got: '{r_type}'.")

    def exitFunction_call(self, ctx: CoBaParser.Function_callContext) -> None:
        f_name: str = (ctx.IDENTIFIER() or ctx.K_MAIN()).getText()

        f_table: FunctionSymbol = self.symbol_table.get_function(f_name)
        if f_table is None:
            return self.err_print(ctx, f"unknown function called: '{f_name}'.")

        argument_type_list: list[str] = []
        current_argument = ctx.function_argument()
        while current_argument is not None:
            argument_type_list.insert(0, self.type_stack.pop())
            current_argument = current_argument.function_argument()

        if len(argument_type_list) > len(f_table.parameters):
            return self.err_print(ctx, f"too many arguments provided at function call: '{f_name}'.")
        if len(argument_type_list) < len(f_table.parameters):
            return self.err_print(ctx, f"too few arguments provided at function call: '{f_name}'.")

        current_argument_count: int = 0
        current_argument = ctx.function_argument()
        while current_argument is not None:
            a_type: str = argument_type_list[current_argument_count]
            p_type: str = [*f_table.parameters.values()][current_argument_count]
            if p_type != a_type:
                self.err_print(current_argument, f"wrong argument type: '{a_type}', " + \
                    f"expected: '{p_type}'.")
            current_argument_count += 1
            current_argument = current_argument.function_argument()

        self.type_stack.push(f_table.f_type)

    def exitDeclaration(self, ctx: CoBaParser.DeclarationContext) -> None:
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = ctx.type_assignement().type_spec().getText()
        assigned_type: str = self.type_stack.pop()
        if v_type != assigned_type and \
            (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', " + \
                f"expected: '{v_type}', got: '{assigned_type}'.")

    def exitAssignement(self, ctx: CoBaParser.AssignementContext) -> None:
        v_name: str = ctx.IDENTIFIER().getText()
        v_type: str = self.symbol_table.get_local_variable(self.current_function.f_name, v_name)
        assigned_type: str = self.type_stack.pop()
        if v_type is None:
            self.err_print(ctx, f"used variable without declaration: '{v_name}'.")
        elif v_type != assigned_type and \
            (v_type != ValidTypes.Float64 or assigned_type != ValidTypes.Integer):
            self.err_print(ctx, f"wrong value type for variable: '{v_name}', " + \
                f"expected: '{v_type}', got: '{assigned_type}'.")

    def exitBool_expression(self, ctx: CoBaParser.Bool_expressionContext) -> None:
        ex_type: str = self.type_stack.pop()
        if ex_type != ValidTypes.Boolean:
            self.err_print(ctx, "expression must evaluate to bool type.")

    def exitExpression(self, ctx: CoBaParser.ExpressionContext) -> None:
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
               ex_type_a == ex_type_b:
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

    def exitAtom(self, ctx: CoBaParser.AtomContext) -> None:
        if ctx.IDENTIFIER() is not None:
            v_type: str = self.symbol_table.get_local_variable(
                self.current_function.f_name, ctx.IDENTIFIER().getText())
            if v_type is not None:
                self.type_stack.push(v_type)
            else:
                self.err_print(ctx, f"used variable without declaration: '{ctx.IDENTIFIER()}'.")

    def exitType_element(self, ctx: CoBaParser.Type_elementContext) -> None:
        if ctx.INTEGER_NUMBER() is not None:
            self.type_stack.push(ValidTypes.Integer)
        elif ctx.FLOAT_NUMBER() is not None:
            self.type_stack.push(ValidTypes.Float64)
        elif ctx.STRING() is not None:
            self.type_stack.push(ValidTypes.String)
        elif (ctx.K_TRUE() or ctx.K_FALSE()) is not None:
            self.type_stack.push(ValidTypes.Boolean)
