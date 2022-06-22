from src.algorithms.simulated_anealling import simulated_annealing
from src.include.save_script import generate_metadata
from src.include.save_script import read_wesSA_file
from src.include.generate_arch import create_json
from src.include.save_script import save_script
from src.algorithms.interlace import interlace
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot

import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import math

import networkx as nx

#########
    # EXEMPLE
    # nodes = ['a','b','c','d','e','f','g','h']
    # edges = [('g','c'),('h','c'),('a','c'),('c','d'),
    #         ('a','b'),('d','b'),('b','d'),('e','d'),
    #         ('e','b'),('e','f'),('f','b')]
    # GRN = nx.DiGraph()
    # GRN.add_nodes_from(nodes)
    # GRN.add_edges_from(edges)
#########

def best_interlace(mp:mappingGRN):
    # UPDATE BEST INTERLACE #
    interlace(mp)
    wc = mp.get_worstcase()
    ans = {}

    for i in range(1000):
        interlace(mp)
        cur_wc = mp.get_worstcase()
        if cur_wc < wc:
            wc = cur_wc
            ans = mp.get_mapped_grn()
            print(f"interlace: update worst case to {wc}.")
            f = open('misc/best_interlace2.txt','w')
            f.write(str(wc))
            f.write("\n"+str(ans))
            f.close()

def best_sa(mp:mappingGRN):
    simulated_annealing(mp)
    wc = mp.get_worstcase()
    ans = {}
    for i in range(1000):
        simulated_annealing(mp)
        cur_wc = mp.get_worstcase()
        if cur_wc < wc:
            wc = cur_wc
            ans = mp.get_mapped_grn()
            print(f"SA: update worst case to {wc}.")
            f = open('misc/best_annealing2.txt','w')
            f.write(str(wc))
            f.write("\n"+str(ans))
            f.close()

def main():
    
    # INIT #
    grn2dot = Grn2dot('misc/Benchmark_53.txt')
    GRN = grn2dot.get_nx_digraph()
    N = GRN.number_of_nodes()
    n = 1 + math.isqrt(N)
    create_json(n,n)

    mapping = mappingGRN('arch.json', GRN)
    
    interlace(mapping)
    #simulated_annealing(mapping)

    #best_sa(mapping)
    #best_interlace(mapping)

    # visualization.get_dot(mapping,'interlace_ex','ex')
    # mapping.generate_histogram()
    # h = mapping.get_hist()
    # visualization.get_histogram(h[0],'interlace_ex','ex',0)

if __name__ == '__main__':
    main()