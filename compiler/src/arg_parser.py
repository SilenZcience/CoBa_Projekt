"""
define console menu - ArgParser
"""

import os
from argparse import ArgumentParser
from pathlib import Path

try:
    from compiler import __doc__
except ModuleNotFoundError:
    from __init__ import __doc__

class ArgParser:
    """
    define the ArgParser for handling the console arguments
    """
    def __init__(self) -> None:
        self.parser = ArgumentParser(description=__doc__)
        self.input_file: Path = None
        self.output_file: Path = None
        self.debug: bool = False
        # True -> Compile
        # False -> Liveness
        self.compile: bool = True


    def parse(self) -> None:
        """
        parse the given arguments
        """
        self.parser.add_argument('-compile', type=lambda p: Path(p).absolute(),
                                 metavar='IN_FILE',
                                 help='compile the given Julia IN_FILE into Jasmin-Bytecode.')
        self.parser.add_argument('-liveness', type=lambda p: Path(p).absolute(),
                                 metavar='IN_FILE',
                                 help='generate a register interference graph for the given IN_FILE.')
        self.parser.add_argument('-output', type=lambda p: Path(p).absolute(),
                                 metavar='OUT_FILE',
                                 help='specify the output OUT_FILE used for compilation.')
        self.parser.add_argument('-debug', action='store_true',
                                 help='show additional debug information.')
        params = self.parser.parse_args()

        compile_file: Path = getattr(params, 'compile')
        liveness_file: Path = getattr(params, 'liveness')
        self.output_file = getattr(params, 'output')
        self.debug = getattr(params, 'debug')

        self.compile = compile_file is not None
        liveness: bool = liveness_file is not None

        if self.compile == liveness:
            raise ValueError("Please choose between '-compile' and '-liveness'.")

        self.input_file = compile_file if compile_file is not None else liveness_file

        f_path, f_ext = os.path.splitext(self.input_file)
        if f_ext != '.jl':
            print("Warning: Input File is not of type '.jl'.")

        if self.compile:
            if self.output_file is None:
                self.output_file = Path(f_path + '.j')
            if os.path.isdir(self.output_file):
                raise ValueError('Specified output file is not a file.')
            if os.path.exists(self.output_file):
                from time import sleep
                print('Warning: Specified output file will be overwritten:', self.output_file)
                if self.output_file.suffix != '.j' or self.output_file == self.input_file:
                    print('continuing in: ')
                    for i in range(3, -1, -1):
                        print(f"{i}...", end='', flush=True)
                        sleep(1)
                    print()
