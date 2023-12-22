
from antlr4.ParserRuleContext import ParserRuleContext
from compiler.src.CoBaParser import CoBaParser

try:
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.CoBaParserVisitor import CoBaParserVisitor
    from compiler.src.type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol
except ModuleNotFoundError:
    from .CoBaParser import CoBaParser
    from .CoBaParserVisitor import CoBaParserVisitor
    from .type_checker_helper import ValidTypes, SymbolTable, FunctionSymbol


def gen_next_label_id() -> str:
    id_ = 0
    while True:
        yield str(id_)
        id_ += 1


class CodeGenerator(CoBaParserVisitor):
    """
    
    """
    def __init__(self, symbol_table: SymbolTable, file_name: str, debug: bool) -> None:
        self.symbol_table: SymbolTable = symbol_table
        self.file_name: str = file_name
        self.debug: bool = debug

        self.label_gen = gen_next_label_id()

        self.current_function: FunctionSymbol = None
        self.variable_ids: dict[str, int] = {}
        self.code: str = ''

        # self.has_errors: bool = False

    def set_var_ids(self, f_vars: dict[str, str]) -> int:
        self.variable_ids.clear()
        c_id = 0
        for v_name, v_type in f_vars.items():
            self.variable_ids[v_name] = c_id
            c_id += 1 + (v_type == ValidTypes.Float64)
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
        self.visitChildren(ctx)
        self.code += '.end method\n\n'

    def visitMain_function_header(self, ctx: CoBaParser.Main_function_headerContext):
        current_function_name: str = ctx.K_MAIN().getText()
        self.current_function = self.symbol_table.get_function(current_function_name)
        self.code += '.method public static main([Ljava/lang/String;)V\n'
        local_var_count: int = self.set_var_ids(self.current_function.local_variables)
        self.code += f"\t.limit locals {local_var_count+1}\n"
        self.code += f"\t.limit stack 100\n\n" # TODO: actual stack heuristic

    def visitFunction(self, ctx: CoBaParser.FunctionContext):
        self.visitChildren(ctx)
        self.code += '.end method\n\n'

    def visitFunction_header(self, ctx: CoBaParser.Function_headerContext):
        current_function_name: str = ctx.IDENTIFIER().getText()
        self.current_function = self.symbol_table.get_function(current_function_name)
        self.code += f".method public static {current_function_name}("
        for p_type in self.current_function.parameters.values():
            if p_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += 'I'
            elif p_type == ValidTypes.Float64:
                self.code += 'D'
            elif p_type == ValidTypes.String:
                self.code += 'Ljava/lang/String;'
        self.code += ')'
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
        self.code += f"\t.limit stack 100\n\n" # TODO: actual stack heuristic

    def visitFunction_body(self, ctx: CoBaParser.Function_bodyContext):
        self.visitChildren(ctx)
        if ctx.return_statement() is None:
            f_type = self.current_function.f_type
            if f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += '\tireturn\n'
            elif f_type == ValidTypes.Float64:
                self.code += '\tdreturn\n'
            elif f_type == ValidTypes.String:
                self.code += '\tareturn\n'
            else:
                self.code += '\treturn\n'

    def visitReturn_statement(self, ctx: CoBaParser.Return_statementContext):
        self.debug_info(ctx, 'return')
        self.visitChildren(ctx)
        f_type = self.current_function.f_type
        if f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += '\tireturn\n'
        elif f_type == ValidTypes.Float64:
            self.code += '\tdreturn\n'
        elif f_type == ValidTypes.String:
            self.code += '\tareturn\n'
        else:
            self.code += '\treturn\n'

    def visitFunction_call(self, ctx: CoBaParser.Function_callContext):
        self.debug_info(ctx, 'function_call')
        self.visitChildren(ctx)
        if ctx.IDENTIFIER() is not None:
            f_table: FunctionSymbol = self.symbol_table.get_function(ctx.IDENTIFIER().getText())
            self.code += f"\tinvokestatic {self.file_name}/{f_table.f_name}("
            for p_type in f_table.parameters.values():
                if p_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                    self.code += 'I'
                elif p_type == ValidTypes.Float64:
                    self.code += 'D'
                elif p_type == ValidTypes.String:
                    self.code += 'Ljava/lang/String;'
            self.code += ')'
            if f_table.f_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += 'I'
            elif f_table.f_type == ValidTypes.Float64:
                self.code += 'D'
            elif f_table.f_type == ValidTypes.String:
                self.code += 'Ljava/lang/String;'
            else:
                self.code += 'V'
            self.code += '\n\n'
            return f_table.f_type
        elif ctx.K_MAIN() is not None:
            f_name: str = ctx.K_MAIN().getText()
            self.code += '\ticonst_0\n\tanewarray java/lang/String\n'
            self.code += f"\tinvokestatic {self.file_name}/{f_name}([Ljava/lang/String;)V\n\n"
            return None

    def visitDeclaration(self, ctx: CoBaParser.DeclarationContext):
        self.debug_info(ctx, 'declaration')
        e_type: str = self.visit(ctx.expression())
        v_name = ctx.IDENTIFIER().getText()
        v_type = self.current_function.local_variables[v_name]
        v_id = self.variable_ids[v_name]
        if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += f"\tistore {v_id}\n\n"
        elif v_type == ValidTypes.Float64:
            if e_type == ValidTypes.Integer:
                self.code += '\ti2d\n'
            self.code += f"\tdstore {v_id}\n\n"
        elif v_type == ValidTypes.String:
            self.code += f"\tastore {v_id}\n\n"

    def visitAssignement(self, ctx: CoBaParser.AssignementContext):
        self.debug_info(ctx, 'assignement')
        e_type: str = self.visit(ctx.expression())
        v_name = ctx.IDENTIFIER().getText()
        v_type = self.current_function.local_variables[v_name]
        v_id = self.variable_ids[v_name]
        if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
            self.code += f"\tistore {v_id}\n\n"
        elif v_type == ValidTypes.Float64:
            if e_type == ValidTypes.Integer:
                self.code += '\ti2d\n'
            self.code += f"\tdstore {v_id}\n\n"
        elif v_type == ValidTypes.String:
            self.code += f"\tastore {v_id}\n\n"

    def visitPrint(self, ctx: CoBaParser.PrintContext):
        self.debug_info(ctx, 'println')
        self.code += '\tgetstatic java/lang/System/out Ljava/io/PrintStream;\n'
        if ctx.expression() is not None:
            e_type = self.visit(ctx.expression())
            self.code += '\tinvokevirtual java/io/PrintStream/println('
            if e_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += 'I'
            elif e_type == ValidTypes.Float64:
                self.code += 'D'
            elif e_type == ValidTypes.String:
                self.code += 'Ljava/lang/String;'
        else:
            self.code += '\tinvokevirtual java/io/PrintStream/println('
        self.code += ')V\n\n'

    def visitIf_structure(self, ctx: CoBaParser.If_structureContext):
        self.visit(ctx.bool_expression())
        l_id: str = next(self.label_gen)
        self.code += f"\tifne label_{l_id}_if\n"
        if ctx.else_branch() is not None:
            for instruction in ctx.else_branch().instruction():
                self.visit(instruction)
        self.code += f"\tgoto label_{l_id}_end\nlabel_{l_id}_if:\n"
        for instruction in ctx.then_branch().instruction():
            self.visit(instruction)
        self.code += f"label_{l_id}_end:\n\n"

    def visitWhile_structure(self, ctx: CoBaParser.While_structureContext):
        l_id: str = next(self.label_gen)
        self.code += f"label_{l_id}_while:\n"
        self.visit(ctx.bool_expression())
        self.code += f"\tifeq label_{l_id}_end\n"
        for instruction in ctx.instruction():
            self.visit(instruction)
        self.code += f"\tgoto label_{l_id}_while\n"
        self.code += f"label_{l_id}_end:\n"

    def visitExpression(self, ctx: CoBaParser.ExpressionContext) -> str:
        self.debug_info(ctx, 'expression')
        if ctx.UNARY is not None:
            e_type = self.visit(ctx.RIGHT)
            if ctx.T_PLUS() is not None:
                return e_type
            if ctx.T_MINUS() is not None:
                if e_type == ValidTypes.Integer:
                    self.code += 'ineg\n'
                    return ValidTypes.Integer
                if e_type == ValidTypes.Float64:
                    self.code += 'dneg\n'
                    return ValidTypes.Float64
            if ctx.T_EXCLAMATION() is not None:
                self.code += '\ticonst_1\n\tixor\n'
                return ValidTypes.Boolean
        if (ctx.LEFT or ctx.RIGHT) is not None:
            e_type_l = self.visit(ctx.LEFT)
            e_type_r = self.visit(ctx.RIGHT)
            r_type = e_type_l
            if e_type_l == ValidTypes.Integer and e_type_r == ValidTypes.Float64:
                self.code += '\tdup2_x1\n\tpop2\n\ti2d\n\tdup2_x2\n\tpop2\n'
                r_type = ValidTypes.Float64
            elif e_type_l == ValidTypes.Float64 and e_type_r == ValidTypes.Integer:
                self.code += '\ti2d\n'
                r_type = ValidTypes.Float64
            if ctx.T_STAR() is not None:
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'mul\n'
                return r_type
            if ctx.T_SLASH() is not None:
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'div\n'
                return r_type
            if ctx.T_PERCENT() is not None:
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'rem\n'
                return r_type
            if ctx.T_PLUS() is not None:
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'add\n'
                return r_type
            if ctx.T_MINUS() is not None:
                self.code += '\t' + ('i' if r_type == ValidTypes.Integer else 'd') + 'sub\n'
                return r_type
            if ctx.T_D_AND() is not None:
                self.code += '\tiand\n'
                return ValidTypes.Boolean
            if ctx.T_D_VBAR() is not None:
                self.code += '\tior\n'
                return ValidTypes.Boolean
            l_id: str = next(self.label_gen)
            if r_type in [ValidTypes.Integer, ValidTypes.Boolean]:
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
            elif r_type == ValidTypes.Float64:
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
            elif r_type == ValidTypes.String:
                if ctx.T_NOTEQUAL() is not None:
                    self.code += '\tif_acmpne'
                elif ctx.T_D_EQUAL() is not None:
                    self.code += '\tif_acmpeq'
            self.code += f" label_{l_id}_if\n\ticonst_0\n"
            self.code += f"\tgoto label_{l_id}_end\nlabel_{l_id}_if:\n"
            self.code += f"\ticonst_1\nlabel_{l_id}_end:\n"
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
            if v_type in [ValidTypes.Integer, ValidTypes.Boolean]:
                self.code += f"\tiload {v_id}\n"
            elif v_type == ValidTypes.Float64:
                self.code += f"\tdload {v_id}\n"
            elif v_type == ValidTypes.String:
                self.code += f"\taload {v_id}\n"
            return v_type

    def visitType_element(self, ctx: CoBaParser.Type_elementContext) -> str:
        self.debug_info(ctx, 'type_element', False)
        if ctx.INTEGER_NUMBER() is not None:
            self.code += f"\tldc {ctx.INTEGER_NUMBER().getText()}\n"
            return ValidTypes.Integer
        if ctx.FLOAT_NUMBER() is not None:
            self.code += f"\tldc2_w {ctx.FLOAT_NUMBER().getText()}\n"
            return ValidTypes.Float64
        if ctx.K_TRUE() is not None:
            self.code += '\ticonst_1\n'
            return ValidTypes.Boolean
        if ctx.K_FALSE() is not None:
            self.code += '\ticonst_0\n'
            return ValidTypes.Boolean
        if ctx.STRING() is not None:
            self.code += f"\tldc {ctx.STRING().getText()}\n"
            return ValidTypes.String
