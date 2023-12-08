"""
python -m pip install antlr4-python3-runtime==4.13.1
java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/src/CoBaLexer.g4 ./compiler/src/CoBaParser.g4 -o ./compiler/src
python ./compiler/main.py test.txt
"""

import sys
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

try: # package import (python -m compiler ...)
    from compiler.src.CoBaLexer import CoBaLexer
    from compiler.src.CoBaParser import CoBaParser
    from compiler.arg_parser import ArgParser
    from compiler.errorListener import ErrorListener
    from compiler.symbol_table_gen_listener import SymbolTableGenListener
    from compiler.type_checker import TypeChecker
    from compiler.type_checker_helper import SymbolTable
except ModuleNotFoundError: # default import (python ./compiler/main.py ...)
    from src.CoBaLexer import CoBaLexer
    from src.CoBaParser import CoBaParser
    from arg_parser import ArgParser
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
    except Exception:
        debug_hook(exception_type, exception, traceback)

sys.excepthook = exception_handler


def status_print(msg: str, *args, **kwargs) -> None:
    """
    print to stdout.
    """
    print(f"Status: {msg}", *args, end='\n', file=sys.stdout, **kwargs)


def main():
    """
    main method - implements compiler frontend (for now)
    """
    arg_parser = ArgParser()
    arg_parser.parse()
    status_print('reading file', arg_parser.compile_file if (
        arg_parser.compile) else arg_parser.liveness_file
    )
    if not arg_parser.compile:
        status_print('-Error-', 'liveness is not yet implemented')
        sys.exit(1)

    status_print('parsing...')
    error_listener = ErrorListener()

    input_stream = FileStream(arg_parser.compile_file, encoding='utf-8')
    lexer = CoBaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CoBaParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree = parser.main()
    if error_listener.has_errors:
        sys.exit(1)
    status_print('parsing successful.')

    status_print('typechecking...')
    symbol_table = SymbolTable()
    symbol_table_gen_listener = SymbolTableGenListener(symbol_table)
    type_checker = TypeChecker(symbol_table)
    walker = ParseTreeWalker()

    walker.walk(symbol_table_gen_listener, tree)
    if symbol_table_gen_listener.has_errors:
        sys.exit(2)

    walker.walk(type_checker, tree)
    if type_checker.has_errors:
        sys.exit(3)
    status_print('typechecking successful.')


if __name__ == '__main__':
    main()

# DEBUG: antlr4-parse .\compiler\src\CoBaLexer.g4 .\compiler\src\CoBaParser.g4 main -gui .\Testcases\input1.txt
