import networkx as nx
import json

def create_json(x:int, y:int):

    g = nx.grid_2d_graph(x,y,create_using= nx.DiGraph)
    g = nx.convert_node_labels_to_integers(g,ordering='sorted')


    json_file = {}
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


    with open('arch.json', 'w') as outfile:
        json.dump(json_file, outfile,indent=4)

