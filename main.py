from src.include.save_script import generate_metadata
import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import src.algorithms.simulated_anealling as sm
from src.include.save_script import save_script
from src.include.save_script import get_grn_dot
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot






def main():
    grn2dot = Grn2dot('misc/grn_benchmarks-main/40-100/Differentiation of T lymphocytes/expr/expressions.ALL.txt')

    GRN = grn2dot.get_nx_digraph()

    arch_path = 'misc/arch/15x15/cgra_mesh_ho_15x15.json'

    aux = arch_path.split('/')
    aux = aux[3].split('.')
    fname = aux[0]

    mapping = mappingGRN(arch_path, GRN)



    ### TEST BENCH ###
    sm.simulated_annealing(mapping,data=True)
    list_hist = mapping.get_hist()
    # print(f"WC: {mapping.get_worstcase()}")


    visualization.get_histogram(list_hist[-1],fname,'histogram',len(list_hist))
    visualization.get_histogram(list_hist[0],fname,'histogram',0)


    ### GRN DOT ###
    # get_grn_dot("misc/grn_benchmarks-main")



    ### BENCHMARK ###
    # save_script("misc/grn_benchmarks-main","misc/arch/15x15")






if __name__ == '__main__':
    main()