"""
define SymbolTableCreaterListener
"""

import sys
from antlr4.ParserRuleContext import ParserRuleContext

try:
    from compiler.src.CoBaParserListener import CoBaParserListener
    from compiler.type_checker_helper import SymbolTable
except ModuleNotFoundError:
    from src.CoBaParserListener import CoBaParserListener
    from type_checker_helper import SymbolTable


class SymbolTableGenListener(CoBaParserListener):
    """
    Listener for:
    - Creating a Symbol Table of
    - - Functions
    - - Local Variables (including Parameters)
    """
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table: SymbolTable = symbol_table
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

        if not self.symbol_table.add_function(f_name, None):
            self.err_print(ctx, f"fatal error in function: '{f_name}'.")

        self.current_function = f_name

    def exitFunction_header(self, ctx):
        f_name: str = ctx.IDENTIFIER().getText()
        f_type: str = ctx.type_assignement().type_spec().getText() if (
            ctx.type_assignement()) is not None else None

        if not self.symbol_table.add_function(f_name, f_type):
            self.err_print(ctx, f"duplicate function name: '{f_name}'.")

        current_parameter = ctx.function_parameter()
        while current_parameter is not None:
            current_name: str = current_parameter.IDENTIFIER().getText()
            current_type: str = current_parameter.type_assignement().type_spec().getText()
            if not self.symbol_table.add_parameter(f_name, current_name, current_type):
                self.err_print(current_parameter, 'duplicate variable name: ' + \
                    f"'{current_name}' in scope '{f_name}'")

            current_parameter = current_parameter.function_parameter()

        self.current_function = f_name

    def exitDeclaration(self, ctx):
        v_name = ctx.IDENTIFIER().getText()
        v_type = ctx.type_assignement().type_spec().getText()

        if not self.symbol_table.add_local_variable(self.current_function, v_name, v_type):
            self.err_print(ctx, f"duplicate variable name: '{v_name}'")
