from grn2dot.grn2dot import Grn2dot
import src.include.visualization as visualization
from src.mappingGRN import mappingGRN
import src.algorithms.simulated_anealling as sm
from src.include.save_script import save_script






def main():
    grn2dot = Grn2dot('misc/Benchmark_48.txt')

    GRN = grn2dot.get_nx_digraph()

    arch_path = 'misc/arch/15x15/cgra_mesh_ho_15x15.json'

    aux = arch_path.split('/')
    aux = aux[1].split('.')
    fname = aux[0]



    mapping = mappingGRN(arch_path, GRN)
    # sm.simulated_annealing(mapping)



    # ### CGRA VISUALIZATION ###
    # visualization.get_dot(mapping,fname,'ex',False)


    # ### GRAPH TOTAL_COST X N_SWAPS ###
    # visualization.sa_curve(mapping.get_allcost(),fname,'ex')

    # # ### HISTOGRAM OF N TIMES A PE WAS USED ###
    # # # visualGraph.num_pes_used(10,mapping,GRN)

    # # print(mapping.get_num_swaps())


    # ### BENCHMARK ###
    save_script("misc\\grn_benchmarks-main","misc\\arch\\15x15")





if __name__ == '__main__':
    main()