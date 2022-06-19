import src.include.json2graph as json2graph
from queue import PriorityQueue
import random as rand
import networkx as nx
import json
import math 

class mappingGRN:

    _instance = None

    def __init__(self, file_path, graph, pre_made = None) -> None:
        self.set_cgra(file_path)
        self.set_grn(graph,pre_made)
        self.cost_table=[]
        self.hist = []
        self.distance_list = PriorityQueue()

        for i in self.cgra.nodes():
            self.cost_table.append(nx.single_source_dijkstra(self.cgra, i)[0])


        for edge in self.grn.edges():
            # Get edge xy from grn
            pe_a = self.grn_2_arc(edge[0])
            pe_b = self.grn_2_arc(edge[1])
            self.distance_list.put((-self.cost_table[pe_a][pe_b],pe_a,pe_b))
            


    # SETS
    def set_cgra(self, file_path) -> None:

        f               = open(file_path)
        f_json          = json.load(f)
        try: self.dimension  = f_json['dimension']
        except: self.dimension = [None,None]
        self.cgra       = json2graph.make_digraph(f_json)
        self.arc_size   = self.cgra.__len__()
        nx.set_edge_attributes(self.cgra,1,'weight')
        nx.set_edge_attributes(self.cgra,'penwidth(0.1)','style')
        nx.set_edge_attributes(self.cgra,'grey89','color')
        nx.set_edge_attributes(self.cgra,' ','tooltip')


        nx.set_node_attributes(self.cgra,'10','fontsize')
        nx.set_node_attributes(self.cgra,'#FFFFFF','fillcolor')
        nx.set_node_attributes(self.cgra,' ','label')
        nx.set_node_attributes(self.cgra,' ','tooltip')
        nx.set_node_attributes(self.cgra,'square','shape')

        f.close()

    def set_grn(self, graph: nx.DiGraph, pre_made ) -> None:
        # init values
        self.wcase = self.cost = 0
        self.ctSwap = 0
        self.allCost=[]
        self.r_mapping = {}
        removed_nodes = []
        for node in graph.nodes():
            if graph.degree(node) == 0:
                removed_nodes.append(node)

        graph.remove_nodes_from(removed_nodes)
        self.grn = graph


        self.__random_mapping(pre_made=pre_made)

    def set_distance_list(self):
        # self.distance_list.put((self.cost_table[x][y],x,y))



        for edge in self.grn.edges():
            # Get edge xy from grn
            pe_a = self.grn_2_arc(edge[0])
            pe_b = self.grn_2_arc(edge[1])
            self.distance_list.put((-self.cost_table[pe_a][pe_b],pe_a,pe_b))

    # GETS
    def get_dimension(self):
        if self.dimension[0] != None: 
            return self.dimension
        else: return None

    def get_distance(self):
        return self.distance_list

    def get_cost(self,source,target):
        return self.cost_table[source][target]

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
        self.generate_wcase()
        return self.wcase

    def get_allcost(self) -> int:
        return self.allCost
  
    def get_num_swaps(self) -> int:
        return self.ctSwap

    def get_dot(self):
        return json2graph.nx_2_dot(self.cgra)

    def get_hist(self) -> dict:
        return self.hist

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

    def get_edge_attr(self) -> dict:
        
        wc = self.get_worstcase()
        dist_label,dist_color = {},{}
        for edge in self.grn.edges():
            pe1 = self.grn_2_arc(edge[0])
            pe2 = self.grn_2_arc(edge[1])

            dist = self.get_cost(pe1,pe2)
            dist_label[edge] = dist

            if dist == wc:
                dist_color[edge] = 'red'
            else:
                dist_color[edge] = 'black'

        return dist_label,dist_color
                                                                                

    # METHODS

    def __random_mapping(self, seed=None, pre_made=None, fit = False) -> None: 
        """ Return a dictionary where the keys are nodes in the architecture and the values are random nodes from the graph.
            Parameters
            ----------
            graph: digraph
                A networkX digraph
                A gene regulatory network that will be used as values for de dictionary.
            Notes
            ----------  
        """
        if pre_made != None:
            self.r_mapping = pre_made
            return
        if seed != None:
            rand.seed(seed)

        empty_pe = []
        # create a list with all pes

        if self.grn.number_of_nodes() < 64 and fit:
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

        try:    
            position = val_list.index(node)
        except:
            print(f"Did't find pe position for {node}, returning itself")
            return node
        return key_list[position]

    def arc_2_grn(self,node):
        try: 
            return self.r_mapping[node]   
        except: return None

    def generate_histogram(self):
        hist = {i : 0 for i in range(1,self.get_worstcase()+1)}

        for node in self.grn.nodes():
            pe1 = self.grn_2_arc(node)
            for neighbor in self.grn.neighbors(node):
                if neighbor == node: continue

                pe2 = self.grn_2_arc(neighbor)
                dist = self.get_cost(pe1,pe2)
                hist[dist]+=1


        self.hist.append(hist)

    def generate_wcase(self):
        wc = 0


        for node in self.grn.nodes():
            pe1 = self.grn_2_arc(node)
            for neighbor in self.grn.neighbors(node):
                if neighbor == node: continue

                pe2 = self.grn_2_arc(neighbor)
                dist = self.get_cost(pe1,pe2)
                if dist > wc : wc = dist


        self.wcase = wc
 
    def total_edge_cost(self) -> int:
        """ Returns the init_cost edge cost from peX to peY.
            Also calculates the worst case cost. """

        # Reset costs
        self.cost=0
        for edge in self.grn.edges():
            # Get edge xy from grn
            x = self.grn_2_arc(edge[0])
            y = self.grn_2_arc(edge[1])

            # Calcualte distance between peX and peY
            dist_xy = self.get_cost(x,y)
            self.cost += dist_xy

        return self.cost

