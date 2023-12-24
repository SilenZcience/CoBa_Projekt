"""
define LivenessAnalysis to generate a RegisterInterferenceGraph and
calculate the chromatic number
"""

try:
    from compiler.src.CoBaParser import CoBaParser
    from compiler.src.CoBaParserVisitor import CoBaParserVisitor
    from compiler.src.graphs import CFNode, CFGraph, RIGraph
    from compiler.src.type_checker_helper import SymbolTable
except ModuleNotFoundError:
    from .CoBaParser import CoBaParser
    from .CoBaParserVisitor import CoBaParserVisitor
    from .graphs import CFNode, CFGraph, RIGraph
    from .type_checker_helper import SymbolTable


class LivenessAnalysis(CoBaParserVisitor):
    """
    analyse liveness by constructing a controlflowgraph and
    a register interferencegraph and calculate its chromatic value
    """
    def __init__(self, symbol_table: SymbolTable) -> None:
        self.symbol_table: SymbolTable = symbol_table
        self.current_graph: CFGraph = None
        self.control_flow_graphs: dict[str, CFGraph] = {}
        self.register_interference_graphs: dict[str, RIGraph] = {}
        self.node_anchor_id: int = -1

    def gen_interference_graph(self) -> None:
        for f_name, cf_graph in self.control_flow_graphs.items():
            ri_graph = RIGraph([*self.symbol_table.get_function(f_name).local_variables.keys()],
                               cf_graph.gen_interference_sets())
            self.register_interference_graphs[f_name] = ri_graph

    def visitMain_function_header(self, ctx:CoBaParser.Main_function_headerContext):
        self.current_graph = CFGraph()
        self.control_flow_graphs[ctx.K_MAIN().getText()] = self.current_graph

        node: CFNode = CFNode()
        self.node_anchor_id = self.current_graph.add_node(node)

    def visitFunction_header(self, ctx: CoBaParser.Function_headerContext):
        f_name: str = ctx.IDENTIFIER().getText()
        self.current_graph = CFGraph()
        self.control_flow_graphs[f_name] = self.current_graph

        node: CFNode = CFNode()
        for param in self.symbol_table.get_function(f_name).parameters.keys():
            node.add_in(param)
        self.node_anchor_id = self.current_graph.add_node(node)

    def visitFunction_body(self, ctx: CoBaParser.Function_bodyContext):
        for declaration in ctx.declaration():
            self.visit(declaration)
        for instruction in ctx.instruction():
            self.visit(instruction)
            if instruction.return_statement() is not None:
                return
        if ctx.return_statement() is not None:
            self.visit(ctx.return_statement())

    def visitReturn_statement(self, ctx: CoBaParser.Return_statementContext):
        node: CFNode = CFNode()
        if ctx.expression() is not None:
            for variable in self.visit(ctx.expression()):
                node.add_out(variable)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        self.node_anchor_id = node_id

    def visitFunction_call(self, ctx: CoBaParser.Function_callContext) -> list[str]:
        if ctx.function_argument() is not None:
            return self.visit(ctx.function_argument())
        return []

    def visitFunction_argument(self, ctx: CoBaParser.Function_argumentContext) -> list[str]:
        used_vars: list[str] = self.visit(ctx.expression())
        if ctx.function_argument() is not None:
            used_vars += self.visit(ctx.function_argument())
        return used_vars

    def visitDeclaration(self, ctx: CoBaParser.DeclarationContext):
        node: CFNode = CFNode()
        node.add_in(ctx.IDENTIFIER().getText())
        for v_in in self.visit(ctx.expression()):
            node.add_out(v_in)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        self.node_anchor_id = node_id

    def visitBlock_structure(self, ctx: CoBaParser.Block_structureContext):
        for instruction in ctx.instruction():
            self.visit(instruction)
            if instruction.return_statement() is not None:
                return

    def visitAssignement(self, ctx: CoBaParser.AssignementContext):
        node: CFNode = CFNode()
        node.add_in(ctx.IDENTIFIER().getText())
        for v_in in self.visit(ctx.expression()):
            node.add_out(v_in)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        self.node_anchor_id = node_id

    def visitPrint(self, ctx: CoBaParser.PrintContext):
        node: CFNode = CFNode()
        if ctx.expression() is not None:
            for variable in self.visit(ctx.expression()):
                node.add_out(variable)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        self.node_anchor_id = node_id

    def visitIf_structure(self, ctx: CoBaParser.If_structureContext):
        node_s: CFNode = CFNode()
        for variable in self.visit(ctx.bool_expression()):
            node_s.add_out(variable)
        node_id_s: int = self.current_graph.add_node(node_s)
        self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        self.node_anchor_id = node_id_s
        flow_then:bool = self.visit(ctx.then_branch())
        then_id: int = self.node_anchor_id
        self.node_anchor_id = node_id_s
        flow_else: bool = self.visit(ctx.else_branch())
        node_e: CFNode = CFNode()
        node_id_e: int = self.current_graph.add_node(node_e)
        if flow_then:
            self.current_graph.add_edge(then_id, node_id_e)
        if flow_else:
            self.current_graph.add_edge(self.node_anchor_id, node_id_e)
        self.node_anchor_id = node_id_e

    def visitThen_branch(self, ctx: CoBaParser.Then_branchContext) -> bool:
        for instruction in ctx.instruction():
            self.visit(instruction)
            if instruction.return_statement() is not None:
                return False
        return True

    def visitElse_branch(self, ctx: CoBaParser.Else_branchContext) -> bool:
        for instruction in ctx.instruction():
            self.visit(instruction)
            if instruction.return_statement() is not None:
                return False
        return True

    def visitWhile_structure(self, ctx: CoBaParser.While_structureContext):
        node_s: CFNode = CFNode()
        for variable in self.visit(ctx.bool_expression()):
            node_s.add_out(variable)
        node_id_s: int = self.current_graph.add_node(node_s)
        self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        self.node_anchor_id = node_id_s
        for instruction in ctx.instruction():
            self.visit(instruction)
            if instruction.return_statement() is not None:
                break
        else:
            self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        self.node_anchor_id = node_id_s

    def visitExpression(self, ctx: CoBaParser.ExpressionContext) -> list[str]:
        used_vars: list[str] = []
        if ctx.LEFT is not None:
            used_vars += self.visit(ctx.LEFT)
        if ctx.RIGHT is not None:
            used_vars += self.visit(ctx.RIGHT)
        if ctx.function_call() is not None:
            used_vars += self.visit(ctx.function_call())
        if ctx.atom() is not None:
            used_vars += self.visit(ctx.atom())

        return used_vars

    def visitAtom(self, ctx: CoBaParser.AtomContext) -> list[str]:
        if ctx.expression() is not None:
            return self.visit(ctx.expression())
        if ctx.IDENTIFIER() is not None:
            return [ctx.IDENTIFIER().getText()]
        return []
