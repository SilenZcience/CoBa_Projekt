"""
defines helpful utility for the typechecker/code-generator.
"""

class ValidTypes:
    """
    define all valid types (like 'type_spec' in the Parser-Grammar)
    """
    Integer: str = 'Integer'
    Float64: str = 'Float64'
    Boolean: str = 'Bool'
    String : str = 'String'


class FunctionSymbol:
    """
    define a function
    """
    def __init__(self, f_name: str, f_type: str) -> None:
        self.f_name: str = f_name
        self.f_type: str = f_type
        # dictionaries are since Python >= 3.6 in order (important)
        self.parameters: dict[str, str] = {}
        self.local_variables: dict[str, str] = {}
        self.has_return: bool = False

    def add_parameter(self, p_name: str, p_type: str) -> bool:
        """
        add parameter (parameters are also local variables)
        """
        if p_name in self.parameters:
            return False
        self.parameters[p_name] = p_type
        return self.add_local_variable(p_name, p_type)

    def add_local_variable(self, v_name: str, v_type: str) -> bool:
        """
        add local variable
        """
        if v_name in self.local_variables:
            return False
        self.local_variables[v_name] = v_type
        return True

    def add_return(self) -> None:
        """
        check if cuntion has a return statement
        """
        self.has_return = True

    def __str__(self) -> str:
        s_str: str = f"----- function -----\n\t{self.f_name} -> {self.f_type}\n"
        if self.parameters:
            s_str+= 'parameters:\n'
            for p_name, p_type in self.parameters.items():
                s_str+= f"\t{p_name}: {p_type}\n"
        if not self.local_variables:
            return s_str
        s_str+= 'local variables:\n'
        for l_name, l_type in self.local_variables.items():
            s_str+= f"\t{l_name}: {l_type}\n"
        return s_str


class SymbolTable:
    """
    define interface to manage all functions
    """
    def __init__(self) -> None:
        self.functions: dict[str, FunctionSymbol] = {}

    def add_function(self, f_name: str, f_type: str) -> bool:
        """
        add a function via name and type
        """
        if f_name in self.functions:
            return False
        self.functions[f_name] = FunctionSymbol(f_name, f_type)
        return True

    def get_function(self, f_name: str) -> FunctionSymbol:
        """
        get a function by name
        """
        return self.functions.get(f_name)

    def get_local_variable(self, f_name: str, v_name: str) -> str:
        """
        get a local variable by function- and variable name
        """
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return None
        return f_symbol.local_variables.get(v_name)

    def add_parameter(self, f_name: str, v_name: str, v_type: str) -> bool:
        """
        add a parameter by function name and parameter name and type
        """
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return False
        return f_symbol.add_parameter(v_name, v_type)

    def add_local_variable(self, f_name: str, v_name: str, v_type: str) -> bool:
        """
        add a local variable by function name and parameter name and type
        """
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return False
        return f_symbol.add_local_variable(v_name, v_type)
