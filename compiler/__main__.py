"""
__main__
"""

import sys


try:
    from compiler import stups_compiler
except KeyboardInterrupt:
    sys.exit(404)
except Exception as e:
    print('an error occured while loading the module:', file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(404)


def entry_point():
    """
    run the main program.
    """
    sys.exit(stups_compiler.main())

if __name__ == '__main__':
    entry_point()
