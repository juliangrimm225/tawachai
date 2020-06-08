class Graph(object):
    
    """A simple python graph class form https://www.python-course.eu/graphs_python.php"""

    def __init__(self, graph_dict = None):
        """ initializes a graph object """
        if graph_dict == None:
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
