import src.include.visualization as visualization
import statistics as stat
import networkx as nx
import pandas as pd
import scipy as sp
import pathlib
import glob

from src.include.generate_arch import create_json 
from src.mappingGRN import mappingGRN as mapping
from src.include.save_script import GRN_paths
from tabulate import tabulate

## DataFrame para a machine learning
## https://excalidraw.com/#json=XcITaIsJC96KvMA_g7Ug8,2UKreSYssA1QnFkYsTgHnA

# COLUMN NAMES
COLS  = ['name', 'edge', 'arch_type', 'worst_case', 'dist_src_tar', 
            'src_indeg', 'src_eigenvector', 'src_closeness', 'src_betweenness',
            'tar_indeg', 'tar_eigenvector', 'tar_closeness', 'tar_betweenness']


# SIZE OF LIST WITH BEST RESULTS
BEST      = 10

# AUX. FUNCTIONS 
def split_name(res):
    name_ = res[2]
    name  = res[2].replace('_', ' ')
    return name, name_

def split_type(res):
    type = res[3].split('.')[0].split('_')[1]
    return type

def get_line(row):
    line = [l for l in row]
    return line

def generate_df(file_path,grn_path,results_path,ARCH_TYPE):

    print("Working on results...")

    arch_dict={'mesh':0, '1-hop':1, 'chess':2}
    arch_list=['mesh','1-hop','chess']

    GRN,grn_names = GRN_paths(grn_path)
    p = pathlib.Path(results_path)
    results_paths = list(p.glob('**/results*.txt'))
    
    df = pd.DataFrame(columns=COLS)

    #Getting best result one by one
    for results in results_paths:
        
        res = str(results).split('/')

        # Getting grn name
        grn_name, grn_path = split_name(res)
        grn_index = grn_names.index(grn_name)

        if grn_name != grn_names[grn_index]:
            print(f'ERRO\nwesSA file name: {grn_name} is different from GRN name: {grn_names[grn_index]}')
            break
        
        # Getting arch type
        arch_type = split_type(res)
        
        if arch_dict[arch_type]!=ARCH_TYPE: continue

        # Getting a dict where the key is the test id {N} 
        # and the value is its result {cost}.
        # And then finding the key with minimum value of cost
        x = {}
        with open(results) as results:
            for line in results:
                data = line.split(', ')
                if data[0] == 'Name': continue
                try:
                    (N,cost) = (data[1],data[4])
                    x[N] = cost
                except: continue 

        # Select the top results
        x_sorted = dict(sorted(x.items(), key=lambda item: item[1]))
        top_case = list(x_sorted.keys())[:BEST-1]

        eigenvector = nx.centrality.eigenvector_centrality_numpy(GRN[grn_index])
        betweenness = nx.betweenness_centrality(GRN[grn_index])
        in_degree   = nx.in_degree_centrality(GRN[grn_index])    
        closeness   = nx.closeness_centrality(GRN[grn_index])

        print(f"processing {grn_name} {arch_type}.", end=' ')

        for case in top_case:
            # Getting txt that have the best result for wesSA
            p = pathlib.Path(file_path)
            PATHS = list(p.glob(f'**/{grn_path}/{arch_type}/{case}.txt'))
            path = PATHS[0]
            
            dic =      {}
            with open(path) as f:
                for line in f:
                    (key,val) = line.split()
                    if key == val: # creating arch for that dictionary [NOT USED NOW]
                        arch_path = create_json(int(key),int(val),arch_type=arch_type)
                        continue
                    dic[int(key)] = (" " + val + " ")

            mp = mapping(arch_path,GRN[grn_index],dic)
            wc = mp.get_worstcase()

            # if wc <= 4: wc = 2
            # elif wc <= 10: wc = 5
            # elif wc <= 13: wc = 11

            for edge in GRN[grn_index].edges:
                
                src  = edge[0]
                dest = edge[1]

                pe1=mp.grn_2_arc(src)
                pe2=mp.grn_2_arc(dest)

                data = [grn_name, edge, ARCH_TYPE, wc, mp.get_cost(pe1,pe2),
                        in_degree[src], eigenvector[src], closeness[src], betweenness[src],
                        in_degree[dest], eigenvector[dest], closeness[dest], betweenness[dest]]
                
                new_df = pd.DataFrame(data=[data], columns=COLS)
                df     = pd.concat([df, new_df])
        print("ok")
        

    df.to_csv('misc/dataframes/df_edges_'+ arch_list[ARCH_TYPE] +'2.csv',index=False)