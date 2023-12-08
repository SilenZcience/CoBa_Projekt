import os
import sys
from argparse import ArgumentParser
from pathlib import Path

try:
    from compiler import __doc__
except ModuleNotFoundError:
    from __init__ import __doc__

class ArgParser:
    def __init__(self) -> None:
        self.parser = ArgumentParser(description=__doc__)
        self.compile_file: Path = None
        self.liveness_file: Path = None
        self.output_file: Path = None

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
        params = self.parser.parse_args()

        self.compile_file = getattr(params, 'compile')
        self.liveness_file = getattr(params, 'liveness')
        self.output_file = getattr(params, 'output')


        self.compile = self.compile_file is not None
        liveness = self.liveness_file is not None

        if self.compile and liveness or \
            not self.compile and not liveness:
            raise ValueError("Please choose between '-compile' and '-liveness'")

        if self.compile:
            self.output_file = Path(os.path.splitext(self.compile_file)[0] + '.j')
            if os.path.isdir(self.output_file):
                raise ValueError('Specified output file is not a file.')
            if os.path.exists(self.output_file):
                raise ValueError('Specified output file already exists.')
