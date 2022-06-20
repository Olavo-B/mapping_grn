import networkx as nx
import json
import os

def create_json(x:int, y:int, arch_type='mesh'):


    if arch_type == 'mesh':
        g = nx.grid_2d_graph(x,y,create_using= nx.DiGraph)
        g = nx.convert_node_labels_to_integers(g,ordering='sorted')


    elif arch_type == '1-hop':
        g = nx.grid_2d_graph(x,y,create_using= nx.DiGraph)

        for node in g.nodes():
            if ((node[0] + 2),node[1]) in g.nodes():
                # print(f'creating edge from {node} to {((node[0] + 2),node[1])}')
                g.add_edge(node,((node[0] + 2),node[1]))
            if ((node[0]-2),node[1]) in g.nodes():
                # print(f'creating edge from {node} to {((node[0] - 2),node[1])}')
                g.add_edge(node,((node[0] - 2),node[1]))
            if (node[0],(node[1]+2)) in g.nodes():
                # print(f'creating edge from {node} to {(node[0],(node[1]+2))}')
                g.add_edge(node,(node[0],(node[1]+2)))
            if (node[0],(node[1]-2)) in g.nodes():
                # print(f'creating edge from {node} to {(node[0],(node[1]-2))}')
                g.add_edge(node,(node[0],(node[1]-2))) 
            
        g = nx.convert_node_labels_to_integers(g,ordering='sorted')
    
    elif arch_type == 'chess':
        print('Not implemented yet')
    elif arch_type == 'hex':
        print('Not implemented yet')
    else:
        print(f'{arch_type} not specified, please try again with one of the pre set types')
        return



    json_file = {}
    json_file['arch type'] = arch_type
    json_file['dimension'] = [x,y]
    pe_info_list = []
    for node in g.nodes():
        pe = {}
        pe['id'] = int(node)
        neighbors = []
        for ney in g.neighbors(node):
            neighbors.append(int(ney))
        pe['neighbors'] = neighbors
        pe_info_list.append(pe)
    
    json_file['pe'] = pe_info_list


    path = f"misc/arch/{x}x{y}"  
    file_name = f'arch_{arch_type}_{x}x{y}.json'


    isExist = os.path.exists(path)

    if not isExist:
  
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

    completeName = os.path.join(path, file_name)


    with open(completeName, 'w') as outfile:
        json.dump(json_file, outfile,indent=4)

    return completeName

