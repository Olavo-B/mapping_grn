from sys import maxsize
import src.algorithms.interlace_strats.edge_strategy as es
import src.algorithms.interlace_strats.search_strategy as ss
import networkx as nx
import random as rand
from queue import Queue
from collections import Counter

class DoubleCrossing:
    def __init__(self,grn:nx.DiGraph,arch:nx.Graph,dim:int) -> None: # arch graph para mesh!!!!!
        self.__grn=grn
        self.__arch=arch
        self.__dim=dim
        self.__grid_cost=self.__create_grid()
        self.__search_strat=ss.dfsStrategy()        # std search
        self.__edge_strat=es.InDegreeStrategy(grn)  # std edge valuation
        self.__adj=self.__edge_strat.create_adj()
        self.__map=dict()
        self.__cost_table=self.__create_cost_table()
    
    # SET PARAMETERS
    def set_search_strat(self, strat) -> None:
        self.__search_strat=strat
        pass

    def set_edge_strat(self,strat) -> None:
        self.__edge_strat=strat
        self.__adj=self.__edge_strat.create_adj()
        pass

    # TRAVERSE
    def traverse(self) -> None:
        path,notes= self.__exploration()
        map = self.__placement(path,notes)
        return map

    def __exploration(self) -> tuple:

        edges = list(self.__grn.edges)
        edges.sort(key=self.__edge_strat.strat, reverse=True)
        
        nodes=[]
        for edge in edges:
            nodes.append(edge[0])
            nodes.append(edge[1])
        nodes = list(dict.fromkeys(nodes))
        
        n = len(nodes)

        return self.__search_strat.search(n, self.__adj, nodes)

    def __placement(self, path, notes) -> dict:
        
        # Place source
        source=path[0][0]
        val=self.__grn.degree(source)
        min_val, pos=maxsize,0
        for i in range(len(self.__grid_cost)):            
            diff=val-self.__grid_cost[i]
            if diff<min_val: 
                min_val=diff
                pos=i
                if diff==0: break
        self.__place(source,pos)
        self.__update_grid(pos)

        # Place seq
        for node in path:
            src=node[0]
            tar=node[1]

            # Vizinhos de par
            neighbor_src = self.__bfs_neighbors(src)
            #print("NEIGH",list(set(neighbor_src)))

            # Anotações + vizinhos par
            possible_pe=list(set(neighbor_src + notes[tar]))

            # Grid cost
            val=self.__grn.degree(tar)
            pos=0
            fit=[]
            for node in possible_pe:
                if self.__grid_cost[node]>=val:
                    fit.append(node)

            pos = rand.choice(possible_pe+fit)

            self.__place(tar,pos)
            self.__update_grid(pos)

        return self.__map.copy()

    # OTHER METHODS
    def __place(self,tar,pos):
        self.__map[tar]=pos

    def __update_grid(self,pos):
        self.__grid_cost[pos]=0
        for neighbor in self.__arch.neighbors(pos):
            self.__grid_cost[neighbor]-=1

    def __create_grid(self) -> None:
        grid_cost=[]
        for node in self.__arch.nodes:
            grid_cost.append(len(self.__arch[node]))
        return grid_cost

    def __create_cost_table(self) -> None:
        cost_table=[]
        for i in self.__arch.nodes():
            cost_table.append(nx.single_source_dijkstra(self.__arch, i)[0])
        return cost_table

    def __neighbors(self,node):
        neighbors=list(self.__grn.neighbors(node))
        predecessors=list(self.__grn.predecessors(node))
        return list(set(neighbors+predecessors))

    def worst_case(self):
        wc = 0
        for src in self.__grn.nodes():
            try: 
                pe1 = self.__map[src]
            except:
                continue
            
            for tar in self.__neighbors(src):
                if src == tar: continue
                try:
                    pe2 = self.__map[tar]
                except: continue                
                dist = self.__cost_table[pe1][pe2]
                if dist > wc : wc = dist
        return wc

    def __bfs_neighbors(self,v):

        visited=[False]*self.__arch.number_of_nodes()
        neighbors=[]
        q = Queue()

        visited[v]=True
        q.put(v)
        
        min_dist=maxsize

        while not q.empty():
            node = q.get()
            for neighbor in self.__arch.neighbors(node):
                if self.__grid_cost[neighbor]<=0 and not visited[neighbor]:
                    q.put(neighbor)
                    visited[neighbor]=True
                else:
                    dist=self.__cost_table[node][neighbor]
                    if dist<min_dist:
                        min_dist=dist
                        neighbors.append(neighbor)
                    
        
        return neighbors

    def debug(self) -> None:
        print(f"-- GRN {self.__grn}")
        print(f"-- ARCH. {self.__arch}")
        print(f"-- DIM. {self.__dim}")
        self.__search_strat.strategy()
        self.__edge_strat.strategy()
        pass