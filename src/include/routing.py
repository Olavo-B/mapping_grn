from src.mappingGRN import mappingGRN
from heapq import heappop, heappush
from itertools import count
import networkx


'''
add edges attributes
    used_when
    used_by
'''


class dijkstra_routing:


    def weight(v,u,data,step):
        '''Function that returns edges weight and if it can be used as path at step time

        Parameters
        ----------
        v,u : non-empty nodes of a NetworkX graph
            Two nodes that compose a edge in the graph
            v as source and u as target for nx.Digraph

        data : a dict with all attributes of the edge (v,u)

        step : a integer that represent the current step of the path

        Returns
        -------
        None : if data['used_when'] == step
        weight : integer
            data['weight']
        '''

        if data['used_when'] == step:
            return None
        else:
            return data['weight']

    def dijkstra_multisource(
        G, sources, weight, pred=None, paths=None, cutoff=None, target=None
    ):
        """Uses Dijkstra's algorithm to find shortest weighted paths

        Parameters
        ----------
        G : NetworkX graph

        sources : non-empty iterable of nodes
            Starting nodes for paths. If this is just an iterable containing
            a single node, then all paths computed by this function will
            start from that node. If there are two or more nodes in this
            iterable, the computed paths may begin from any one of the start
            nodes.

        weight: function
            Function with (u, v, data) input that returns that edges weight

        pred: dict of lists, optional(default=None)
            dict to store a list of predecessors keyed by that node
            If None, predecessors are not stored.

        paths: dict, optional (default=None)
            dict to store the path list from source to each node, keyed by node.
            If None, paths are not stored.

        target : node label, optional
            Ending node for path. Search is halted when target is found.

        cutoff : integer or float, optional
            Length (sum of edge weights) at which the search is stopped.
            If cutoff is provided, only return paths with summed weight <= cutoff.

        Returns
        -------
        distance : dictionary
            A mapping from node to shortest distance to that node from one
            of the source nodes.

        Raises
        ------
        NodeNotFound
            If any of `sources` is not in `G`.

        Notes
        -----
        The optional predecessor and path dictionaries can be accessed by
        the caller through the original pred and paths objects passed
        as arguments. No need to explicitly return pred or paths.



        This method was altered my students aiming count the momentum of each step
        create the shorted path, this as made due the necessity of simulated a parallel
        routing. With this count was possible make a validation on the weight function.

        """
        G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

        push = heappush
        pop = heappop
        dist = {}  # dictionary of final distances
        seen = {}
        # fringe is heapq with 3-tuples (distance,c,node)
        # use the count c to avoid comparing nodes (may not be able to)
        c = count()
        fringe = []
        for source in sources:
            seen[source] = 0
            push(fringe, (0, next(c), source))
        while fringe:
            (d, c, v) = pop(fringe)
            if v in dist:
                continue  # already searched this node.
            dist[v] = d
            if v == target: # arrived in target node
                break
            for u, e in G_succ[v].items(): # for each neighbor and data weight of v
                # in function weight was validate if the current step is
                # not equal to the attribute 'used_when' of the edge (v,u)
                cost = weight(v, u, e, c)
                if cost is None: # if the step is equal to 'used_when'
                    continue
                vu_dist = dist[v] + cost
                if cutoff is not None:
                    if vu_dist > cutoff:
                        continue
                if u in dist:
                    u_dist = dist[u]
                    if vu_dist < u_dist:
                        raise ValueError("Contradictory paths found:", "negative weights?")
                    elif pred is not None and vu_dist == u_dist:
                        pred[u].append(v)
                elif u not in seen or vu_dist < seen[u]:
                    # here the path was validate, and two attributes
                    # was set in edge (v,u): used_by = source and
                    #                        used_when = step
                    G_succ[v][u]['used_by'].append(source)
                    G_succ[v][u]['used_when'] = c
                    seen[u] = vu_dist
                    push(fringe, (vu_dist, next(c), u))
                    if paths is not None:
                        paths[u] = paths[v] + [u]
                    if pred is not None:
                        pred[u] = [v]
                elif vu_dist == seen[u]:
                    if pred is not None:
                        pred[u].append(v)

        # The optional predecessor and path dictionaries can be accessed
        # by the caller via the pred and paths objects passed as arguments.
        return dist
