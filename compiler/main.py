"""
python -m pip install antlr4-python3-runtime==4.13.1
java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/src/JuliaLexer.g4 ./compiler/src/JuliaParser.g4 -o ./compiler/src
python ./compiler/main.py test.txt
"""

import sys
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

try: # package import (python -m compiler ...)
    from compiler.src.JuliaLexer import JuliaLexer
    from compiler.src.JuliaParser import JuliaParser
    from compiler.errorListener import ErrorListener
    from compiler.symbol_table_gen_listener import SymbolTableGenListener
    from compiler.type_checker import TypeChecker
    from compiler.type_checker_helper import SymbolTable
except ModuleNotFoundError: # default import (python ./compiler/main.py ...)
    from src.JuliaLexer import JuliaLexer
    from src.JuliaParser import JuliaParser
    from errorListener import ErrorListener
    from symbol_table_gen_listener import SymbolTableGenListener
    from type_checker import TypeChecker
    from type_checker_helper import SymbolTable


def exception_handler(exception_type: type, exception, traceback,
                      debug_hook=sys.excepthook) -> None:
    """
    custom exception handler (ignore every internal error >.<).
    """
    try:
        print(exception, file=sys.stderr)
        # debug_hook(exception_type, exception, traceback)
        # pass
    except Exception:
        debug_hook(exception_type, exception, traceback)

sys.excepthook = exception_handler


def main():
    """
    main method - implements compiler frontend (for now)
    """
    # TODO: actual argv menu
    error_listener = ErrorListener()

    input_stream = FileStream(sys.argv[1])
    lexer = JuliaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JuliaParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    tree = parser.main()

    if error_listener.has_errors:
        sys.exit(1)

    symbol_table = SymbolTable()
    symbol_table_gen_listener = SymbolTableGenListener(symbol_table)
    type_checker = TypeChecker(symbol_table)
    walker = ParseTreeWalker()

    walker.walk(symbol_table_gen_listener, tree)
    # for function in symbol_table.functions.values():
    #     print(function)
    if symbol_table_gen_listener.has_errors:
        sys.exit(2)

    walker.walk(type_checker, tree)
    if type_checker.has_errors:
        sys.exit(3)


if __name__ == '__main__':
    main()

# DEBUG: antlr4-parse .\compiler\src\JuliaLexer.g4 .\compiler\src\JuliaParser.g4 main -gui .\Testcases\input1.txt
