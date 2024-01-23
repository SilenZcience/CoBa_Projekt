"""
define the CodeGenerator
"""

from antlr4.ParserRuleContext import ParserRuleContext

try:
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.CoBaParserVisitor import CoBaParserVisitor
    from compiler.src.type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol
except ModuleNotFoundError:
    from .CoBaParser import CoBaParser
    from .CoBaParserVisitor import CoBaParserVisitor
    from .type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol


def gen_next_label_id() -> str:
    """
    generator incrementing numbers for distinguishable markers/labels
    """
    id_ = 0
    while True:
        yield str(id_)
        id_ += 1


class StackSize:
    """
    define an object to calculate the stack size
    for .limit stack
    """
    def __init__(self) -> None:
        self.current_stack_size: int = 0
        self.max_stack_size: int = 0

    def reset_stack(self) -> None:
        """
        reset stack size (new stack for each function)
        """
        self.current_stack_size: int = 0
        self.max_stack_size: int = 0

    def increase_stack(self, amount: int = 1) -> None:
        """
        increase stack size (on every push op)
        """
        self.current_stack_size += amount
        self.max_stack_size = max(self.current_stack_size, self.max_stack_size)

    def decrease_stack(self, amount: int = 1) -> None:
        """
        decrease stack size (on every store or eval op)
        """
        self.current_stack_size -= amount

    def get_stack_size(self) -> int:
        """
        get the (max) needed stack size
        """
        return self.max_stack_size

class CodeGenerator(CoBaParserVisitor):
    """
    generate Jasmin ByteCode.
    """
    def __init__(self, symbol_table: SymbolTable, file_name: str, debug: bool) -> None:
        self.symbol_table: SymbolTable = symbol_table
        self.file_name: str = file_name
        self.debug: bool = debug

        self.label_gen = gen_next_label_id()

        self.current_function: FunctionSymbol = None
        self.variable_ids: dict[str, int] = {}
        self.code: str = ''

        self.stack_size = StackSize()

    def generate(self, out_file: str) -> None:
        """
        write the bytecode to a file.
        """
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(self.code)

    def set_var_ids(self, f_vars: dict[str, str]) -> int:
        """
        assign each local variable a distinguishable number/id
        """
        self.variable_ids.clear()
        c_id: int = 0
        for v_name, v_type in f_vars.items():
            self.variable_ids[v_name] = c_id
            # float64 needs two variable spaces
            c_id += 1 + (v_type == ValidTypes.Float64)
        # return number of variables to generate '.limit locals'
        return c_id

    def debug_info(self, ctx: ParserRuleContext, info: str = '', ctx_text: bool = True) -> None:
        """
        add additional info to the generated output
        """
        if not self.debug:
            return
        last_line: int = self.code.rfind('\n')+1
        debug_info = f"; DEBUG: {ctx.start.line}:{ctx.start.column}"
        debug_info += f"-{ctx.stop.line}:{ctx.stop.column}"
        if info:
            debug_info += f"; {info}"
        if ctx_text:
            debug_info += f"; txt = {ctx.getText()}"
        debug_info += '\n'
        self.code = self.code[:last_line] + debug_info + self.code[last_line:]

    def visitMain(self, ctx: CoBaParser.MainContext):
        # generate skeleton code
        self.code += '.bytecode 50.0\n'
        self.code += f".class public {self.file_name}\n"
        self.code += '.super java/lang/Object\n\n'
        self.code += '.method public <init>()V\n'
        self.code += '\taload_0\n'
        self.code += '\tinvokenonvirtual java/lang/Object/<init>()V\n'
        self.code += '\treturn\n'
        self.code += '.end method\n\n'
        self.visitChildren(ctx)

    def visitMain_function(self, ctx:CoBaParser.Main_functionContext):
        # compute a new stack
        self.stack_size.reset_stack()
        self.visitChildren(ctx)
        # set the actually needed stack size
        self.code = self.code.replace('.limit stack -',
                                      f".limit stack {self.stack_size.get_stack_size()}")
        self.code += '.end method\n\n'

    def visitMain_function_header(self, ctx: CoBaParser.Main_function_headerContext):
        current_function_name: str = ctx.K_MAIN().getText()
        self.current_function = self.symbol_table.get_function(current_function_name)
        # main methods have always the same structure in this project
        self.code += '.method public static main([Ljava/lang/String;)V\n'
        local_var_count: int = self.set_var_ids(self.current_function.local_variables)
        self.code += f"\t.limit locals {local_var_count}\n"
        # this line will be replaced later with an actual value:
        self.code += '\t.limit stack -\n\n'

    def visitFunction(self, ctx: CoBaParser.FunctionContext):
        # compute a new stack
        self.stack_size.reset_stack()
        self.visitChildren(ctx)
        # set the actually needed stack size
        self.code = self.code.replace('.limit stack -',
                                      f".limit stack {self.stack_size.get_stack_size()}")
        self.code += '.end method\n\n'

    def visitFunction_header(self, ctx: CoBaParser.Function_headerContext):
        current_function_name: str = ctx.IDENTIFIER().getText()
        self.current_function = self.symbol_table.get_function(current_function_name)
        self.code += f".method public static {current_function_name}("
        # generate the code for parameters
        for p_type in self.current_function.parameters.values():
            if p_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += 'I'
            elif p_type == ValidTypes.Float64:
                self.code += 'D'
            elif p_type == ValidTypes.String:
                self.code += 'Ljava/lang/String;'
        self.code += ')'
        # generate the code for return type
        f_type: str = self.current_function.f_type
        if f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += 'I'
        elif f_type == ValidTypes.Float64:
            self.code += 'D'
        elif f_type == ValidTypes.String:
            self.code += 'Ljava/lang/String;'
        else:
            self.code += 'V'
        self.code += '\n'
        local_var_count: int = self.set_var_ids(self.current_function.local_variables)
        self.code += f"\t.limit locals {local_var_count}\n"
        # this line will be replaced later with an actual value:
        self.code += '\t.limit stack -\n\n'

    def visitFunction_body(self, ctx: CoBaParser.Function_bodyContext):
        self.visitChildren(ctx)
        # in case the function does not have a return statement, we just add one.
        # technically only void functions are allowed to not have one ...
        # but these cases should be cought by the type checker
        if ctx.return_statement() is None:
            self.code += '\treturn\n'

    def visitReturn_statement(self, ctx: CoBaParser.Return_statementContext):
        self.debug_info(ctx, 'return')
        self.visitChildren(ctx)
        # generate code of the return statement based on the function return type
        f_type = self.current_function.f_type
        if f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += '\tireturn\n'
            self.stack_size.decrease_stack(1)
        elif f_type == ValidTypes.Float64:
            self.code += '\tdreturn\n'
            self.stack_size.decrease_stack(2)
        elif f_type == ValidTypes.String:
            self.code += '\tareturn\n'
            self.stack_size.decrease_stack(1)
        else:
            self.code += '\treturn\n'

    def visitFunction_call(self, ctx: CoBaParser.Function_callContext):
        self.debug_info(ctx, 'function_call')
        self.visitChildren(ctx)
        if ctx.IDENTIFIER() is not None:
            f_table: FunctionSymbol = self.symbol_table.get_function(ctx.IDENTIFIER().getText())
            # generate the parameters for the function
            self.code += f"\tinvokestatic {self.file_name}/{f_table.f_name}("
            for p_type in f_table.parameters.values():
                if p_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                    self.code += 'I'
                    self.stack_size.decrease_stack(1)
                elif p_type == ValidTypes.Float64:
                    self.code += 'D'
                    self.stack_size.decrease_stack(2)
                elif p_type == ValidTypes.String:
                    self.code += 'Ljava/lang/String;'
                    self.stack_size.decrease_stack(1)
            self.code += ')'
            # generate the return type
            if f_table.f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += 'I'
                self.stack_size.increase_stack(1)
            elif f_table.f_type == ValidTypes.Float64:
                self.code += 'D'
                self.stack_size.increase_stack(2)
            elif f_table.f_type == ValidTypes.String:
                self.code += 'Ljava/lang/String;'
                self.stack_size.increase_stack(1)
            else:
                self.code += 'V'
            self.code += '\n\n'
            return f_table.f_type
        elif ctx.K_MAIN() is not None:
            # in case the main method gets called recursively we need to create a new
            # (empty) String array
            f_name: str = ctx.K_MAIN().getText()
            self.code += '\ticonst_0\n\tanewarray java/lang/String\n'
            self.code += f"\tinvokestatic {self.file_name}/{f_name}([Ljava/lang/String;)V\n\n"
            self.stack_size.increase_stack(1)
            self.stack_size.decrease_stack(1)
            return None

    def visitDeclaration(self, ctx: CoBaParser.DeclarationContext):
        self.debug_info(ctx, 'declaration')
        e_type: str = self.visit(ctx.expression())
        v_name = ctx.IDENTIFIER().getText()
        v_type = self.current_function.local_variables[v_name]
        v_id = self.variable_ids[v_name]
        # generate the code based on the data type of the variable
        # to store in and the expression to store
        if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += f"\tistore {v_id}\n\n"
            self.stack_size.decrease_stack(1)
        elif v_type == ValidTypes.Float64:
            if e_type == ValidTypes.Integer:
                self.code += '\ti2d\n'
                self.stack_size.increase_stack(1)
            self.code += f"\tdstore {v_id}\n\n"
            self.stack_size.decrease_stack(2)
        elif v_type == ValidTypes.String:
            self.code += f"\tastore {v_id}\n\n"
            self.stack_size.decrease_stack(1)

    def visitAssignement(self, ctx: CoBaParser.AssignementContext):
        self.debug_info(ctx, 'assignement')
        e_type: str = self.visit(ctx.expression())
        v_name = ctx.IDENTIFIER().getText()
        v_type = self.current_function.local_variables[v_name]
        v_id = self.variable_ids[v_name]
        # generate the code based on the data type of the variable
        # to store in and the expression to store
        if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += f"\tistore {v_id}\n\n"
            self.stack_size.decrease_stack(1)
        elif v_type == ValidTypes.Float64:
            if e_type == ValidTypes.Integer:
                self.code += '\ti2d\n'
                self.stack_size.increase_stack(1)
            self.code += f"\tdstore {v_id}\n\n"
            self.stack_size.decrease_stack(2)
        elif v_type == ValidTypes.String:
            self.code += f"\tastore {v_id}\n\n"
            self.stack_size.decrease_stack(1)

    def visitPrint(self, ctx: CoBaParser.PrintContext):
        self.debug_info(ctx, 'println')
        # get the PrintStream on the stack
        self.code += '\tgetstatic java/lang/System/out Ljava/io/PrintStream;\n'
        self.stack_size.increase_stack(1)
        # generate the argument type for the statement
        if ctx.expression() is not None:
            e_type = self.visit(ctx.expression())
            # convert boolean to literal 'true'/'false'
            if e_type == ValidTypes.Boolean:
                l_id: str = next(self.label_gen)
                self.code += f"\tifne label_{l_id}_if\n"
                self.code += '\tldc "false"\n'
                self.code += f"\tgoto label_{l_id}_end\nlabel_{l_id}_if:\n"
                self.code += '\tldc "true"\n'
                self.code += f"label_{l_id}_end:\n\n"
            self.code += '\tinvokevirtual java/io/PrintStream/println('
            if e_type == ValidTypes.Integer:
                self.code += 'I'
                self.stack_size.decrease_stack(1)
            elif e_type == ValidTypes.Float64:
                self.code += 'D'
                self.stack_size.decrease_stack(2)
            elif e_type in [ValidTypes.Boolean, ValidTypes.String]:
                self.code += 'Ljava/lang/String;'
                self.stack_size.decrease_stack(1)
        else:
            self.code += '\tinvokevirtual java/io/PrintStream/println('
        self.code += ')V\n\n'
        self.stack_size.decrease_stack(1)

    def visitIf_structure(self, ctx: CoBaParser.If_structureContext):
        self.visit(ctx.bool_expression())
        # generate the following structure:
        #   header true -> label_if
        #   else_branch()
        #   -> label_end
        # label_if:
        #   if_branch()
        # label_end:
        l_id: str = next(self.label_gen)
        self.code += f"\tifne label_{l_id}_if\n"
        self.stack_size.decrease_stack(1)
        if ctx.else_branch() is not None:
            for instruction in ctx.else_branch().instruction():
                self.visit(instruction)
        self.code += f"\tgoto label_{l_id}_end\nlabel_{l_id}_if:\n"
        for instruction in ctx.then_branch().instruction():
            self.visit(instruction)
        self.code += f"label_{l_id}_end:\n\n"

    def visitWhile_structure(self, ctx: CoBaParser.While_structureContext):
        # generate the following structure:
        # label_while:
        #   header false -> label_end
        #   body()
        #   -> label_while
        # label_end:
        l_id: str = next(self.label_gen)
        self.code += f"label_{l_id}_while:\n"
        self.visit(ctx.bool_expression())
        self.code += f"\tifeq label_{l_id}_end\n"
        self.stack_size.decrease_stack(1)
        for instruction in ctx.instruction():
            self.visit(instruction)
        self.code += f"\tgoto label_{l_id}_while\n"
        self.code += f"label_{l_id}_end:\n"

    def visitExpression(self, ctx: CoBaParser.ExpressionContext) -> str:
        self.debug_info(ctx, 'expression')
        if ctx.UNARY is not None:
            e_type = self.visit(ctx.RIGHT)
            if ctx.T_PLUS() is not None:
                # unary + does not do anything ...
                return e_type
            if ctx.T_MINUS() is not None:
                # unary - does not change stack but depends on data type
                if e_type == ValidTypes.Integer:
                    self.code += '\tineg\n'
                    return ValidTypes.Integer
                if e_type == ValidTypes.Float64:
                    self.code += '\tdneg\n'
                    return ValidTypes.Float64
            if ctx.T_EXCLAMATION() is not None:
                # !-op negates the value. can be implemented using xor with value 1
                self.code += '\ticonst_1\n\tixor\n'
                self.stack_size.increase_stack(1)
                self.stack_size.decrease_stack(1)
                return ValidTypes.Boolean
        if (ctx.LEFT or ctx.RIGHT) is not None:
            e_type_l = self.visit(ctx.LEFT)
            e_type_r = self.visit(ctx.RIGHT)
            r_type = e_type_l
            if e_type_l == ValidTypes.Integer and e_type_r == ValidTypes.Float64:
                # if a Float lays above an Integer we need to convert the Integer to a Float
                # some copying and moving around is needed since the Float uses 2 stack spaces
                self.code += '\tdup2_x1\n\tpop2\n\ti2d\n\tdup2_x2\n\tpop2\n'
                self.stack_size.increase_stack(3)
                self.stack_size.decrease_stack(2)
                r_type = ValidTypes.Float64
            elif e_type_l == ValidTypes.Float64 and e_type_r == ValidTypes.Integer:
                # if an Integer lays above a Float we can simply convert it to a Float
                self.code += '\ti2d\n'
                self.stack_size.increase_stack(1)
                r_type = ValidTypes.Float64
            if ctx.T_STAR() is not None:
                # * op depends on data type
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'mul\n'
                self.stack_size.decrease_stack(1 if r_type == ValidTypes.Integer else 2)
                return r_type
            if ctx.T_SLASH() is not None:
                # / op depends on data type
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'div\n'
                self.stack_size.decrease_stack(1 if r_type == ValidTypes.Integer else 2)
                return r_type
            if ctx.T_PERCENT() is not None:
                # % op depends on data type
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'rem\n'
                self.stack_size.decrease_stack(1 if r_type == ValidTypes.Integer else 2)
                return r_type
            if ctx.T_PLUS() is not None:
                # + op depends on data type
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'add\n'
                self.stack_size.decrease_stack(1 if r_type == ValidTypes.Integer else 2)
                return r_type
            if ctx.T_MINUS() is not None:
                # - op depends on data type
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'sub\n'
                self.stack_size.decrease_stack(1 if r_type == ValidTypes.Integer else 2)
                return r_type
            if ctx.T_D_AND() is not None:
                # && op only works for Bool
                self.code += '\tiand\n'
                self.stack_size.decrease_stack(1)
                return ValidTypes.Boolean
            if ctx.T_D_VBAR() is not None:
                # || op only works for Bool
                self.code += '\tior\n'
                self.stack_size.decrease_stack(1)
                return ValidTypes.Boolean
            # comparison:
            # the goal is to have either 0 or 1 on the stack depending
            # if the statement is false or true
            l_id: str = next(self.label_gen)
            if r_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                # for Integer there already exists useful Bytecode instructions
                if ctx.T_NOTEQUAL() is not None:
                    self.code += '\tif_icmpne'
                elif ctx.T_D_EQUAL() is not None:
                    self.code += '\tif_icmpeq'
                elif ctx.T_LESS() is not None:
                    self.code += '\tif_icmplt'
                elif ctx.T_GREATER() is not None:
                    self.code += '\tif_icmpgt'
                elif ctx.T_LESSEQUAL() is not None:
                    self.code += '\tif_icmple'
                elif ctx.T_GREATEREQUAL() is not None:
                    self.code += '\tif_icmpge'
                self.stack_size.decrease_stack(2)
            elif r_type == ValidTypes.Float64:
                # Floats need to be compared differently using dcmpg
                # after that we implement a simple if statement
                self.code += '\tdcmpg\n'
                if ctx.T_NOTEQUAL() is not None:
                    self.code += '\tifne'
                elif ctx.T_D_EQUAL() is not None:
                    self.code += '\tifeq'
                elif ctx.T_LESS() is not None:
                    self.code += '\tiflt'
                elif ctx.T_GREATER() is not None:
                    self.code += '\tifgt'
                elif ctx.T_LESSEQUAL() is not None:
                    self.code += '\tifle'
                elif ctx.T_GREATEREQUAL() is not None:
                    self.code += '\tifge'
                self.stack_size.decrease_stack(4)
            elif r_type == ValidTypes.String:
                # Strings can only be compared on equality
                if ctx.T_NOTEQUAL() is not None:
                    self.code += '\tif_acmpne'
                elif ctx.T_D_EQUAL() is not None:
                    self.code += '\tif_acmpeq'
                self.stack_size.decrease_stack(2)
            # implement the basic if statement and push either 0 or 1
            self.code += f" label_{l_id}_if\n\ticonst_0\n"
            self.code += f"\tgoto label_{l_id}_end\nlabel_{l_id}_if:\n"
            self.code += f"\ticonst_1\nlabel_{l_id}_end:\n"
            self.stack_size.increase_stack(1)
            return ValidTypes.Boolean
        if ctx.function_call() is not None:
            return self.visit(ctx.function_call())
        if ctx.atom() is not None:
            return self.visit(ctx.atom())

    def visitAtom(self, ctx: CoBaParser.AtomContext) -> str:
        self.debug_info(ctx, 'atom')
        if ctx.expression() is not None:
            return self.visit(ctx.expression())
        if ctx.type_element() is not None:
            return self.visit(ctx.type_element())
        if ctx.IDENTIFIER() is not None:
            self.debug_info(ctx, 'variable', False)
            v_name = ctx.IDENTIFIER().getText()
            v_type = self.current_function.local_variables[v_name]
            v_id = self.variable_ids[v_name]
            # if a variable is used we need to load its value
            # the data type is needed for the code generation
            if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += f"\tiload {v_id}\n"
                self.stack_size.increase_stack(1)
            elif v_type == ValidTypes.Float64:
                self.code += f"\tdload {v_id}\n"
                self.stack_size.increase_stack(2)
            elif v_type == ValidTypes.String:
                self.code += f"\taload {v_id}\n"
                self.stack_size.increase_stack(1)
            return v_type

    def visitType_element(self, ctx: CoBaParser.Type_elementContext) -> str:
        self.debug_info(ctx, 'type_element', False)
        # simply push an atom on the stack
        if ctx.INTEGER_NUMBER() is not None:
            self.code += f"\tldc {ctx.INTEGER_NUMBER().getText()}\n"
            self.stack_size.increase_stack(1)
            return ValidTypes.Integer
        if ctx.FLOAT_NUMBER() is not None:
            self.code += f"\tldc2_w {ctx.FLOAT_NUMBER().getText()}\n"
            self.stack_size.increase_stack(2)
            return ValidTypes.Float64
        if ctx.K_TRUE() is not None:
            self.code += '\ticonst_1\n'
            self.stack_size.increase_stack(1)
            return ValidTypes.Boolean
        if ctx.K_FALSE() is not None:
            self.code += '\ticonst_0\n'
            self.stack_size.increase_stack(1)
            return ValidTypes.Boolean
        if ctx.STRING() is not None:
            self.code += f"\tldc {ctx.STRING().getText()}\n"
            self.stack_size.increase_stack(1)
            return ValidTypes.String
