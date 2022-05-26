

import src.include.json2graph as json2graph
import src.algorithms.simulated_anealling as sa
import networkx as nx
import json
import math 
import random as rand

class mappingGRN:

    _instance = None

    def __init__(self, file_path, graph) -> None:
        self.set_cgra(file_path)
        self.set_grn(graph)



    # SETS
    def set_cgra(self, file_path) -> None:
        f               = open(file_path)
        self.cgra       = json2graph.make_digraph(json.load(f))
        self.arc_size   = self.cgra.__len__()
        nx.set_edge_attributes(self.cgra,1,'weight')
        nx.set_edge_attributes(self.cgra,'penwidth(0.1)','style')
        nx.set_edge_attributes(self.cgra,'grey89','color')
        nx.set_edge_attributes(self.cgra,' ','tooltip')


        nx.set_node_attributes(self.cgra,'8','fontsize')
        nx.set_node_attributes(self.cgra,'#FFFFFF','fillcolor')
        nx.set_node_attributes(self.cgra,' ','label')
        nx.set_node_attributes(self.cgra,' ','tooltip')
        nx.set_node_attributes(self.cgra,'square','shape')

        f.close()


    def set_grn(self, graph: nx.DiGraph ) -> None:
        # init values
        self.wcase = self.cost = 0
        self.ctSwap = 0
        self.allCost=[]
        self.r_mapping = {}
        self.grn = graph


        self.__random_mapping()

    # GETS
    def get_arc_size(self) -> int:
        return self.arc_size

    def get_cgra(self) -> nx.DiGraph:
        return self.cgra


    def get_grn(self) -> nx.DiGraph:
        return self.grn


    def get_mapped_grn(self) -> dict:
        ''' Return r_mapping
        '''
        return self.r_mapping


    def get_worstcase(self) -> int:
        return self.wcase


    def get_allcost(self) -> int:
        return self.allCost

    
    def get_num_swaps(self) -> int:
        return self.ctSwap


    def get_dot(self):
        return json2graph.nx_2_dot(self.cgra)

    def display_arc(self):
        bline = math.sqrt(self.arc_size)
        for i in range(self.arc_size):
            if i%bline==0 : print()
            node = self.arc_2_grn(i)
            if(self.grn.has_node(node)):
                print(node[1], end=' ')
            else: 
                print('-', end=' ')
        print()

    def get_all_stats(self) -> None:
        print(
            f"{'Number of PEs in CGRA:' : <30}{self.get_arc_size() : >10}",
            f"\n{'Number of genes in the GRN:' : <30}{self.get_grn().number_of_nodes() : >10}",
            f"\n{'Total number of swaps:' : <30}{self.get_num_swaps() : >10}",
            f"\n{'Total cost:' : <30}{self.total_edge_cost() : >10}",
            f"\n{'Worst path cost:' : <30}{self.get_worstcase() : >10}"
        )
                                                                                

    # METHODS


    def __random_mapping(self, seed=None) -> None: 
        """ Return a dictionary where the keys are nodes in the architecture and the values are random nodes from the graph.
            Parameters
            ----------
            graph: digraph
                A networkX digraph
                A gene regulatory network that will be used as values for de dictionary.
            Notes
            ----------  
        """
        if seed != None:
            rand.seed(seed)

        empty_pe = []
        # create a list with all pes

        if self.grn.number_of_nodes() < 64:
            for i in range(2,10):
                for j in range(2,10):
                    empty_pe.append(15 * i + j) # fixado para arch 15x15
        else:
            empty_pe = list(range(self.arc_size))
        
        # choose random values [0, arcSize_nXn) to map the grn nodes in it
        arc_nodes = rand.sample(empty_pe, len( self.grn.nodes() ) )

        # map PE : NODE
        for node, k in zip(self.grn.nodes(), arc_nodes):
            self.r_mapping[k] = node

    def grn_2_arc(self,node):
        """ Give one node in the GRN, return the CGRA's node that it is in.

            Parameters
            ----------
            node: string
                A node in the GRN graph

            Returns
            ----------
            A node in the CGRA.

            Notes
            -
        """
        key_list = list(self.r_mapping.keys())
        val_list = list(self.r_mapping.values())

        try:    position = val_list.index(node)
        except: return node
        return key_list[position]


    def arc_2_grn(self,node):
        try: 
            return self.r_mapping[node]   
        except: return None
 
    def total_edge_cost(self) -> int:
        """ Returns the init_cost edge cost from peX to peY.
            Also calculates the worst case cost. """

        # Reset costs
        self.cost,self.wcase=0,0
        for edge in self.grn.edges():
            # Get edge xy from grn
            x = self.grn_2_arc(edge[0])
            y = self.grn_2_arc(edge[1])

            # Calcualte distance between peX and peY
            dist_xy = nx.dijkstra_path_length(self.cgra,x,y)
            self.cost += dist_xy

            # Calculate worst case
            if dist_xy > self.wcase: self.wcase = dist_xy

        return self.cost

