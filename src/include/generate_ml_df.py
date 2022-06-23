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
ARCH_COLS = ['name', 'arch. type', 'worst', 'median', 'mean']
GRN_COLS  = ['name', 'in degree', 'eigenvector', 'closeness', 'betweenness'] # ADD PAGE RANK!

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

# CREATE ARCH DATAFRAME
def DF_ARCH(res):

    print("\n== DataFrame ARCH ==")

    df = pd.DataFrame(columns=ARCH_COLS)
    worst = mean = median = case = 0
    distances = []

    # Foreach best result
    for row in res:
        
        name, type, grn, mp = get_line(row)

        # Calculate the current worst case
        worst = max(worst, mp.get_worstcase())

        # get weigth of the edges
        for edge in grn.edges:
            e0 = mp.grn_2_arc(edge[0])
            e1 = mp.grn_2_arc(edge[1])
            dist = mp.get_cost(e0, e1)
            distances.append(dist)
        
        # Append new row to the dataframe
        if case%BEST==0: 
            print(f"Processed {name} {type}.")
            mean   = stat.mean(distances)
            median = stat.median(distances)

            data = [name, type, worst, median, mean]
            
            new_df = pd.DataFrame( columns=ARCH_COLS, data=[data] )
            df     = pd.concat([df, new_df])
            
            worst = mean = median = 0
            distances=[]
        case+=1

    return df

# CREATE GRN DATAFRAME
def DF_GRN(GRNs, grn_name):

    print("\n== DataFrame GRN ==")

    df = pd.DataFrame(columns=GRN_COLS)
    k  = 0

    # foreach grn calculate the mean of the centrality prop.
    # in degree, eigenvector, closeness and betweenness
    for grn in GRNs:
        
        print(f"Processing {grn_name[k]}.")

        in_degree=[]
        eigenvector=[]
        closeness=[]
        betweenness=[]

        # Create dict node->prop.
        in_degree_dic   = nx.in_degree_centrality(grn)    
        eigenvector_dic = nx.centrality.eigenvector_centrality_numpy(grn)
        closeness_dic   = nx.closeness_centrality(grn)
        betweenness_dic = nx.betweenness_centrality(grn)

        # Create a list with the prop. values
        for node in grn.nodes:
            in_degree.append( in_degree_dic[node] )
            eigenvector.append( eigenvector_dic[node] )
            closeness.append( closeness_dic[node] )
            betweenness.append( betweenness_dic[node] )
        
        # Calculate the mean of those values
        mean_in_degree   = stat.mean(in_degree)
        mean_eigenvector = stat.mean(eigenvector)
        mean_closeness   = stat.mean(closeness)
        mean_betweenness = stat.mean(betweenness)

        # Append new row to the dataframe
        data = [grn_name[k], mean_in_degree, mean_eigenvector, mean_closeness, mean_betweenness]
        k+=1

        new_df = pd.DataFrame(data=[data], columns=GRN_COLS)
        df     = pd.concat([df, new_df])

    return df

def generate_df(file_path,grn_path,results_path):

    print("Working on results...")

    GRN,grn_names = GRN_paths(grn_path)
    p = pathlib.Path(results_path)
    results_paths = list(p.glob('**/results*.txt'))
    top_res = []

    # Getting best result one by one
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

        # Select the top results
        x_sorted = dict(sorted(x.items(), key=lambda item: item[1]))
        top_case = list(x_sorted.keys())[:BEST-1]
    
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

            # Append Best Results
            top_res.append( [grn_name, arch_type, GRN[grn_index], mp] )

    # Create DataFrames
    df_arch = DF_ARCH(top_res)
    df_grn  = DF_GRN(GRN, grn_names)

    # create a .csv file
    df_arch.to_csv('misc/dataframes/df_arch.csv',index=False)
    df_grn.to_csv('misc/dataframes/df_grn.csv', index=False)