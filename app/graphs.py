""" Defining the Graph class"""
class Graph():

    """ A simple python graph class form https://www.python-course.eu/graphs_python.php """

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
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    @staticmethod
    def depth_first_search(starting_node, direction='forward'):
        """ Runs a depth first search from a node in the graph.
        The direction can be 'forward', 'backward' or 'undirected'."""

        visited = []
        def dfs(node):
            if node in visited:
                return
            visited.append(node)
            if direction == 'forward':
                neighbours = node.sinks()
            elif direction == 'backward':
                neighbours = node.sources()
            elif direction == 'undirected':
                neighbours = node.sinks()+node.sources()
            for neighbour in neighbours:
                dfs(neighbour)
        dfs(starting_node)
        return visited

    def weak_components(self):
        """Returns a list of the components of weak components of an directed graph."""
        visited = []
        components = []
        nodes = self.nodes()
        for node in nodes:
            while node not in visited:
                dfs = self.depth_first_search(starting_node=node, direction='undirected')
                visited = visited + dfs
                components.append(dfs)
        return components

    def strong_components(self):
        pass

        
