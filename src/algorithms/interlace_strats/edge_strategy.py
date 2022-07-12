import networkx as nx

class EdgeStrategy:
    def __init__(self) -> None:
        pass

    def strategy(self) -> None:
        pass

class InDegreeStrategy:
    def __init__(self, grn:nx.DiGraph) -> None:
        self.__grn=grn

    def strat(self,node):
        return self.__grn.degree(node)

    def create_adj(self):
        adj=[]

        for node in self.__grn.nodes():
            neigh_node = list(set(list(self.__grn.neighbors(node))+list(self.__grn.predecessors(node))))
            neigh_node.sort(key=self.strat, reverse=True)
            adj.append(neigh_node)
        return adj

    def strategy(self) -> None:
        print("-- In Degree")

class DecisionTreeMesh:
    def __init__(self,grn:nx.DiGraph, arch:nx.DiGraph) -> None:
        self.__grn=grn
        self.__arch=arch
        self.__betweenness = nx.betweenness_centrality(grn)
        self.__in_degree   = nx.in_degree_centrality(grn)    
        self.__closeness   = nx.closeness_centrality(grn)
        self.__dist=[]
        for i in self.__arch.nodes():
            self.__dist.append(nx.single_source_dijkstra(self.__arch, i)[0])
        self.__rank=self.__set_rank()
    
    def create_adj(self):
        adj=[]  
        for node in self.__grn.nodes:
            neigh_node=[]
            neighbors=list(self.__grn.neighbors(node))
            predecessors=list(self.__grn.predecessors(node))
            
            for src in predecessors:
                neigh_node.append((src,node))

            for tar in neighbors:
                neigh_node.append((node,tar))

            neigh_node.sort(key=self.strat, reverse=True)
            
            final_list=[]
            for edge in neigh_node:
                if edge[0]==node:
                    final_list.append(edge[1])
                else:
                    final_list.append(edge[0])
            adj.append(final_list)
        
        return adj
    def __set_rank(self):
        rank=dict()
        for edge in self.__grn.edges():
            pts=0
            src,tar=edge[0],edge[1]

            if self.__closeness[tar]>=0.126051:  pts+=1
            if self.__in_degree[src]<0.0267822:  pts+=1
            if self.__closeness[src]>=0.126365:  pts+=1
            if self.__in_degree[tar]<0.0339879:  pts+=1
            if self.__betweenness[src]<0.105545: pts+=1

            # if self.__betweenness[src] < 0.105545: pts+=1
            # if self.__dist[src][tar] >= 3.50000: pts+=1
            # if self.__betweenness[tar] < 0.00606008: pts+=1

            rank[edge]=pts
        return rank

    def strat(self,edge):
        return self.__rank[edge]