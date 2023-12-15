"""
python -m pip install antlr4-python3-runtime==4.13.1
java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/src/CoBaLexer.g4 ./compiler/src/CoBaParser.g4 -o ./compiler/src
python ./compiler/stups_compiler.py -compile test.jl
"""

import sys
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

try: # package import (python -m compiler ...)
    from compiler.src.CoBaLexer import CoBaLexer
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.arg_parser import ArgParser
    from compiler.src.errorListener import ErrorListener
    from compiler.src.symbol_table_gen_listener import SymbolTableGenListener
    from compiler.src.type_checker import TypeChecker
    from compiler.src.type_checker_helper import SymbolTable
except ModuleNotFoundError: # default import (python ./compiler/main.py ...)
    from src.CoBaLexer import CoBaLexer
    from src.CoBaParser import CoBaParser
    from src.arg_parser import ArgParser
    from src.errorListener import ErrorListener
    from src.symbol_table_gen_listener import SymbolTableGenListener
    from src.type_checker import TypeChecker
    from src.type_checker_helper import SymbolTable


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


def main() -> int:
    """
    main method - implements compiler frontend (for now)
    """
    arg_parser: ArgParser = ArgParser()
    arg_parser.parse()
    status_print('reading file', arg_parser.compile_file if (
        arg_parser.compile) else arg_parser.liveness_file
    )
    if not arg_parser.compile:
        status_print('-Error-', 'liveness is not yet implemented')
        return 1

    status_print('parsing...')
    error_listener: ErrorListener = ErrorListener()

    input_stream: FileStream = FileStream(arg_parser.compile_file, encoding='utf-8')
    lexer: CoBaLexer = CoBaLexer(input_stream)
    stream: CommonTokenStream = CommonTokenStream(lexer)
    parser: CoBaParser = CoBaParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    tree: CoBaParser.MainContext = parser.main()
    if error_listener.has_errors:
        return 1
    status_print('parsing successful.')

    status_print('typechecking...')
    symbol_table: SymbolTable = SymbolTable()
    symbol_table_gen_listener: SymbolTableGenListener = SymbolTableGenListener(symbol_table)
    type_checker: TypeChecker = TypeChecker(symbol_table)
    walker: ParseTreeWalker = ParseTreeWalker()

    walker.walk(symbol_table_gen_listener, tree)
    if symbol_table_gen_listener.has_errors:
        return 2

    walker.walk(type_checker, tree)
    if type_checker.has_errors:
        return 3
    status_print('typechecking successful.')


if __name__ == '__main__':
    sys.exit(main())

# DEBUG:
# python -m pip install antlr4-tools
# antlr4-parse .\compiler\src\CoBaLexer.g4 .\compiler\src\CoBaParser.g4 main -gui .\Testcases\pos\test00.jl
