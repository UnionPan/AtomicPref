# This file contains two classes: the base class Graph,
# based on which transportation network class is constructed using demand info
# The assignment model should be based on the Tran 
import numpy as np


class Graph(object):
    def __init__(self, graph_dict= None) -> None:
        """ 
        Transportation network: no self-loop
        inputs:
            graph_dictionary, if none, then initialize with empty graph
        """
        from collections import OrderedDict
        if graph_dict is None:
            graph_dict = OrderedDict()
        self.__graph_dict = OrderedDict(graph_dict)
        if self.__is_with_loop():
            raise ValueError("The graph are supposed to be without self-loop please recheck the input data!")
    
    def vertices(self):
        """ 
        returns the vertices of a graph
        """
        return list(self.__graph_dict.keys())

    def edges(self):
        """ 
        returns the edges of a graph
        """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ 
        If the vertex "vertex" is not in 
        self._graph_dict, a node without edge connection 
        is added to the dictionary.  
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []
        else:
            print(f"The vertex {vertex} already exists in the graph and has been ignored")


    def add_edge(self, edge):
        """ 
        edge is ordered, and between two 
        vertices there could exists only one edge. 
        """
        vertex1, vertex2 = self.__decompose_edge(edge)
        if self.__is_edge_in_graph(edge):
            print("The edge %s already exists in the graph, thus it has been ignored!" % ([vertex1, vertex2]))

        elif vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
            if vertex2 not in self.__graph_dict:
                self.__graph_dict[vertex2] = []
        else:
            self.__graph_dict[vertex1] = [vertex2]

    def find_all_paths(self, start_vertex, end_vertex, path=None):
        """ 
        find all simple paths (path with no repeated vertices)
        from start vertex to end vertex in graph 
        """
        if path is None:
            path = []
        path = path + [start_vertex]
        if start_vertex == end_vertex:
            return [path]
        paths = []
        for neighbor in self.__graph_dict[start_vertex]:
            if neighbor not in path:
                sub_paths = self.find_all_paths(neighbor, end_vertex, path)
                paths.extend(iter(sub_paths))
        return paths

    def __is_edge_in_graph(self, edge):
        """ 
        return if an edge is already in the graph
        """
        vertex1, vertex2 = self.__decompose_edge(edge)
        return vertex1 in self.__graph_dict and vertex2 in self.__graph_dict[vertex1]
    
    def __decompose_edge(self, edge):
        """ 
        return the two nodes in order that connect through this edge
        """
        if (isinstance(edge, (list, tuple))) and len(edge) == 2:
            return edge[0], edge[1]
        else:
            raise ValueError(
                f"{edge} is not of type list or tuple or its length does not equal to 2"
            )

    def __is_with_loop(self):
        """ If the graph contains a self-loop, that is, an 
            edge connects a vertex to itself, then return
            True, otherwise return False
        """
        return any(vertex in self.__graph_dict[vertex] for vertex in self.__graph_dict)
    
    def __generate_edges(self):
        """ 
        A static method generating the edges of the 
        graph "graph". Edges are represented as list
        of two vertices 
        """
        edges = []
        for vertex in self.__graph_dict:
            edges.extend([vertex, neighbor] for neighbor in self.__graph_dict[vertex])
        return edges

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += f"{str(k)} "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += f"{str(edge)} "
        return res



class TrafficNetwork(Graph):
    """Traffic Network Class"

    Inputs:
        Graph (_class_): _the graph incidence without self-loop
        O: Orgins
        D: Destinations
    Generate the Paths by demand, edge-path incident matrix
    """
    def __init__(self, graph= None, O=None, D=None):
        if O is None:
            O = []
        if D is None:
            D = []
        Graph.__init__(self, graph)
        self.__origins = O
        self.__destinations = D
        self.__cast()

    # Override of add_edge function, notice that when an edge
    # is added, then the links and paths will changes alongside.
    # However, it doesn't matter when a vertex is added
    def add_edge(self, edge):
        Graph.add_edge(self, edge)
        self.__cast()

    def add_origin(self, origin):
        if origin not in self.__origins:
            self.__origins.append(origin)
            self.__cast()
        else:
            print(f"The origin {origin} already exists, thus has been ignored!")

    def add_destination(self, destination):
        if destination not in self.__destinations:
            self.__destinations.append(destination)
            self.__cast()
        else:
            print(f"The destination {destination} already exists, thus has been ignored!")

    def num_of_links(self):
        return len(self.__links)

    def num_of_paths(self):
        return len(self.__paths)

    def num_of_OD_pairs(self):
        return len(self.__OD_pairs)

    def __cast(self):
        """ 
        Calculate or re-calculate the links, paths and
        Link-Path incidence matrix
        """
        if self.__origins != None and self.__destinations != None:
            self.__OD_pairs = self.__generate_OD_pairs()
            self.__links = self.edges()
            self.__paths, self.__paths_category = self.__generate_paths_by_demands()
            self.__LP_matrix = self.__generate_LP_matrix()
    
    def __generate_OD_pairs(self):
        ''' 
        Generate the OD pairs by Cartesian production 
        '''
        OD_pairs = []
        for o in self.__origins:
            OD_pairs.extend([o, d] for d in self.__destinations)
        return OD_pairs

    def __generate_paths_by_demands(self):
        """ 
        path_category: path sets indexed by OD pairs
        path_by_demands: a list of path lists
        """ 
        paths_by_demands = []
        paths_category = []
        for od_pair_index, OD_pair in enumerate(self.__OD_pairs):
            paths = self.find_all_paths(*OD_pair)
            paths_by_demands.extend(paths)
            paths_category.extend([od_pair_index] * len(paths))
        return paths_by_demands, paths_category

    def __generate_LP_matrix(self):
        """ 
        Generate the Link-Path incidence matrix Delta:
        if the i-th link is on j-th link, then delta_ij = 1,
        otherwise delta_ij = 0
        """
        n_links = self.num_of_links()
        n_paths = self.num_of_paths()
        lp_mat = np.zeros(shape= (n_links, n_paths), dtype= int)
        for path_index, path in enumerate(self.__paths):
            for i in range(len(path) - 1):
                current_link = self.__get_link_from_path_by_order(path, i)
                link_index = self.__links.index(current_link)
                lp_mat[link_index, path_index] = 1
        return lp_mat
    
    def __get_link_from_path_by_order(self, path, order):
        """
        Given a path, which is a list with length N, 
        search the link by order, which is a integer
        in the range [0, N-2]
        """
        if len(path) < 2:
            raise ValueError(f"{path} contains only one vertex and cannot be input!")
        if order >= 0 and order <= len(path) - 2:
            return [path[order], path[order+1]]
        else:
            raise ValueError("%d is not in the reasonable range!" % order)

    def disp_links(self):
        ''' 
        Print all the links in the network by order
        '''
        for counter, link in enumerate(self.__links):
            print("%d : %s" % (counter, link))

    def disp_paths(self):
        """ 
        Print all the paths in order according to
        given origins and destinations
        """
        for counter, path in enumerate(self.__paths):
            print("%d : %s " % (counter, path))

    def LP_matrix(self):
        ''' 
        Return the Link-Path matrix of
        current traffic network
        '''
        return self.__LP_matrix

    def LP_matrix_rank(self):
        ''' 
        Return the rank of Link-Path matrix
        of current traffic network
        '''
        
        return np.linalg.matrix_rank(self.__LP_matrix)

    def OD_pairs(self):
        """ 
        Return the origin-destination pairs of
        current traffic network
        """
        return self.__OD_pairs

    def paths_category(self):
        """ 
        Return a list which implies the conjugacy
        between path and OD pairs
        """
        return self.__paths_category

    def paths(self):
        """ 
        Return the paths with respected to given
        origins and destinations 
        """
        return self.__paths