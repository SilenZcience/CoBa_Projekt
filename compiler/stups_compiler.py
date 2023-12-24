"""
python -m pip install antlr4-python3-runtime==4.13.1
java -jar ./antlr-4.13.1-complete.jar -Dlanguage=Python3 ./compiler/grammar/CoBaLexer.g4 ./compiler/grammar/CoBaParser.g4 -listener -visitor -o ./compiler/src
python ./compiler/stups_compiler.py -compile test.jl
"""

import sys
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker

try: # package import (python -m compiler ...)
    from compiler.src.CoBaLexer import CoBaLexer
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.arg_parser import ArgParser
    from compiler.src.code_generator import CodeGenerator
    from compiler.src.error_listener import ErrorListener
    from compiler.src.liveness_analysis import LivenessAnalysis
    from compiler.src.symbol_table_gen_listener import SymbolTableGenListener
    from compiler.src.type_checker import TypeChecker
    from compiler.src.type_checker_helper import SymbolTable
except ModuleNotFoundError: # default import (python ./compiler/main.py ...)
    from src.CoBaLexer import CoBaLexer
    from src.CoBaParser import CoBaParser
    from src.code_generator import CodeGenerator
    from src.arg_parser import ArgParser
    from src.error_listener import ErrorListener
    from src.liveness_analysis import LivenessAnalysis
    from src.symbol_table_gen_listener import SymbolTableGenListener
    from src.type_checker import TypeChecker
    from src.type_checker_helper import SymbolTable


def exception_handler(exception_type: type, exception, traceback,
                      debug_hook=sys.excepthook) -> None:
    """
    custom exception handler (ignore traceback).
    """
    try:
        # print(exception, file=sys.stderr)
        debug_hook(exception_type, exception, traceback)
    except Exception:
        debug_hook(exception_type, exception, traceback)

sys.excepthook = exception_handler


def status_print(msg: str, *args, **kwargs) -> None:
    """
    print to stdout.
    """
    print(f"Status: {msg}", *args, end='\n', file=sys.stdout, **kwargs)


def debug_print(out, desc: str = '') -> None:
    """
    print debug info. (colored)
    """
    print('\x1b[32mDEBUG:', desc)
    print('\x1b[31m====================')
    try:
        if isinstance(out, dict):
            print('\n'.join([str(out[item]) for item in dict(sorted(out.items()))]))
        else:
            print('\n'.join([item for item in out]))
    except TypeError:
        print(out)
    print('====================\x1b[0m\n')


def main() -> int:
    """
    main method - implements compiler
    """
    arg_parser: ArgParser = ArgParser()
    arg_parser.parse()
    status_print('reading file', arg_parser.input_file)

    status_print('parsing...')
    error_listener: ErrorListener = ErrorListener()
    input_stream: FileStream = FileStream(arg_parser.input_file, encoding='utf-8')
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
    if arg_parser.debug:
        debug_print(symbol_table.functions, 'Symbol Table')
    if symbol_table_gen_listener.has_errors:
        return 2
    walker.walk(type_checker, tree)
    if type_checker.has_errors:
        return 3
    status_print('typechecking successful.')

    if arg_parser.compile:
        status_print('generating...')
        code_generator: CodeGenerator = CodeGenerator(symbol_table,
                                                    arg_parser.output_file.stem,
                                                    arg_parser.debug)
        code_generator.visit(tree)
        code_generator.generate(arg_parser.output_file)
        status_print('generating successful.')
    else:
        status_print('liveness...')
        liveness_analysis: LivenessAnalysis = LivenessAnalysis(symbol_table)
        liveness_analysis.visit(tree)
        liveness_analysis.gen_interference_graph()
        if arg_parser.debug:
            debug_print(liveness_analysis.control_flow_graphs,
                        'Control Flow Graphs')
        if arg_parser.debug:
            debug_print(liveness_analysis.register_interference_graphs,
                        'Register Interference Graphs')
        for f_name, ri_graph in liveness_analysis.register_interference_graphs.items():
            print('Function:', f_name)
            print('Registers:', ri_graph.min_registers)
            print(ri_graph)

    return 0


if __name__ == '__main__':
    sys.exit(main())

# DEBUG:
# python -m pip install antlr4-tools
# antlr4-parse ./compiler/grammar/CoBaLexer.g4 ./compiler/grammar/CoBaParser.g4 main -gui test.jl
