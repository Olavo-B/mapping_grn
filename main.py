from src.include.save_script import generate_metadata
from src.include.save_script import read_wesSA_file
import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import src.algorithms.simulated_anealling as sm
from src.include.save_script import save_script
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot
from src.include.generate_arch import create_json






def main():
    # grn2dot = Grn2dot('misc/Benchmark_53.txt')

    # GRN = grn2dot.get_nx_digraph()

    # arch_path = create_json(8,8,'chess')

    # aux = arch_path.split('/')
    # aux = aux[3].split('.')
    # fname = aux[0]

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
    read_wesSA_file('misc/results','misc/grn_benchmarks-main','misc/results')






if __name__ == '__main__':
    main()