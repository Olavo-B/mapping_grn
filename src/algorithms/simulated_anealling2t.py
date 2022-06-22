from tqdm import tqdm
from src.mappingGRN import mappingGRN
import networkx as nx
import random as rand
import math


def __evaluate_move(mp: mappingGRN,u,v,peU,peV) -> int:
        """Returns the local cost from peU to all neighbors peW and
            the new local cost from peU (where peU is on peV) to
            to all neighbors peW. 
        """

        localC,newLocalC=0,0 
        if (mp.grn.has_node(u)==True):
            for w in mp.grn.neighbors(u):
                if w==u: continue # Calculate distance only for the neighbors of v
                peW = mp.grn_2_arc(w)
                localC += mp.get_cost(peU,peW)
                newLocalC += mp.get_cost(peV,peW)
            
            for w in mp.grn.predecessors(u):
                if w==u: continue # Calculate distance only for the neighbors of u
                peW = mp.grn_2_arc(w)
                localC += mp.get_cost(peW,peU)
                newLocalC += mp.get_cost(peW,peV)

        return localC, newLocalC


def __switching_cost(mp,u,v,peU,peV,curr_cost) -> int:
    """Return the new cost from peU to peV.
        uLocal_cost     : cost from peU to all neighbors of node u
        uNew_local_cost : cost from peV to all neighbors of node u

        vLocal_cost     : cost from peV to all neighbors of node v
        vNew_local_cost : cost from peU to all neighbors of node v
        
        local_cost      : total local cost     (uLocal_cost + vLocal_cost)
        new_local_cost  : total new local cost (uNew_local_cost + vNew_local_cost)  
    """

    # get partial local costs and new local costs
    uLocal_cost, uNew_local_cost = __evaluate_move(mp,u,v,peU,peV)
    vLocal_cost, vNew_local_cost = __evaluate_move(mp,v,u,peV,peU)

    # get total local cost and new local_cost
    local_cost      = uLocal_cost + vLocal_cost
    new_local_cost  = uNew_local_cost + vNew_local_cost 

    # new cost
    return (curr_cost - local_cost + new_local_cost)


def __fit(mp,u,v,peU,peV) -> bool:
    """ Give two GRN's nodes and two pe of the CGRA, validate if the swap between this two
        PEs is the optimal based on the in_degree of each parameter

        Parameters
        ----------
        u: Node Label
            A node in the GRN graph
        v: Node Label
            A node in the GRN graph
        peU: Node Label
            A node in the CGRA graph
        peV: Node Label
            A node in the CGRA graph

        Returns
        ----------
        True if it is a optimal swap, false otherwise.

        Notes
        ----------
        For more, access: https://excalidraw.com/#json=VpNWRIhAEcB5gAjIEA6BK,AyAnSPqGGmpOy_j6NGb6ZA
    """

    peU_in_degree = mp.cgra.in_degree(peU)
    peV_in_degree = mp.cgra.in_degree(peV)

    u_in_degree = mp.grn.in_degree(u)
    v_in_degree = mp.grn.in_degree(v)

    fit_v = False


    if peU_in_degree == peV_in_degree: return True

    if (peU_in_degree - v_in_degree >= 0 ) and (peV_in_degree - u_in_degree >= 0): return True

    return False        


def __randpes(mp: mappingGRN, inf, sup):

    # Get the GRN's edge that have the greatest distance value
    distance_list = mp.get_distance()
    ARCH = mp.get_cgra()
    if distance_list.empty():
        mp.set_distance_list()
    peA,peB = distance_list.get()[1:]

    peC = rand.choice(list(ARCH.neighbors(peA)))

    return peB,peC

def __range(max,dec,min) -> int:
    a_n = math.log10(min)
    a_1 = math.log10(max)
    q = math.log10(dec)

    n =  ((a_n -  a_1) + q) / q

    return int(n)

def simulated_annealing(mp: mappingGRN,data = False) -> None:
    """ 
        Aplies Simulated Annealing algorithm on a GRN mapped into CGRA
        - Starts with a random mapped GRN
        - Expected to end up with a lower cost mapped GRN  
        Template
        --------
        let 'T' be the temperature, 'curr_cost' the total edge cost and 'n' the arc length.
        T           <- 100
        curr_cost   <- total_edge_cost()
        while T>0.00001:
            choose random pe's:
                peU,peV <- rand( [0, n²) ), rand( [0, n²) )
            map pe's to grn nodes:
                u,v <- CGRA_2_GRN(peU), CGRA_2_GRN(peV)
            Calculate new cost:
                if u is a node from grn then:
                    evaluate_move(u,v,peU,peV)                
                if v is a node from grn then:
                    evaluate_move(v,u,peV,peU)
                new_cost <- curr_cost - local_cost + new_local_cost
            Calculate acceptance probability:
                accProb <- exp(-1 * (dC/T) )
            if new_cost < curr_cost or rand([0,...,1]) < accProb then:
                make a swap between peU and peV
            decrease temperature
    """
    # INIT
    T=100                               # Start Simulated Annealing temperature
    curr_cost=mp.total_edge_cost()      # Calculate current total edge cost
    
    # interval of pe's
    inf = 0
    sup = mp.get_arc_size()-1

    n_range = __range(T,0.999,0.00001)
    for interation in tqdm(
        range(n_range),
        position=0,
        leave = True,
        desc= f"Simulated Annealing with {mp.grn.number_of_nodes()} genes and {mp.get_arc_size()} PEs:"
    ):
        
        # Choose random Pe's
        peU, peV = __randpes(mp,inf,sup)

        # map pe's to grn nodes
        u = mp.arc_2_grn(peU)
        v = mp.arc_2_grn(peV)

        # Verify if peU and peV has grn's nodes in it
        if u == None or v == None:    continue
        
        # Calculate new cost 
        new_cost = __switching_cost(mp,u,v,peU,peV,curr_cost)

        # Calculate acceptance probability
        dC      = new_cost - curr_cost   
        try:    accProb= math.exp(-dC/T)
        except: accProb= -1

        # If it's a good swap
        # Calculate current curr_cost edge cost
        # Swap peU content with peV content
        if dC<=0 or rand.random()<accProb:
            curr_cost=mp.total_edge_cost()    
            mp.r_mapping.update({peU:v, peV:u})

        # Decrease temp 
        T *= 0.999

    mp.generate_wcase()

    if data == True:
        mp.get_all_stats()