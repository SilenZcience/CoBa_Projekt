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
        """
        generate the register interference graphs for each function
        """
        for f_name, cf_graph in self.control_flow_graphs.items():
            ri_graph = RIGraph([*self.symbol_table.get_function(f_name).local_variables.keys()],
                               cf_graph.gen_interference_sets())
            self.register_interference_graphs[f_name] = ri_graph

    def visitMain_function_header(self, ctx:CoBaParser.Main_function_headerContext) -> None:
        # create a new control flow graph since a new function starts
        self.current_graph = CFGraph()
        self.control_flow_graphs[ctx.K_MAIN().getText()] = self.current_graph

        node: CFNode = CFNode()
        self.node_anchor_id = self.current_graph.add_node(node)

    def visitFunction_header(self, ctx: CoBaParser.Function_headerContext) -> None:
        # create a new control flow graph since a new function starts
        f_name: str = ctx.IDENTIFIER().getText()
        self.current_graph = CFGraph()
        self.control_flow_graphs[f_name] = self.current_graph

        node: CFNode = CFNode()
        # in contrast to the main function this function may contain parameters
        # that used to store values in
        # we just use the symbol table instead of iterating over the parameters
        for param in self.symbol_table.get_function(f_name).parameters.keys():
            node.add_in(param)
        self.node_anchor_id = self.current_graph.add_node(node)

    def visitFunction_body(self, ctx: CoBaParser.Function_bodyContext) -> None:
        # visit every declaration of the function body
        for declaration in ctx.declaration():
            self.visit(declaration)
        # visit every instruction of the function body
        # the flow may end if a return is used
        for instruction in ctx.instruction():
            if self.visit(instruction) is False:
                return
        # visit the optional final return statement
        if ctx.return_statement() is not None:
            self.visit(ctx.return_statement())

    def visitReturn_statement(self, ctx: CoBaParser.Return_statementContext) -> bool:
        # create a control flow node for a return statement
        node: CFNode = CFNode()
        # every variable used in the return expression is loaded
        if ctx.expression() is not None:
            for variable in self.visit(ctx.expression()):
                node.add_out(variable)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id
        # control flow always stops
        return False

    def visitFunction_call(self, ctx: CoBaParser.Function_callContext) -> bool:
        # create a control flow node for the function call.
        # the variables that are loaded are the arguments passed in
        # arguments may contain instructions
        node: CFNode = CFNode()
        if ctx.function_argument() is not None:
            for v_in in self.visit(ctx.function_argument()):
                node.add_out(v_in)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id
        # control flow always continues
        return True

    def visitFunction_argument(self, ctx: CoBaParser.Function_argumentContext) -> list[str]:
        # return the used variables that need to be loaded for the function call
        # iterate over all arguments
        used_vars: list[str] = self.visit(ctx.expression())
        if ctx.function_argument() is not None:
            used_vars += self.visit(ctx.function_argument())
        return used_vars

    def visitDeclaration(self, ctx: CoBaParser.DeclarationContext) -> bool:
        # create a control flow node for a declaration
        node: CFNode = CFNode()
        # the variable that is used for storage is the identifier
        node.add_in(ctx.IDENTIFIER().getText())
        # the expression contains every variable that gets loaded
        for v_in in self.visit(ctx.expression()):
            node.add_out(v_in)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id
        # control flow always continues
        return True

    def visitInstruction(self, ctx:CoBaParser.InstructionContext) -> bool:
        # pass on the control flow indicator
        return self.visit(ctx.assignement() or ctx.block_structure() or ctx.control_structure() or \
            ctx.print_() or ctx.function_call() or ctx.return_statement())

    def visitAssignement(self, ctx: CoBaParser.AssignementContext) -> bool:
        # create a control flow node for an assignement
        node: CFNode = CFNode()
        # the variable that is used for storage is the identifier
        node.add_in(ctx.IDENTIFIER().getText())
        # the expression contains every variable that gets loaded
        for v_in in self.visit(ctx.expression()):
            node.add_out(v_in)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id
        # control flow always continues
        return True

    def visitBlock_structure(self, ctx: CoBaParser.Block_structureContext) -> bool:
        # visit every instruction
        # the entire control flow may end here if a return statement is used
        for instruction in ctx.instruction():
            if self.visit(instruction) is False:
                return False
        return True

    def visitControl_structure(self, ctx:CoBaParser.Control_structureContext) -> bool:
        if ctx.if_structure() is not None:
            return self.visit(ctx.if_structure())
        if ctx.while_structure() is not None:
            return self.visit(ctx.while_structure())

    def visitPrint(self, ctx: CoBaParser.PrintContext) -> bool:
        # create a control flow node for a print statement
        node: CFNode = CFNode()
        # the optional expression contains every variable that gets loaded
        if ctx.expression() is not None:
            for variable in self.visit(ctx.expression()):
                node.add_out(variable)

        node_id: int = self.current_graph.add_node(node)
        self.current_graph.add_edge(self.node_anchor_id, node_id)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id
        # control flow always continues
        return True

    def visitIf_structure(self, ctx: CoBaParser.If_structureContext) -> bool:
        # create a control flow node for the start of an if structure
        node_s: CFNode = CFNode()
        # the boolsch statement in the if header contains every loaded variable
        for variable in self.visit(ctx.bool_expression()):
            node_s.add_out(variable)
        node_id_s: int = self.current_graph.add_node(node_s)
        self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id_s

        complete_then = self.visit(ctx.then_branch())
        complete_else = True
        # temporarily save the last then-branch node
        then_id: int = self.node_anchor_id
        self.node_anchor_id = node_id_s
        if ctx.else_branch() is not None:
            complete_else = self.visit(ctx.else_branch())
        if complete_then or complete_else:
            # create a control flow node for the end of an if structure
            node_e: CFNode = CFNode()
            node_id_e: int = self.current_graph.add_node(node_e)
            # connect the final then-branch node and else-branch node to the end node
            if complete_then:
                self.current_graph.add_edge(then_id, node_id_e)
            if complete_else:
                self.current_graph.add_edge(self.node_anchor_id, node_id_e)
            # append the end node and make it the anchor for following nodes
            self.node_anchor_id = node_id_e
            # control flow continues if at least one branch continues
            return True
        # if both branches end the control flow then the entire structure ends it
        return False

    def visitThen_branch(self, ctx: CoBaParser.Then_branchContext) -> bool:
        # visit every instruction and return indicator if the control flow ends
        for instruction in ctx.instruction():
            if self.visit(instruction) is False:
                return False
        return True

    def visitElse_branch(self, ctx: CoBaParser.Else_branchContext) -> bool:
        # visit every instruction and return indicator if the control flow continues
        for instruction in ctx.instruction():
            if self.visit(instruction) is False:
                return False
        return True

    def visitWhile_structure(self, ctx: CoBaParser.While_structureContext) -> bool:
        # create a control flow node for the start of a while structure
        node_s: CFNode = CFNode()
        # the boolsch statement in the while header contains every loaded variable
        for variable in self.visit(ctx.bool_expression()):
            node_s.add_out(variable)
        node_id_s: int = self.current_graph.add_node(node_s)
        self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        # append the new node and make it the anchor for following nodes
        self.node_anchor_id = node_id_s
        for instruction in ctx.instruction():
            if self.visit(instruction) is False:
                break
        else:
            # connect the last while body node to the while header node
            self.current_graph.add_edge(self.node_anchor_id, node_id_s)
        # for future nodes the anchor is the while header again
        self.node_anchor_id = node_id_s
        # control flow always continues
        return True

    def visitBool_expression(self, ctx:CoBaParser.Bool_expressionContext) -> list[str]:
        return self.visit(ctx.expression())

    def visitExpression(self, ctx: CoBaParser.ExpressionContext) -> list[str]:
        # collect every variable used inside the expression
        used_vars: list[str] = []
        if ctx.LEFT is not None:
            used_vars += self.visit(ctx.LEFT)
        if ctx.RIGHT is not None:
            used_vars += self.visit(ctx.RIGHT)
        if ctx.function_call() is not None:
            # function calls are their own nodes
            self.visit(ctx.function_call())
        if ctx.atom() is not None:
            used_vars += self.visit(ctx.atom())

        return used_vars

    def visitAtom(self, ctx: CoBaParser.AtomContext) -> list[str]:
        if ctx.expression() is not None:
            # the atom may be an expression in parantheses
            return self.visit(ctx.expression())
        if ctx.IDENTIFIER() is not None:
            # simply return the found variable when a variable was used
            return [ctx.IDENTIFIER().getText()]
        # constant atoms are irrelevant
        return []
