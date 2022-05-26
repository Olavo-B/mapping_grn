import src.algorithms.simulated_anealling as sa
from src.mappingGRN import mappingGRN as mapping
import src.include.visualization as visualization
from grn2dot.grn2dot import Grn2dot
from glob import glob
import numpy as np
import pandas as pd
import pathlib



def GRN_paths(path) -> list:
    ''' Return a list with all nx.Digraph object of all GRN found in path
    '''

    GRN = []
    p = pathlib.Path(path)
    paths = list(p.glob('**/expressions.ALL.txt'))
    names = get_grn_names(paths)
    for path in paths:
        grn2dot = Grn2dot(path)
        GRN.append(grn2dot.get_nx_digraph())

    return GRN,names

def get_arch_names(ARCH: list) -> list:

    arch_names = []

    for arch in ARCH:
        aux = arch.split('\\')
        aux = aux[3].split('.')
        arch_names.append(aux[0])
    
    return arch_names

def get_grn_names(GRN: list) -> list:

    grn_names = []

    for grn in GRN:
        rato = str(grn)
        aux = rato.split('\\')
        grn_names.append(aux[3])

    return grn_names

def get_data(row: list, mp: mapping,  arch_name: str,grn_name: str) -> list:


    cost = mp.total_edge_cost()
    wc = mp.get_worstcase()

    row.extend([wc,cost])


    # get sa_curve and dot
    visualization.sa_curve(mp.get_allcost(),arch_name,grn_name)
    visualization.get_dot(mp,arch_name,grn_name)



    return row


def write_file(data: pd.DataFrame()) -> None:
    ''' Write a xls file with all data
    '''

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
        data.to_excel(f"benchmarks\\ex.xlsx")
    except:
        print(data)
        




