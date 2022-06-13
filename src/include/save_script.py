import src.algorithms.simulated_anealling as sa
from src.mappingGRN import mappingGRN as mapping
import src.include.visualization as visualization
from src.include.generate_arch import create_json
from grn2dot.grn2dot import Grn2dot
import statistics as st
import networkx as nx
from glob import glob
import pandas as pd
import numpy as np
import pathlib
import os



def GRN_paths(path) -> list:
    ''' Return a list with all nx.Digraph object of all GRN found in path
    '''

    GRN = []
    p = pathlib.Path(path)
    paths = list(p.glob('**/expressions.ALL.txt'))


    if not paths:
        print("ERROR: Paths to GRNs do not exist")
        quit

    names = get_grn_names(paths)
    for path in paths:
        grn2dot = Grn2dot(path)
        GRN.append(grn2dot.get_nx_digraph())

    return GRN,names

def get_arch_names(ARCH: list) -> list:

    arch_names = []

    if not ARCH:
        print("ERROR: Paths to ARCHs do not exist")
        quit

    for arch in ARCH:
        aux = arch.split('/')
        aux = aux[3].split('.')
        arch_names.append(aux[0])
    
    return arch_names

def get_grn_names(GRN: list) -> list:

    grn_names = []

    for grn in GRN:
        rato = str(grn)
        aux = rato.split('/')
        grn_names.append(aux[3])

    return grn_names

def get_data(row: list, mp: mapping,  arch_name: str,grn_name: str) -> list:


    cost = mp.total_edge_cost()
    wc = mp.get_worstcase()
    list_hist = mp.get_hist()

    row.extend([wc,cost])



    # get sa_curve, dot and histogram
    visualization.sa_curve(mp.get_allcost(),arch_name,grn_name)
    visualization.get_dot(mp,arch_name,grn_name)
    visualization.get_histogram(list_hist[0],arch_name,grn_name,0)
    visualization.get_histogram(list_hist[-1],arch_name,grn_name,len(list_hist))


    return row


def generate_metadata(grn_path) -> None:

    GRN,grn_names = GRN_paths(grn_path)


    for grn,grn_name in zip(GRN,grn_names):


        values_in = []
        values_out = []

        for node in grn.nodes():
            values_in.append(grn.in_degree(node)) 
            values_out.append(grn.out_degree(node))

        max_degree_in = max(values_in)
        max_degree_out = max(values_out)

        mean_in = st.mean(values_in)
        mean_out =st.mean(values_out)

        path = f"benchmarks/{grn_name}"  
        file_name = f"{grn_name}.txt"


        isExist = os.path.exists(path)

        if not isExist:
    
            # Create a new directory because it does not exist 
            os.makedirs(path)
            print("The new directory is created!")

        completeName = os.path.join(path, file_name)

        with open(completeName, 'w') as f:
            print(            
                f"{'Number of nodes in GRN:' : <30}{grn.number_of_nodes() : >20}",
                f"\n{'Number of edges in GRN:' : <30}{grn.number_of_edges() : >20}",
                f"\n{'Average in-degree:' : <30}{mean_in : >20}",
                f"\n{'Average out-degree:' : <30}{mean_out : >20}",
                f"\n{'Max in-degree:' : <30}{max_degree_in : >20}",
                f"\n{'Max out-degree:' : <30}{max_degree_out : >20}",
                file=f)

            f.close()

def get_grn_dot(grn_path) -> None:
    GRN,grn_names = GRN_paths(grn_path)



    for graph,grn_name in zip(GRN,grn_names):


        removed_nodes = []
        for node in graph.nodes():
            if graph.degree(node) == 0:
                removed_nodes.append(node)

        graph.remove_nodes_from(removed_nodes)
        grn = graph

        dot = nx.nx_pydot.to_pydot(grn)
        dot_s = dot.to_string()
        
        path = f"benchmarks/grn_DOT"  
        file_name = f"{grn_name}.dot"





        isExist = os.path.exists(path)

        if not isExist:
    
            # Create a new directory because it does not exist 
            os.makedirs(path)
            print("The new directory is created!")

        completeName = os.path.join(path, file_name)

        with open(completeName, 'w') as f:
            f.write(dot_s)
        f.close()


def save_script(grn_path, arch_path):

    GRN,grn_names = GRN_paths(grn_path)
    ARCH = glob(arch_path + "/*.json")
    arch_names = get_arch_names(ARCH)

    rows = []

    for grn,grn_name in zip(GRN,grn_names):
        row = []
        if grn.number_of_nodes() > 225:
            row.extend(['-'] * (len(ARCH)*2))
            print(row)
            rows.append(row)
            continue
        for arch,arch_name in zip(ARCH,arch_names):
            mp = mapping(arch,grn)
            try:
                sa.simulated_annealing(mp)
                row = get_data(row,mp,
                               arch_name,
                               grn_name)
            except:
                row.extend(['-','-'])
        print(row)
        rows.append(row)


    columns = pd.MultiIndex.from_product([arch_names,['WC','Cost']])
    data = pd.DataFrame(rows,columns=columns, index=grn_names)


    try: 
        data.to_excel(f"benchmarks/data_01-06-22.xlsx")
    except:
        print(data)


def read_wesSA_file(file_path,grn_path,results_path):

    GRN,grn_names = GRN_paths(grn_path)
    p = pathlib.Path(results_path)
    results_paths = list(p.glob('**/results.txt'))


    # Getting best result one by one
    for results,name,grn in zip(results_paths,grn_names,GRN):

        aux = str(results)
        aux = aux.split('/')
        aux = aux[2]

        grn_name = aux.replace('_', ' ')
        grn_index = grn_names.index(grn_name)

        if grn_name != grn_names[grn_index]:
            print(f'ERRO\nwesSA file name: {grn_name} is different from GRN name: {grn_names[grn_index]}')
            break



        x = {}
        with open(results) as results:
            for line in results:
                data = line.split(', ')
                if data[0] == '1\n': break
                if data[0] == 'N': continue
                try:
                    (N,cost) = (data[1],data[4])
                    x[N] = cost
                except: continue 

        d = min(x, key=x.get)

        # Getting txt that have the best result for wesSA
        # aux is the GRN name (using _ as space)
        # d is the id of the test [0...1000]
        p = pathlib.Path(file_path)
        PATHS = list(p.glob('**/' + aux + '/mesh/' + d + '.txt'))

        path = PATHS[0]

        print(path)

        dict =      {}
        with open(path) as f:
            for line in f:
                (key,val) = line.split()
                if key == val: # creating arch for that dictionary
                    create_json(int(key),int(val))
                    continue
                dict[int(key)] = (" " + val + " ")


        mp = mapping('arch.json',GRN[grn_index],dict)
        mp.generate_histogram()
        hist = mp.get_hist()
        # visualization.get_dot(mp,'wesSA_mesh',grn_names[grn_index])
        visualization.get_histogram(hist[0],'wesSA_mesh',grn_names[grn_index],'B_' + d)










# def save_wesSA_data(file_path,results_path):

#     grn2dot = Grn2dot('misc/grn_benchmarks-main/40-100/Apoptosis network/expr/expressions.ALL.txt')

#     GRN = grn2dot.get_nx_digraph()
#     x = {}


#     # Getting all best results using results.txt files
#     with open(results_path) as results:
#         for line in results:
#             data = line.split(', ')
#             if data[0] == '1\n': break
#             if data[0] == 'N': continue
#             try:
#                 (N,cost) = (data[1],data[4])
#                 x[N] = cost
#             except: continue 

#     d = min(x, key=x.get)


#     p = pathlib.Path(file_path)
#     PATHS = list(p.glob('**/mesh/' + d + '.txt'))

#     for file in PATHS:
#         dict =      {}


#         with open(file) as f:
#             for line in f:
#                 (key,val) = line.split()
#                 if key == val:
#                     create_json(int(key),int(val))
#                     continue
#                 dict[int(key)] = (" " + val + " ")


#         mp = mapping('arch.json',GRN,dict)
#         mp.generate_histogram()
#         hist = mp.get_hist()
#         visualization.get_dot(mp,'wesSA_mesh','Apoptosis network')
#         visualization.get_histogram(hist[0],'wesSA_mesh','Apoptosis network','B_' + d)
        




