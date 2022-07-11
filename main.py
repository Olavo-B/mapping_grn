from sys import maxsize
from src.include.save_script import generate_metadata
from src.include.save_script import read_wesSA_file
import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import src.algorithms.simulated_anealling as sm
from src.include.save_script import save_script
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot
from src.include.generate_arch import create_json
from src.include.generate_ml_df import generate_df

from src.algorithms.double_crossing import DoubleCrossing
import src.include.json2graph as json2graph
import json
import networkx as nx
import src.algorithms.interlace_strats.edge_strategy as es
import src.algorithms.interlace_strats.search_strategy as ss

def main():
    grn2dot = Grn2dot('misc/Benchmark_53.txt')

    grn = GRN = grn2dot.get_nx_digraph()

    arch_path = create_json(8,8,'mesh')

    aux = arch_path.split('/')
    aux = aux[3].split('.')
    fname = aux[0]

    # mapping = mappingGRN(arch_path, GRN)

    ### TEST BENCH ###

    # sm.simulated_annealing(mapping,data=True)
    # mapping_rework = mappingGRN(arch_path,GRN,mapping.get_mapped_grn())
    # sm.simulated_annealing(mapping_rework,data=True)
    # list_hist = mapping.get_hist()
    # visualization.get_histogram(list_hist[-1],fname,'histogram',len(list_hist))
    # visualization.get_histogram(list_hist[0],fname,'histogram',0)
    # visualization.get_dot(mapping,'8x8_chess','histogram')

    ### BENCHMARK ###
    # save_script("misc/grn_benchmarks-main","misc/arch/15x15")
    #read_wesSA_file('misc/results','misc/grn_benchmarks-main','misc/results')

    #generate_df('misc/results','misc/grn_benchmarks-main','misc/results')


    ## DUPLA TRAVESSIA ## 
    f           = open(arch_path)
    f_json      = json.load(f)
    try: dim    = f_json['dimension']
    except: dim = [None,None]
    cgra        = json2graph.make_digraph(f_json)

    # Convertendo GRN para grafo com labels de 0 a n
    label=dict()
    nodes=list()
    edges=list()
    key=0

    graph = nx.DiGraph()

    for node in grn.nodes:
        if grn.degree(node)==0:
            continue
        label[node]=key
        key+=1
        nodes.append(label[node])
    
    for edge in grn.edges:
        edges.append((label[edge[0]], label[edge[1]]))

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    min_wc=maxsize
    dcross = DoubleCrossing(grn=graph, arch=cgra, dim=dim)
    dcross.set_edge_strat(es.DecisionTreeMesh(graph,cgra))
    for i in range(10000):
        if i%10==0:
            print(f"it:{i} - wc:{min_wc}")
        if min_wc==1: break
        #dcross.debug() 
        map = dcross.traverse()
        wc = dcross.worst_case()
        #print(f"map: {map}\nwc: {wc}")
        min_wc=min(wc,min_wc)

    print(min_wc)
    print(map)
    
if __name__ == '__main__':
    main()