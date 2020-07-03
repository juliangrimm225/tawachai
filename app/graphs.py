""" Defining the Graph class"""
from copy import deepcopy


class Graph():

    """ A simple python graph class
    https://www.python-course.eu/graphs_python.php """

    def __init__(self, graph_dict=None):
        """ initializes a graph object """
        if graph_dict is None:
            graph_dict = {}
        self.__graph_dict = graph_dict

    def nodes(self):
        """ returns node of a graph """
        return list(self.__graph_dict.keys())

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for sink in self.__graph_dict[vertex]:
                if [vertex, sink] not in edges:
                    edges.append([vertex, sink])
        return edges

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_edge(self, edge):
        [source, sink] = edge
        if edge in self.edges():
            return
        if source in self.__graph_dict:
            self.__graph_dict[source].append(sink)
        else:
            self.__graph_dict[source] = [sink]

    def undirected(self):
        undirected_graph = deepcopy(self)
        for edge in undirected_graph.edges():
            [source, sink] = edge
            reverse_edge = [sink, source]
            undirected_graph.add_edge(reverse_edge)
        return undirected_graph

    def depth_first_search(self, start_node, direction="forward"):
        if direction == "undirected":
            graph = self.undirected()
        elif direction == "forward":
            graph = self
        visited = []

        def dfs(at):
            if at in visited:
                return
            visited.append(at)
            neighbours = graph.__graph_dict[at]
            for next in neighbours:
                dfs(next)
        dfs(start_node)
        return visited

    def connected_components(self):
        components = []
        visited = []
        for node in self.nodes():
            if node in visited:
                continue
            component = self.depth_first_search(start_node=node,
                                                direction="undirected")
            components.append(component)
            visited += component
        return components

    def topsort(self):
        visited = []
        order = []
        nodes = self.nodes()

        def dfs(node):
            if node in visited:
                return
            visited.append(node)
            neighbours = self.__graph_dict[node]
            for next in neighbours:
                dfs(next)
            order.append(node)

        for node in nodes:
            if node in visited:
                continue
            dfs(node)

        order.reverse()

        # test ordering
        edges = self.edges()
        for edge in edges:
            [source, sink] = edge
            if order.index(source) > order.index(sink):
                return

        return order


if __name__ == "__main__":
    g = {
        "a": ["b"],
        "b": ["c", "d"],
        "c": ["d"],
        "d": [],
        "e": [],
        "f": []
        }
    graph = Graph(g)
    print(graph.nodes())
    print(graph.edges())
    print(graph.connected_components())
    print(graph.topsort())
