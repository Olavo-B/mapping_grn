from struct import pack
from src.mappingGRN import mappingGRN as mp
import networkx as nx
import random as rand
import math
from queue import Queue
from queue import PriorityQueue

UP    = -1
DOWN  = 1
LEFT  = -1
RIGHT = 1
direction = [UP,DOWN,LEFT,RIGHT]

def map(grn:nx.DiGraph, mapping:mp, pe:list, myMap:dict, package:tuple):
    
    parent,node = package
  
    if parent == None:
        pex = rand.choice(pe)
        myMap[pex] = node
    else:
        pex = mapping.grn_2_arc(parent)
        is_mapped = False
        dist=1

        while True:
            for dir in direction:
                pey = pex + dir*dist
                if not mapping.arc_2_grn(pey).has_node():   # <-- errado
                    myMap[pey] = node
                    is_mapped=True
                    break
            if is_mapped: break    
            else: dist+=1


def bfs(mapping:mp, grn:nx.DiGraph, node:list):

    pe = list(range(mapping.get_cgra().__len__()))
    myMap = mapping.get_mapped_grn()
    myMap.clear()

    pq = PriorityQueue()
    q  = Queue()

    # init
    source = [node, None]
    node.remove(source)
    q.put(source)

    while not q.empty():
        # process
        u = q.get()
        map(grn,mapping,pe,myMap,u)

        # put in queue
        neighbors_u = grn.predecessors(u[0])
        for neighbor in neighbors_u:
            if neighbor in node:
                node.remove(neighbor)
                pq.put( [neighbor, u[0] ])
        while not pq.empty():
            q.put( pq.get() )
    
    print(myMap)

def interlace(mapping:mp):
    
    # 1° Test Case
    G = nx.Graph()
    G.add_nodes_from(range(10))
    G.add_edges_from([(0,1), (1,3), (1,2), (2,4), (2,6), (4,3), (5,6), (5,7), (6,7), (7,8), (8,9)])
    grn = G

    # Generic Case
    #grn  = mapping.get_grn()

    node = list( grn.in_degree( grn.nodes ) )
    node.sort(key=lambda x: x[1], reverse=True)

    # while node list not empty...
    bfs(mapping,grn,node)
    