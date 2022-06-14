from src.include.save_script import generate_metadata
from src.include.save_script import read_wesSA_file
from src.include.generate_arch import create_json
from src.include.save_script import save_script
from src.algorithms.interlace import interlace
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot

import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import src.algorithms.simulated_anealling as sm
import math





def main():
    
    # INIT #
    grn2dot = Grn2dot('misc/Benchmark_53.txt')
    GRN = grn2dot.get_nx_digraph()
    N = GRN.number_of_nodes()
    n = 1 + math.isqrt(N)
    create_json(n,n)
    mapping = mappingGRN('arch.json', GRN)

    # INTERLACE #
    interlace(mapping)
    
    # UPDATE BEST INTERLACE #
    wc = mapping.get_worstcase()
    ans = {}

    while True:
        interlace(mapping)
        curr_wc = mapping.get_worstcase()
        if curr_wc < wc:
            wc = curr_wc
            ans = mapping.get_mapped_grn()
            print(f"update worst case to {wc}.")
            f = open('misc/best_interlace.txt','w')
            f.write(str(wc))
            f.write("\n"+str(ans))
            f.close()

    # visualization.get_dot(mapping,'interlace_ex','ex')
    # mapping.generate_histogram()
    # h = mapping.get_hist()
    # visualization.get_histogram(h[0],'interlace_ex','ex',0)


if __name__ == '__main__':
    main()