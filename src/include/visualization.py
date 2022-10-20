from dis import dis
import os
from pkg_resources import get_distribution
import pydot
import pandas as pd
import networkx as nx
import random as rand 
from colour import Color
import matplotlib.pyplot as plt
from src.mappingGRN import mappingGRN
import src.algorithms.simulated_anealling as sa




def get_histogram(data:dict,arch_name:str,grn_name:str,i, show_plot = False) -> None:


    source =  pd.DataFrame.from_dict(data,orient='index',columns=['num_cases'])


    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.bar(list(source.index.values),list(source['num_cases']))
    ax.set_title('Number of connections by distance')
    ax.set_xlabel('Distance')
    ax.set_ylabel('Num of connections')


    path = f"benchmarks/{grn_name}/histogram"  
    file_name = f"{arch_name}_{i}.svg"

    isExist = os.path.exists(path)

    if not isExist:
  
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

    completeName = os.path.join(path, file_name)


    plt.savefig(completeName,dpi=150)
    if show_plot: plt.show()



def sa_curve(data:list,arch_name:str,grn_name:str, show_plot = False) -> None:
    df = pd.DataFrame(data)
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df[1], df[0], color='tab:blue')
    ax.set_title('Simulated Anealling Cost')
    ax.set_xlabel('num swaps')
    ax.set_ylabel('total cost')


    path = f"benchmarks/{grn_name}/sa_curve"  
    file_name = f"{arch_name}.svg"

    isExist = os.path.exists(path)

    if not isExist:
  
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

    completeName = os.path.join(path, file_name)


    plt.savefig(completeName,dpi=150)
    if show_plot: plt.show()



def build_dot(graph: pydot.Dot, nodes: list, dim: list, arch_name: str,grn_name: str) -> None:

    '''
        dim = row x col -> dim[0] = row din[1] = col

        nodes[i + dim[1] * j]

        nodes[j + dim[1] * i]
    '''

    graph.create_attribute_methods('rankdir')
    graph.create_attribute_methods('splines')

    graph.set_rankdir("TB")
    graph.set_splines("ortho")

    graph_string = graph.to_string()
    graph_string = graph_string.replace("strict digraph  {", "digraph layout  {")


    # colunas
    graph_string = graph_string.replace("}","edge [constraint=true, style=invis];\n")

    for i in range(dim[0]):
        for j in range(dim[1]):
            if (j + 1) % dim[1] == 0:
                graph_string = graph_string + "%d;\n" % (nodes[i + dim[1] * j])
            else:
                graph_string = graph_string + "{} -> ".format(nodes[i + dim[1] * j])

    # linhas
    for i in range(dim[0]):
        graph_string = graph_string + "rank = same {"
        for j in range(dim[1]):
            if (j + 1) % dim[1] == 0:
                graph_string = graph_string + "%d};\n" % (nodes[j + dim[1] * i])
            else:
                graph_string = graph_string + "{} -> ".format(nodes[j + dim[1] * i])

    graph_string = graph_string + "}"

    path = f"benchmarks/{grn_name}/DOT"  
    file_name = f"{arch_name}.dot"


    isExist = os.path.exists(path)

    if not isExist:
  
        # Create a new directory because it does not exist 
        os.makedirs(path)
        print("The new directory is created!")

    completeName = os.path.join(path, file_name)

    with open(completeName, 'w') as f:
        f.write(graph_string)
    f.close()


def to_pydot(N):
    """Returns a pydot graph from a NetworkX graph N.

    Parameters
    ----------
    N : NetworkX graph
      A graph created with NetworkX

    Examples
    --------
    >>> K5 = nx.complete_graph(5)
    >>> P = nx.nx_pydot.to_pydot(K5)

    Notes
    -----
    This function is derived from NetworkX method (see more on: https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pydot.to_pydot.html)

    """
    import pydot

    # set Graphviz graph type
    if N.is_directed():
        graph_type = "digraph"
    else:
        graph_type = "graph"
    strict = nx.number_of_selfloops(N) == 0 and not N.is_multigraph()

    name = N.name
    graph_defaults = N.graph.get("graph", {})
    if name == "":
        P = pydot.Dot("", graph_type=graph_type, strict=strict, **graph_defaults)
    else:
        P = pydot.Dot(
            f'"{name}"', graph_type=graph_type, strict=strict, **graph_defaults
        )
    try:
        P.set_node_defaults(style = 'filled',
                            fixedsize = 'false',
                            width = '0.6')
    except KeyError:
        pass
    try:
        P.set_edge_defaults(constraint = 'false')
    except KeyError:
        pass

    for n, nodedata in N.nodes(data=True):
        str_nodedata = {k: str(v) for k, v in nodedata.items()}
        p = pydot.Node(str(n), **str_nodedata)
        P.add_node(p)

    if N.is_multigraph():
        for u, v, key, edgedata in N.edges(data=True, keys=True):
            str_edgedata = {k: str(v) for k, v in edgedata.items() if k != "key"}
            edge = pydot.Edge(str(u), str(v), key=str(key), **str_edgedata)
            P.add_edge(edge)

    else:
        for u, v, edgedata in N.edges(data=True):
            str_edgedata = {k: str(v) for k, v in edgedata.items()}
            edge = pydot.Edge(str(u), str(v), **str_edgedata)
            P.add_edge(edge)
    return P


def graph_visu(mp: mappingGRN, pre_made_sa = True) -> nx.DiGraph:
        """ Graph visualization with .dot 

            1. Rodar o simulated annealing
            2. pegar todas as conexões da grn e rodar elas no crga
            2.1. para cada gene -> key referente no dict (source e target)
            2.2. rodar dijkstra_path


            Notes
            ---------
            Ainda a fazer;
            1. rodar dijkstra_path e salvar cada custo não repetido em um dict sendo:
                key = custo e valule = cor

                color[distance] -> #FF0000

        """
        if not pre_made_sa: sa.simulated_annealing(mp)

        GRN = mp.get_grn()
        CGRA = mp.get_cgra()

        # list of lists where each one is a path in the GRN on CGRA
        paths = []
        colors = {}
        

        # dict that count 0. how many times an PE is source
        #                 1. how many times an PE is target
        #                 2. how many times an PE is pasage for each PE
        # dict[PE] = [0,1,2]
        pe_stats = {pe : [0,0,0] for pe in range(mp.get_arc_size())}
                
        for node in GRN.nodes():
            pe_source = mp.grn_2_arc(node)
            pe_stats[pe_source][0] += 1
            for neighbor in GRN.neighbors(node):
                pe_target = mp.grn_2_arc(neighbor)
                pe_stats[pe_target][1] += 1
                distance,path = nx.single_source_dijkstra(CGRA,pe_source,pe_target)
                if distance <= mp.get_worstcase() * 0.5: continue
                if distance not in colors.keys():
                    while True:
                        color = ["#"+''.join([rand.choice('ABCDEF0123456789') for i in range(6)])]
                        if color not in colors.values(): break
                    colors[distance] = color
                paths.append([path,distance])
            nx.set_node_attributes(CGRA,{pe_source: {'fillcolor':'#666666'}}) #fill color for PEs with a gene in
            

        # add edge attributes:
        #                     a) colors by path's distance
        #                     b) tooltip showing path's source and target: pe_name(gene_name) to pe_name(gene_name) 
        for path,distance in paths:
            for path_node,i in zip(path,range(len(path))):
                if path_node == path[-1]: break
                if i > 0: pe_stats[path_node][2] += 1
                CGRA[path_node][path[i+1]]['color'] = colors[distance][0]
                CGRA[path_node][path[i+1]]['tooltip'] = "{}({}) to {}({})".format(path[0],
                                                                                        mp.arc_2_grn(path[0]),
                                                                                        path[-1],
                                                                                        mp.arc_2_grn(path[-1]))

        # add node attributes:
        #                     a) fillcolor of PEs used as bridge
        #                     b) label showing PEs stats: in degree, out degree, bridge count
        #                     c) tooltip showing gene's name in PE
        for pe in CGRA.nodes():
            grn_node = mp.arc_2_grn(pe)
            if (pe_stats[pe][0] == 0 and pe_stats[pe][1] == 0 and pe_stats[pe][2] != 0):
                nx.set_node_attributes(CGRA,{pe: {'fillcolor':'#bdbdbd'}}) #fill color for PEs used as bridge
            nx.set_node_attributes(CGRA, {pe: {'label':pe_stats[pe][2]}})
            nx.set_node_attributes(CGRA,{pe: {'tooltip':f"name: {grn_node},\nin_degree: {CGRA.in_degree(pe)},\nout_degree: {CGRA.out_degree(pe)}" }})


        bridge_dict = {}
        for k, v in pe_stats.items():
            bridge_dict[k] = (v[0] + v[1] + v[2])

        bridge_dict = {k: v for k, v in sorted(bridge_dict.items(), key=lambda item: item[1])}
        values = list(bridge_dict.values())
        max = values[-1]

        for pe in bridge_dict.keys():
            if bridge_dict[pe] == max : 
                nx.set_node_attributes(CGRA,{pe: {'shape': 'Msquare'}})



    
        return mp.get_cgra()
 

def graph_visu_all_dist(mp: mappingGRN, pre_made_sa = True) -> nx.DiGraph:



    CGRA = mp.get_cgra()
    x,y = mp.get_dimension()
    pos_x = x//2
    pos_y = y//2

    pe_pos = x * pos_x + pos_y - 1

    dist = nx.bellman_ford_predecessor_and_distance(CGRA, pe_pos)[1]

    max_dsit = max(dist.values())

    red = Color("white")
    colors = list(red.range_to(Color("red"),max_dsit+1))


    # add node attributes:
    #                     a) fillcolor of PEs used as bridge
    #                     b) label showing PEs stats: in degree, out degree, bridge count
    #                     c) tooltip showing gene's name in PE
    for pe in CGRA.nodes():
        nx.set_node_attributes(CGRA, {pe: {'label': dist[pe]}})
        if(pe == pe_pos): nx.set_node_attributes(CGRA, {pe: {'fillcolor': '#ffffff'}})
        nx.set_node_attributes(CGRA, {pe: {'fillcolor': str(colors[dist[pe]])}})


    return mp.get_cgra()





def arch_struct(graph: nx.DiGraph):
    return to_pydot(graph) , list(graph.nodes())


def get_dot(mp: mappingGRN,  arch_name: str,grn_name: str, pre_made_sa = True) -> None:
    arch = graph_visu_all_dist(mp,pre_made_sa)
    dot,nodes = arch_struct(arch)
    build_dot(dot,nodes,mp.get_dimension(),arch_name, grn_name)