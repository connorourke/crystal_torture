from crystal_torture.cluster import  Cluster

class Graph:
    """
    Graph class: group of disconnected clusters making up full graph
    """

    def __init__(self, nodes):
        """
        Initialise a graph.

        Args:
            nodes  (set(Nodes)): set of unit-cell nodes in graph.
            halo   (set(Nodes)): set of halo image nodes in graph.

        """

        
        self.nodes = nodes
#        self.halo = halo
        self.clusters = None
#        self.halo_clusters = None
        

    def obtain_clusters(self):
        """
        Search through the nodes in the graph and return the set of connected clusters

        """



#        cluster_to_grow  = Cluster(self.nodes.pop(0))
#        clusters = set()
        
#        while 
            
        

