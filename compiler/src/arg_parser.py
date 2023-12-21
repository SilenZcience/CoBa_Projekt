import os
from argparse import ArgumentParser
from pathlib import Path

try:
    from compiler import __doc__
except ModuleNotFoundError:
    from __init__ import __doc__

class ArgParser:
    def __init__(self) -> None:
        self.parser = ArgumentParser(description=__doc__)
        self.input_file: Path = None
        self.output_file: Path = None
        self.debug: bool = False
        # True -> Compile
        # False -> Liveness
        self.compile: bool = True


    def parse(self) -> None:
        self.parser.add_argument('-compile', type=lambda p: Path(p).absolute(),
                                 metavar='FILE',
                                 help='compile the defined input file.')
        self.parser.add_argument('-liveness', type=lambda p: Path(p).absolute(),
                                 metavar='FILE',
                                 help='Not yet implemented!')
        self.parser.add_argument('-output', type=lambda p: Path(p).absolute(),
                                 metavar='FILE',
                                 help='specify the output file.')
        self.parser.add_argument('-debug', action='store_true')
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
                print('Warning: Specified output file already exists:', self.output_file)
