from tqdm import tqdm
from src.mappingGRN import mappingGRN
import networkx as nx
import random as rand
import math
from src.include.data_map import DataMap
from queue import Queue

## https://excalidraw.com/#json=5AAr7ZdQjEew31PkTHZO6,72cYyJfUvGAXyOuyg2Ws6g

def map(data:DataMap,node,parent):
    if parent==None:
 
        # get random pe
        visited=data.pes()
        pelist=[]
        for i in range(len(visited)):
            if visited[i]==False:
                pelist.append(i)
        pe = rand.choice(pelist)
        data.map(node,pe)
        data.visit_pe(pe)
    else:
        pe = data.mp.grn_2_arc(parent)
        neighbor_parent = data.get_adj(pe)

        # assumindo que num_nodes <= num_pes
        while True:
            aux=[]
            for pe in neighbor_parent:
                if not data.is_pe_visited(pe):
                    data.map(node,pe)
                    data.visit_pe(pe)
                    return
                aux.append( data.get_adj( pe ) )

            flat_list = [x for xs in aux for x in xs]
            flat_list = list(set(flat_list))
            rand.shuffle(flat_list)
            neighbor_parent=flat_list

def bfs(src, data:DataMap):
    q  = Queue()
    
    source=data.make_pair(src)
    data.visit_node(src)
    q.put(source)

    while not q.empty():
        node,parent = q.get()
        map(data,node,parent)
        
        neighbors = data.neighbors(node)

        neigh_in_degree=[]
        for neighbor in neighbors:
            if not data.is_node_visited(neighbor):
                indeg=data.mp.get_grn().in_degree(neighbor)
                
                neigh_in_degree.append( (indeg, neighbor) )
                data.visit_node(neighbor)
        neigh_in_degree.sort(key=lambda x: x[0], reverse=True)
    
        for neigh in neigh_in_degree:
            newNode = data.make_pair(neigh[1],node)
            q.put(newNode)

def interlace(mp:mappingGRN):
    
    data = DataMap(mp)

    best_in_degree = []
    for node in mp.get_grn().nodes:
        best_in_degree.append( (mp.get_grn().in_degree(node), node) )
    best_in_degree.sort(key=lambda x: x[0], reverse=True)

    num_grn_nodes = data.mp.get_grn().number_of_nodes() 
    num_cgra_nodes= data.mp.get_cgra().number_of_nodes()

    if num_grn_nodes > num_cgra_nodes:  
        print(f"Cannot map this grn. grn_nodes::{num_grn_nodes}> cgra_nodes::{num_cgra_nodes}")
        return

    bfs(best_in_degree[0][1], data)




    # # while node list not empty...
    # for src in best_in_degree:
    #     if not data.is_node_visited(src[1]):
    #         print("RESTART")
    #         bfs(src[1], data)
