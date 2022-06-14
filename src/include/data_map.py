from src.mappingGRN import mappingGRN

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
        pred = list(self.mp.get_grn().predecessors(node))
        neig = list(self.mp.get_grn().neighbors(node))
        return list(set(pred+neig))

    # debug
    def debug(self):
        print(self.mp.r_mapping)