import src.include.visualization as visualization
from src.include.generate_arch import create_json 
from src.mappingGRN import mappingGRN as mapping
from src.include.save_script import GRN_paths
import networkx as nx
import pandas as pd
import numpy as np
import pathlib
import glob
import copy

## DataFrame para a machine learning
## What is needed 
## 1. GRN name
## 2. edge id
## 3. worst case
## 4. 
## https://excalidraw.com/#json=XcITaIsJC96KvMA_g7Ug8,2UKreSYssA1QnFkYsTgHnA


COLUMNS     = ['WC', 'Eigenvector', 'Betweenness', 'Closeness']
ARCH        = {'mesh':1,'1-hop':2,'chess':3}
BEST        = 10

def generate_df(file_path,grn_path,results_path):

    GRN,grn_names = GRN_paths(grn_path)
    p = pathlib.Path(results_path)
    results_paths = list(p.glob('**/results*.txt'))

    global_df = pd.DataFrame(columns=COLUMNS)


    # Getting best result one by one
    for results in results_paths:

        # Getting grn name
        aux = str(results)
        aux = aux.split('/')
        aux_grn_name = aux[2]

        grn_name = aux_grn_name.replace('_', ' ')
        grn_index = grn_names.index(grn_name)

        if grn_name != grn_names[grn_index]:
            print(f'ERRO\nwesSA file name: {grn_name} is different from GRN name: {grn_names[grn_index]}')
            break

        # Getting arch type
        aux_arch_type = aux[3].split('.')
        aux_arch_type = aux_arch_type[0].split('_')

        arch_type = aux_arch_type[1]


        # print(f'Processing {grn_name} with a {arch_type}')
        
        # Getting a dict where the key is the test id {N} 
        # and the value is its result {cost}.
        # And then finding the key with minimum value of cost
        x = {}
        with open(results) as results:
            for line in results:
                data = line.split(', ')
                # if data[0] == '1\n': break 
                if data[0] == 'Name': continue
                try:
                    (N,cost) = (data[1],data[4])
                    x[N] = cost
                except: continue 

        x_sorted = dict(sorted(x.items(), key=lambda item: item[1]))
        top_case = list(x_sorted.keys())[:BEST-1]


        # Getting txt that have the best result for wesSA
        # aux_grn_name is the GRN name (using _ as space)
        # d is the id of the test [0...1000]
        mapping_list = []
        for d in top_case:
            p = pathlib.Path(file_path)
            PATHS = list(p.glob(f'**/{aux_grn_name}/{arch_type}/{d}.txt'))

            path = PATHS[0]

            dic =      {}
            with open(path) as f:
                for line in f:
                    (key,val) = line.split()
                    if key == val: # creating arch for that dictionary [NOT USED NOW]
                        arch_path = create_json(int(key),int(val),arch_type=arch_type)
                        continue
                    dic[int(key)] = (" " + val + " ")


            # getting histogram and dot of the best solution from wesSA
            mp = mapping(arch_path,GRN[grn_index],dic)
            mapping_list.append(mp)



        for mp in mapping_list:
            source = get_grn_metadata(mp,arch_type,grn_name)
            if not source: continue
            aux_df = pd.DataFrame(columns=COLUMNS, data = [source])
            global_df = pd.concat([global_df,aux_df],ignore_index=True)

    return global_df

def get_grn_metadata(mp: mapping, arch_type: str, grn_name: str) -> list:
    ''' DataFrame is composed of this columns:

        WC | Eigenvector | Betweenness | Closeness
    '''

    row = []
    G = mp.get_grn()
    row.append(mp.get_worstcase())
    


    n_bridges,g = adjust_graph(G,mp)
    print(G,g)
    try: e = nx.eigenvector_centrality(g,max_iter = 1000)
    except:
        print(f'{g} out of the df') 
        return
    b = nx.betweenness_centrality(g)
    c = nx.closeness_centrality(g)

    e = np.array(list(e.values())).mean()
    b = np.array(list(b.values())).mean()
    c = np.array(list(c.values())).mean()

    row.append(e)
    row.append(b)
    row.append(c)

    return row

def adjust_edge(g: nx.DiGraph, edge) -> None:

    w = int(edge[2]['weight'])
    if w <= 1: return

    # print(f'Adjusting edge from {edge[0]} to {edge[1]}, with a weight of {w}')

    new_node = f'{edge[0]}_b'
    g.add_node(new_node,equation = '')
    g.add_edge(edge[0],new_node,weight='1')
    g.add_edge(new_node,edge[1],weight=f'{(w-1)}')

    g.remove_edge(edge[0],edge[1])

    edge = list(g.edges(new_node,data=True))
    adjust_edge(g,edge[0])

def adjust_graph(G: nx.DiGraph, mp: mapping):

    dist = mp.get_dist_by_edge()
    g = copy.deepcopy(G)
    nx.set_edge_attributes(g,dist,'weight')
    edges = list(g.edges(data = True))
    old_n_nodes = g.number_of_nodes()

    for edge in edges:
        adjust_edge(g,edge)

    new_n_nodes = g.number_of_nodes()
    return (new_n_nodes - old_n_nodes),g


    




    




