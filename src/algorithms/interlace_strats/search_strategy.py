
class SearchStrategy:
    def __init__(self) -> None:
        pass
    
    def strategy(self) -> None:
        pass

    def search(self) -> None:
        pass

class dfsStrategy(SearchStrategy):
    def __init__(self) -> None:
        super().__init__()
        pass
    
    def __is_cycle(self, node, adj, visited, memo, path, notes):
        # marca como visitado
        visited[node]=True
        memo[node]=True

        for neighbor in adj[node]:
            if not visited[neighbor]: # Se vizinho não visitado
                path.append((node,neighbor))
                self.__is_cycle(neighbor, adj, visited, memo, path, notes) # visita
            
            elif memo[neighbor]: # Se foi, checa se ciclo 
                if (neighbor,node) not in path:
                    notes[neighbor].append(node)
        memo[node]=False

    def search(self, n, adj, nodes) -> None:
        visited = [False]*n
        memo = [False]*n
        notes=[ [] for i in range(n) ]
        path=[]

        for node in nodes: # <- Trocar por lista com prioridade de nó!!
            if not visited[node]: 
                self.__is_cycle(node, adj, visited, memo, path, notes)
    
        return path, notes

    def strategy(self) -> None:
        print("-- Depth First Seach")