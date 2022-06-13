from src.mappingGRN import mappingGRN
import networkx as nx
import random as rand
import math
from queue import Queue
from queue import PriorityQueue

## https://excalidraw.com/#json=5AAr7ZdQjEew31PkTHZO6,72cYyJfUvGAXyOuyg2Ws6g

class DataMap(mappingGRN):
    def __init__(self,mp:mappingGRN) -> None:
        self.mp = mp
        self.mp.r_mapping={}
        self.nodeidx={}

        # node
        self.visited_node=[False]*mp.get_grn().number_of_nodes()
        
        idx=0
        for node in self.mp.get_grn().nodes:
            self.nodeidx[node]=idx
            idx+=1

        # pe
        self.visited_pe=[False]*mp.get_arc_size()
        self.adj = self.create_adjacency()
    
    def map(self,node,pe):
        self.mp.r_mapping[pe]=node

    def get_adj(self,pe):
        return self.adj[pe]

    # pe
    def create_adjacency(self):
        adj_iter = self.mp.get_cgra().adjacency()
        adj=[]
        for pair in adj_iter:
            adj.append(( int(pair[0]) ,list(pair[1].keys())))
        
        adj.sort(key=lambda x: x[0])
        for i in range(len(adj)):
            adj[i] = adj[i][1]
        return adj
    
    def visit_pe(self,node):
        self.visited_pe[node]=True

    def is_pe_visited(self,node):
        if self.visited_pe[node]==True: return True
        return False

    def pes(self):
        return self.visited_pe

    # node
    def visit_node(self,node):
        pos = self.nodeidx[node]
        self.visited_node[pos]=True
    
    def is_node_visited(self,node):
        pos = self.nodeidx[node]
        if self.visited_node[pos]==True: return True
        return False

    def make_pair(self,node,parent=None):
        return (node,parent)
    
    def nodes(self):
        return self.visited_node

    def neighbors(self,node):
        return list(self.mp.get_grn().predecessors(node))

    # debug
    def debug(self):
        # print("adjacency list")
        # for i in range(self.mp.get_arc_size()):
        #     print(self.adj[i])
        print(self.mp.r_mapping)

def map(data:DataMap,node,parent):
    if parent==None:
        
        # get random pe
        visited=data.pes()
        pelist=[]
        for i in range(len(visited)):
            if visited[i]==False:
                pelist.append(i)
        pe = rand.choice(pelist)
        
        #print(f"mapping node {node} in pe {pe}.")
        
        data.map(node,pe)
        data.visit_pe(pe)
        data.debug()

    else:
        pe = data.mp.grn_2_arc(parent)
        neighbor_parent = data.get_adj(pe)
        #print(f"Neighbor parent of pe {pe}: {neighbor_parent}")
        
        # assumindo que num_nodes <= num_pes
        while True:
            aux=[]
            for pe in neighbor_parent:
                if not data.is_pe_visited(pe):
                    #print(f"mapping node {node} in pe {pe}.")
                    data.map(node,pe)
                    data.visit_pe(pe)
                    return
                aux.append( data.get_adj( pe ) )

            flat_list = [x for xs in aux for x in xs]
            flat_list = list(set(flat_list))
            neighbor_parent=flat_list

def bfs(src, data:DataMap):
    q  = Queue()
    
    source=data.make_pair(src)
    data.visit_node(src)
    q.put(source)

    #print(f"source: {source}")

    while not q.empty():
        node,parent = q.get()
        map(data,node,parent)
        
        neighbors = data.neighbors(node)
        #print(f"neighbors of node {node}: {neighbors}")

        neigh_in_degree=[]
        for neighbor in neighbors:
            if not data.is_node_visited(neighbor):
                indeg=data.mp.get_grn().in_degree(neighbor)
                
                neigh_in_degree.append( (indeg, neighbor) )
                data.visit_node(neighbor)
        neigh_in_degree.sort(key=lambda x: x[0], reverse=True)

        #print(f"put in queue {neigh_in_degree}")
        
        for neigh in neigh_in_degree:
            newNode = data.make_pair(neigh[1],node)
            #print(newNode)
            q.put(newNode)
        #print()

            
def interlace(mp:mappingGRN):
    
    data = DataMap(mp)

    best_in_degree = []
    for node in mp.get_grn().nodes:
        best_in_degree.append( (mp.get_grn().in_degree(node), node) )
    best_in_degree.sort(key=lambda x: x[0], reverse=True)

    #print(best_in_degree)

    num_grn_nodes = data.mp.get_grn().number_of_nodes() 
    num_cgra_nodes=data.mp.get_cgra().number_of_nodes()

    if num_grn_nodes > num_cgra_nodes:  
        print(f"Cannot map this grn. grn_nodes::{num_grn_nodes}> cgra_nodes::{num_cgra_nodes}")
        return

    # while node list not empty...
    for src in best_in_degree:
        if not data.is_node_visited(src[1]):
            #print(src[1], data.is_node_visited(src[1]))
            bfs(src[1], data)
    #data.debug()
        