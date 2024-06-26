"""
define the ErrorListener
"""

from antlr4.error.ErrorListener import ConsoleErrorListener

class ErrorListener(ConsoleErrorListener):
    """
    default ConsoleErrorListener but saves the occurence of an error
    """
    def __init__(self):
        super().__init__()
        self.has_errors = False

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.has_errors = True
        super().syntaxError(recognizer, offendingSymbol, line, column, msg, e)
