import src.include.visualization as visualization
from src.include.generate_arch import create_json 
from src.mappingGRN import mappingGRN as mapping
from src.include.save_script import GRN_paths
import networkx as nx
import pandas as pd
import pathlib
import glob

## DataFrame para a machine learning
## What is needed 
## 1. GRN name
## 2. edge id
## 3. worst case
## 4. 
## https://excalidraw.com/#json=XcITaIsJC96KvMA_g7Ug8,2UKreSYssA1QnFkYsTgHnA


COLUMNS = ['']

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


        print(f'Processing {grn_name} with a {arch_type}')
        
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

        x_sorted = dict(sorted(x.items()))
        list_of_used_tests = [x for key in x_sorted.keys()] # OLHAR SE FUNCIONA
        list_of_used_tests = list_of_used_tests[:9]


        # Getting txt that have the best result for wesSA
        # aux_grn_name is the GRN name (using _ as space)
        # d is the id of the test [0...1000]
        mapping_list = []
        for d in list_of_used_tests:
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



        #### FAZER MAGICA ####
        source = []

        aux_df = pd.DataFrame(columns=COLUMNS, data = source)
        global_df.append(aux_df,ignore_index=True)

    return global_df


    




