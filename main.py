from src.include.save_script import generate_metadata
from src.include.generate_ml_df import generate_df
from src.include.save_script import read_wesSA_file
import src.algorithms.simulated_anealling2t as sm2t
import src.include.visualization as visualization
import src.algorithms.simulated_anealling as sm
import src.algorithms.simulated_annealing_rand as smrand
from src.include.save_script import save_script
from src.mappingGRN import mappingGRN
from grn2dot.grn2dot import Grn2dot
from src.include.generate_arch import create_json
import networkx as nx
import math
import pathlib



def run_grn(id,GRN,ARCH,results):
    for id in range(id*250,(id+1*250)):
        mp = mappingGRN(ARCH,GRN)
        sm.simulated_annealing(mp)
        





def main():
    grn2dot = Grn2dot('misc/grn_benchmarks-main/40-100/Cholesterol Regulatory Pathway/expr/expressions.ALL.txt')

    GRN = grn2dot.get_nx_digraph()

    # arch_size = math.isqrt(GRN.number_of_nodes()) + 1


    results_path = pathlib.Path('misc/392.txt')
    print(results_path)

    pre_made_mapping = {}
    with open(results_path) as result:
        first_line = result.readline()
        data = first_line.split(' ')
        data[1] =   data[1][:-1]
        arch_path = create_json(int(data[0]),int(data[1]))
        lines = result.readlines()[0:]
        for line in lines:
            data = line.split('  ')
            data[1] = ' ' + data[1][:-1]
            pre_made_mapping[int(data[0])   ] = data[1]    

    aux = arch_path.split('/')
    aux = aux[3].split('.')
    fname = aux[0]

    mapping = mappingGRN(arch_path, GRN,pre_made=pre_made_mapping)



    ### TEST BENCH ###

    print(mapping.get_mapped_grn())

    # sm.simulated_annealing(mapping,data=True)
    # # smrand.simulated_annealing(mapping,data=True)
    # mapping.generate_histogram()
    # list_hist = mapping.get_hist()
    # list_routing = mapping.get__path_count()

    # print(list_routing)


    # visualization.get_histogram(list_hist[-1],fname,'histogram',len(list_hist),show_plot=True)
    # visualization.get_histogram(list_hist[0],fname,'histogram',0)
    visualization.get_dot(mapping,'9x6_mesh','histogram')


    # df = generate_df('misc/results','misc/grn_benchmarks-main','misc/results')
    # df.to_csv('misc/dataframes/df_arch.csv',index=False)





    ### BENCHMARK ###
    # save_script("misc/grn_benchmarks-main","misc/arch/15x15")
    # read_wesSA_file('/home/olavo/yolt/westSA_wscad22/results','misc/grn_benchmarks-main','/home/olavo/yolt/westSA_wscad22/results')

    



if __name__ == '__main__':
    main()