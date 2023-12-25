"""
define a Graph for Liveness Analysis
"""

from copy import deepcopy
from itertools import product

class CFNode:
    """
    implement a node for a control flow graph.
    """
    def __init__(self, name: str = '') -> None:
        self.name = name
        self.id_: int = -1
        self.ins: set[str] = set()
        self.outs: set[str] = set()

    def set_id(self, id_: int) -> None:
        self.id_ = id_

    def add_in(self, a_in: str) -> None:
        self.ins.add(a_in)

    def add_out(self, a_out: str) -> None:
        self.outs.add(a_out)

    def __str__(self) -> str:
        s_str: str = f"{self.id_:>3}: {str(self.ins):<15} @ {str(self.outs):<15}"
        return s_str


class RIGraph:
    """
    implement logic for a register interference graph.
    """
    def __init__(self, local_variables: list[str], interference_sets: list[set[str]]) -> None:
        self.nodes: list[str] = [node for node in local_variables if isinstance(node, str)]
        self.adj: dict[str, set[str]] = {node: set() for node in self.nodes}
        self.colors: dict[str, int] = {node: -1 for node in self.nodes}
        self.min_registers = 0
        for i_set in interference_sets:
            if len(i_set) == 1:
                continue
            for node_a in i_set:
                for node_b in i_set:
                    if node_a != node_b:
                        self.adj[node_a].add(node_b)
        self.brute_force_chromatic_number()

    def greedy_coloring(self) -> tuple[int, dict[str, int]]:
        colors = {}
        valid_colors = set(range(len(self.nodes)))
        for node in self.nodes:
            neighbor_colors = {colors[neighbor] for neighbor in self.adj[node] if neighbor in colors}
            colors[node] = min(valid_colors - neighbor_colors)

        chromatic_number = len(set(colors.values()))
        return chromatic_number, colors

    def is_valid_coloring(self, coloring):
        for node, neighbors in self.adj.items():
            for neighbor in neighbors:
                if coloring[node] == coloring[neighbor]:
                    return False
        return True

    def brute_force_chromatic_number(self) -> None:
        smallest_chromatic_number, best_coloring = self.greedy_coloring()
        if len(self.nodes) < 7:
            num_colors = len(self.nodes)
            for color_assignment in product(range(num_colors), repeat=num_colors):
                chromatic_number = len(set(color_assignment))
                if chromatic_number >= smallest_chromatic_number:
                    continue
                coloring = dict(zip(self.nodes, color_assignment))

                if self.is_valid_coloring(coloring):
                    smallest_chromatic_number = chromatic_number
                    best_coloring = coloring.copy()

        self.colors = best_coloring
        self.min_registers = smallest_chromatic_number

    # def bron_kerbosch(self, R: set[str], P: set[str], X: set[str], colors: dict[str, int]) -> int:
    #     """
    #     modified bron kerbosch maximal cliques algorithm to find chromatic number.
    #     """
    #     if not P and not X:
    #         return len(set(colors.values()))

    #     pivot = next(iter(P.union(X)))
    #     max_color = float('inf')

    #     for node in P.difference(self.adj[pivot]):
    #         P_prime = P.intersection(self.adj[node])
    #         X_prime = X.intersection(self.adj[node])
    #         R_prime = R.union({node})

    #         colors[node] = len(set(R_prime))
    #         color_count = self.bron_kerbosch(R_prime, P_prime, X_prime, colors)
    #         if color_count < max_color:
    #             max_color = color_count

    #         colors[node] = -1  # Backtrack

    #     return max_color

    # def chromatic_number(self):
    #     """
    #     init and run bron kerbosch algorithm.
    #     """
    #     R = set()
    #     P = set(self.nodes)
    #     X = set()
    #     colors: dict[str, int] = {node: -1 for node in self.nodes}
    #     chromatic_number: int = self.bron_kerbosch(R, P, X, colors)
    #     return chromatic_number

    def __str__(self) -> str:
        s_str: str = '+++++++++++++++++++++++++\n'
        s_str += f"Nodes (#{len(self.nodes)}) [Name(Color)]:\n"
        s_str += ','.join([f"{node}({self.colors[node]})" for node in self.nodes])
        s_str += '\nAdjacency List:\n'
        indent: int = max((len(name) for name in self.nodes), default=0)
        for n_id, n_adj in self.adj.items():
            s_str += f"{n_id:>{indent}}: {n_adj}\n"
        s_str += '+++++++++++++++++++++++++'
        return s_str


class CFGraph:
    """
    implement logic for a control flow graph.
    """
    def __init__(self) -> None:
        self.nodes: list[CFNode] = []
        self.adj: dict[int, set[int]] = {}
        self.ref_counter: dict[int, int] = {}
        self.interferences: dict[int, set[str]] = {}

    def add_node(self, node: CFNode) -> int:
        """
        add a node to the graph.
        """
        id_ = len(self.nodes)
        node.set_id(id_)
        self.nodes.append(node)
        self.adj[id_] = set()
        return id_

    def add_edge(self, id_from: int, id_to: int) -> None:
        """
        add an edge between two nodes via node ids.
        """
        self.adj[id_from].add(id_to)
        if self.ref_counter.get(id_to) is None:
            self.ref_counter[id_to] = 0
        self.ref_counter[id_to] += 1

    def dfs(self, node_id: int, visited: set[int])-> set[str]:
        """
        traverse the control flow graph using dfs and update register
        interference sets.
        """
        if node_id not in self.interferences:
            self.interferences[node_id] = set()
        if node_id in visited:
            return self.interferences[node_id]

        visited.add(node_id)
        interference_set = set()

        for neighbor_id in self.adj[node_id]:
            neighbor_interference = self.dfs(neighbor_id, visited)
            interference_set.update(neighbor_interference)

        node = self.nodes[node_id]
        for variable in node.ins:
            interference_set.discard(variable)
        interference_set.update(node.outs)
        self.interferences[node_id].update(interference_set.copy())

        return interference_set

    def _interferences_equal(self, dict_a: dict[int, set[str]],
                             dict_b: dict[int, set[str]]) -> bool:
        """
        check if two dictionaries have the same values.
        """
        if set(dict_a.keys()) != set(dict_b.keys()):
            return False
        for key in dict_a:
            if dict_a[key] != dict_b[key]:
                return False
        return True

    def gen_interference_sets(self) -> list[set[str]]:
        """
        traverse the control flow graph using dfs and update register
        interference sets, until no changes were made.
        """
        interferences: dict[int, set[str]] = {None: None}
        while not self._interferences_equal(self.interferences, interferences):
            interferences: dict[int, set[str]] = deepcopy(self.interferences)
            self.dfs(0, set())
        return [s for s in self.interferences.values() if s]

    def __str__(self) -> str:
        s_str: str = '++++++++++++++++++++\n'
        s_str += f"Nodes (#{len(self.nodes)}):\n"
        for i, node in enumerate(self.nodes):
            s_str += f"{str(node):<32}ref: {self.ref_counter.get(i, 0)}\n"
        s_str += '\nAdjacency List:\n'
        for n_id, n_adj in self.adj.items():
            s_str += f"{n_id:>3}: {n_adj}\n"
        s_str += '++++++++++++++++++++\n'
        return s_str
