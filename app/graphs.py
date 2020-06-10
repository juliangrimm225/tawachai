from collections import deque

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

    def isolated_nodes(self):
        isolated_nodes = []
        for node in self.nodes():
            if node.sinks() == [] and node.sources() == []:
                isolated_nodes.append(node)
        return isolated_nodes

    def depth_first_search(self, starting_node, direction = 'forward'):
        """Runs a depth first search from a node in the graph. The direction can be 'forward', 'backward' or 'undirected'."""
        
        visited = []
        def dfs(at):
            if at in visited:
                return
            else:
                visited.append(at)
                if direction == 'forward':
                    neighbours = at.sinks()
                elif direction == 'backward':
                    neighbours = at.sources()
                elif direction == 'undirected':
                    neighbours = at.sinks()+at.sources()

                for next in neighbours:
                    dfs(next)
        dfs(starting_node)
        return visited

    def connected_components(self):
        nodes = g.nodes()
        if nodes == []:
            return []
        components = []
        visited = []
        for n in nodes:
            if n in visited:
                break
            c = self.depth_first_search(n, direction = 'undirected')
            components.append(c)
            visited += c
        return components

    def strongly_connected_components(self):
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        result = []

        def strongconnect(node):
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)

            try:
                successors = node.sinks()
            except:
                successors = []
            for successor in successors:
                if successor not in lowlinks:
                    strongconnect(successor)
                    lowlinks[node] = min(lowlinks[node],lowlinks[successor])
                elif successor in stack:
                    lowlinks[node] = min(lowlinks[node], index[successor])

            if lowlinks[node] == index[node]:
                connected_component = []

                while True:
                    successor = stack.pop()
                    connected_component.append(successor)
                    if successor == node: break
                component = tuple(connected_component)
                result.append(component)

        for node in self.nodes():
            if node not in lowlinks:
                strongconnect(node)

        return result
                
    def topological_sort(self):
        count = {}
        for node in self.nodes():
            count[node]=0
        for node in self.nodes():
            for successor in node.sinks():
                count[successor] += 1

        ready = [ node for node in self if count[node] == 0 ]

        result = []
        while ready:
            node = ready.pop(-1)
            result.append(node)

            for successor in node.sinks():
                count[successor] -= 1
                if count[successor] == 0:
                    ready.append(successor)

        return result

    def robust_topological_sort(self):
        
        components = self.strongly_connected_components()

        node_component = {}
        for component in components:
            for node in component:
                node_component[node] = component

        component_graph = {}
        for component in components:
            component_graph[component] = []

        for node in self.nodes():
            node_c = node_component[node]
            for successor in node.sinks():
                successor_c = node_component[successor]
                if node_c != successor_c:
                    component_graph[node_c].append(successor_c)

        return topological_sort(component_graph)
