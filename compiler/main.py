"""
python -m pip install antlr4-python3-runtime==4.13.1
java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/src/JuliaLexer.g4 ./compiler/src/JuliaParser.g4 -o ./compiler/src
python ./compiler/main.py test.txt
"""

import sys
from antlr4 import *

from src.JuliaLexer import JuliaLexer
from src.JuliaParser import JuliaParser
from errorListener import ErrorListener
from symbolTableCreaterListener import SymbolTableCreaterListener
from typeChecker import TypeChecker
from typeCheckerHelper import SymbolTable

def exception_handler(exception_type: type, exception, traceback,
                      debug_hook=sys.excepthook) -> None:
    """
    custom exception handler (ignore every internal error >.<).
    TODO: better solution
    """
    try:
        debug_hook(exception_type, exception, traceback)
        pass
    except Exception:
        debug_hook(exception_type, exception, traceback)

sys.excepthook = exception_handler

def main(in_file: str, error_listener_: ErrorListener):
    """
    main method - implements compiler frontend
    """
    input_stream = FileStream(in_file)
    lexer = JuliaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JuliaParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener_)
    return parser.main()

if __name__ == '__main__':
    # TODO: actual argv menu
    error_listener = ErrorListener()
    tree = main(sys.argv[1], error_listener)
    if error_listener.has_errors:
        sys.exit(1)
    symbol_table = SymbolTable()
    symbolTableCreaterListener = SymbolTableCreaterListener(symbol_table)
    typeChecker = TypeChecker(symbol_table)
    walker = ParseTreeWalker()
    walker.walk(symbolTableCreaterListener, tree)
    # for function in symbol_table.functions.values():
    #     print(function)
    if symbolTableCreaterListener.has_errors:
        sys.exit(2)
    walker.walk(typeChecker, tree)
    if typeChecker.has_errors:
        sys.exit(3)

# DEBUG: antlr4-parse .\compiler\src\JuliaLexer.g4 .\compiler\src\JuliaParser.g4 main -gui .\Testcases\input1.txt
