

class ValidTypes:
    Integer = 'Integer'
    Float64 = 'Float64'
    Boolean = 'Bool'
    String  = 'String'


class FunctionSymbol:
    def __init__(self, name: str, return_type: str) -> None:
        self.name: str = name
        self.return_type: str = return_type
        self.parameter_types: list[str] = []
        self.local_variables: dict[str, str] = {}

    def add_parameter(self, name: str, value: str) -> bool:
        self.parameter_types.append(value)
        return self.add_local_variable(name, value)

    def add_local_variable(self, name: str, type: str) -> bool:
        if name in self.local_variables:
            return False
        self.local_variables[name] = type
        return True

    def __str__(self) -> str:
        s_str = f"----- function -----\n\t{self.name} @ {self.return_type}\n"
        if self.parameter_types:
            s_str+= f"parameter types:\n\t{','.join(self.parameter_types)}\n"
        if not self.local_variables:
            return s_str
        s_str+= f"local variables:\n"
        for l_name, l_type in self.local_variables.items():
            s_str+= f"\t{l_name} : {l_type}\n"
        
        return s_str


class SymbolTable:
    def __init__(self) -> None:
        self.functions: dict[str, FunctionSymbol] = {}

    def add_function(self, name: str, return_type: str) -> bool:
        if name in self.functions:
            return False
        self.functions[name] = FunctionSymbol(name, return_type)
        return True

    def get_function(self, name: str) -> FunctionSymbol:
        return self.functions.get(name)

    def get_local_variable(self, f_name: str, v_name: str) -> str:
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return None
        return f_symbol.local_variables.get(v_name)

    def add_parameter(self, f_name: str, v_name: str, v_type: str) -> bool:
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return False
        return f_symbol.add_parameter(v_name, v_type)

    def add_local_variable(self, f_name: str, v_name: str, v_type: str) -> bool:
        f_symbol: FunctionSymbol = self.get_function(f_name)
        if f_symbol is None:
            return False
        return f_symbol.add_local_variable(v_name, v_type)

