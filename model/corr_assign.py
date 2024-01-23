# This file contains the class CorrFlowModel the necessary functionalities
# for computing the correlated equilibrium strategy profile
# for N users in the traffic network

from model.graph import Graph, TrafficNetwork

class CorrFlowModel:
    """_Correlated Equilibrium Assignment Model_
        Inside the algorithm by:
        Yuqiang Ning, Lili Du,
Robust and resilient equilibrium routing mechanism for traffic congestion mitigation built upon correlated equilibrium and distributed optimization,
Transportation Research Part B: Methodological,
Volume 168,
2023,
Pages 170-205,
ISSN 0191-2615,
https://doi.org/10.1016/j.trb.2022.12.006.
(https://www.sciencedirect.com/science/article/pii/S0191261522002089)
    
    """
    def __init__(self, graph=None, origins=None, destinations=None,
                num_users=None, link_free_time= None, link_capacity= None):
        
        self.__network = TrafficNetwork(graph=graph, O=origins, D=destinations)

        self.__link_free_time = np.array(link_free_time)
        self.__link_capacity = np.array(link_capacity)
        self.__num_users = num_users
        self.__user_set = np.range(self.__num_users)

        # Alpha and beta (used in performance function)
        self._alpha = 0.15
        self._beta = 4 

        # Convergent criterion
        self._conv_accuracy = 1e-5

        # Boolean varible: If true print the detail while iterations
        self.__detail = False

        # Boolean varible: If true the model is solved properly
        self.__solved = False

        # Some variables for contemporarily storing the
        # computation result
        self.__final_link_flow = None
        
        # The Decision Variable for recommendation system
        self.__Corr_P = None
        self.__iterations_times = None

    
    def __insert_links_in_order(self, links):
        ''' Insert the links as the expected order into the
            class incidence `CorrFlowModel.__network`
        '''
        first_vertice = [link[0] for link in links]
        for vertex in first_vertice:
            self.__network.add_vertex(vertex)
        for link in links:
            self.__network.add_edge(link)

    def corr_assign(self):
        """_the equilibrium solver_
            return flag self.__solved = True 
        """
        if self.__detail:
            print(self.__dash_line())
            print("Atomic Assignment with Correlated Equilibrium \nPrimal-Dual Algo - DETAIL OF ITERATIONS")
            print(self.__dash_line())
            print(self.__dash_line())
            print("Initialization")
            print(self.__dash_line())

        # step 0, initialize the P matrix 
        self.__Corr_P = np.zeros(())

        while True: 
            pass

    
    def _sol_formatted(self):
        if self.__solved:
            link_flow = self.__final_link_flow
            link_time = self.__link_flow_to_link_time(link_flow)
            path_time = self.__link_time_to_path_time(link_time)
            link_vc = link_flow / self.__link_capacity
            return link_flow, link_time, path_time, link_vc
        else:
            return None


    def __link_time_to_path_time(self, link_time):
        ''' Based on current link traveling time,
            use link-path incidence matrix to compute 
            the path traveling time.
            The input is an array.
        '''
        return link_time.dot(self.__network.LP_matrix())
    
    def __path_flow_to_link_flow(self, path_flow):
        ''' Based on current path flow, use link-path incidence 
            matrix to compute the traffic flow on each link.
            The input is an array.
        '''
        return self.__network.LP_matrix().dot(path_flow)

    def _get_path_free_time(self):
        ''' Only used in the final evaluation, not the recursive structure
        '''
        return self.__link_free_time.dot(self.__network.LP_matrix())

    def __object_function(self):
        val = 0
        return val

    def __is_convergent(self):
        pass

    def __dash_line(self):
        ''' 
        display a set of dashed lines to separate printed information
        '''
        return "-" * 80

    def __str__(self):
        string = ""
        string += self.__dash_line()
        string += "\n"
        string += "Correlated Equilibrium Model \nPrimal-Daul - PARAMS OF MODEL"
        string += "\n"
        string += self.__dash_line()
        string += "\n"
        string += self.__dash_line()
        string += "\n"
        string += "LINK Information:\n"
        string += self.__dash_line()
        string += "\n"
        for i in range(self.__network.num_of_links()):
            string += "%2d : link= %s, free time= %.2f, capacity= %s \n" % (i, self.__network.edges()[i], self.__link_free_time[i], self.__link_capacity[i])
        string += self.__dash_line()
        string += "\n"
        string += "OD Pairs Information:\n"
        string += self.__dash_line()
        string += "\n"
        for i in range(self.__network.num_of_OD_pairs()):
            string += "%2d : OD pair= %s, demand= %d \n" % (i, self.__network.OD_pairs()[i], self.__demand[i])
        string += self.__dash_line()
        string += "\n"
        string += "Path Information:\n"
        string += self.__dash_line()
        string += "\n"
        for i in range(self.__network.num_of_paths()):
            string += "%2d : Conjugated OD pair= %s, Path= %s \n" % (i, self.__network.paths_category()[i], self.__network.paths()[i])
        string += self.__dash_line()
        string += "\n"
        string += f"Link-Path Incidence Matrix (Rank: {self.__network.LP_matrix_rank()}):\n"
        string += self.__dash_line()
        string += "\n"
        string += str(self.__network.LP_matrix())
        return string