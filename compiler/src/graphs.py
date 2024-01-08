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
        # the variables that get stored in
        self.ins: set[str] = set()
        # the variables that get loaded
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
        # additional check to exclude the None type Node in the main function
        self.nodes: list[str] = [node for node in local_variables if isinstance(node, str)]
        self.adj: dict[str, set[str]] = {node: set() for node in self.nodes}
        self.colors: dict[str, int] = {node: -1 for node in self.nodes}
        self.min_registers = 0
        # connect every node with every other node in all given sets
        for i_set in interference_sets:
            if len(i_set) == 1:
                continue
            for node_a in i_set:
                for node_b in i_set:
                    if node_a != node_b:
                        self.adj[node_a].add(node_b)
        self.brute_force_chromatic_number()

    def bron_kerbosch(self, R: set[str], P: set[str], X: set[str], cliques: list[set[str]]) -> None:
        """
        bron kerbosch maximal cliques algorithm.
        https://en.wikipedia.org/wiki/Bron%E2%80%93Kerbosch_algorithm#With_pivoting
        """
        if not P and not X:
            cliques.append(R)
            return

        pivot = next(iter(P.union(X)))

        for node in P.difference(self.adj[pivot]):
            r_prime = R.union({node})
            p_prime = P.intersection(self.adj[node])
            x_prime = X.intersection(self.adj[node])
            self.bron_kerbosch(r_prime, p_prime, x_prime, cliques)

    def greedy_coloring(self) -> tuple[int, dict[str, int]]:
        """
        basic greedy algorithm for graph coloring
        https://en.wikipedia.org/wiki/Greedy_coloring#Algorithm
        """
        colors = {}
        valid_colors = set(range(len(self.nodes)))
        for node in self.nodes:
            neighbor_colors = {colors[nbor] for nbor in self.adj[node] if nbor in colors}
            colors[node] = min(valid_colors - neighbor_colors)

        return len(set(colors.values())), colors

    def brute_force_chromatic_number(self) -> None:
        """
        brute force the chromatic number.
        greedy algorithm is used as an upper boundary.
        clique number (bron kerbosch) is used as a lower boundary.
        """
        def is_valid_coloring(coloring: dict[str, tuple[int, ...]]) -> bool:
            for node, neighbors in self.adj.items():
                for neighbor in neighbors:
                    if coloring[node] == coloring[neighbor]:
                        return False
            return True

        cliques = []
        upper_boundary, best_coloring = self.greedy_coloring()
        self.bron_kerbosch(set(), set(self.nodes), set(), cliques)
        lower_boundary = max(len(clique) for clique in cliques)

        chromatic_number = upper_boundary
        for chrom_num in range(lower_boundary, upper_boundary):
            # we only bruteforce on smaller graphs
            # larger graphs only get approximated using the greedy algorithm
            if chrom_num > 7:
                break
            for color_assignment in product(range(chrom_num), repeat=len(self.nodes)):
                coloring = dict(zip(self.nodes, color_assignment))
                if is_valid_coloring(coloring):
                    best_coloring = coloring.copy()
                    chromatic_number = chrom_num
                    break
            else:
                continue
            break

        # save the best configuration
        self.colors = best_coloring
        self.min_registers = chromatic_number

    def __str__(self) -> str:
        s_str: str = '-------------------------\n'
        if self.nodes:
            s_str += f"Nodes (#{len(self.nodes)}) [Name(Register)]:\n"
            s_str += ','.join([f"{node}({self.colors[node]})" for node in self.nodes])
        if self.adj:
            s_str += '\nAdjacency List:\n'
            indent: int = max((len(name) for name in self.nodes), default=0)
            for n_id, n_adj in self.adj.items():
                s_str += f"{n_id:>{indent}}: {n_adj if n_adj else '{}'}\n"
        s_str += '-------------------------'
        return s_str


class CFGraph:
    """
    implement logic for a control flow graph.
    """
    def __init__(self) -> None:
        self.nodes: list[CFNode] = []
        self.adj: dict[int, set[int]] = {}
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
        s_str: str = '-------------------------\n'
        s_str += f"Nodes (#{len(self.nodes)}):\n"
        for i, node in enumerate(self.nodes):
            s_str += f"{str(node):<32} interference: {self.interferences[i]}\n"
        s_str += '\nAdjacency List:\n'
        for n_id, n_adj in self.adj.items():
            s_str += f"{n_id:>3}: {n_adj if n_adj else '{}'}\n"
        s_str += '-------------------------\n'
        return s_str
