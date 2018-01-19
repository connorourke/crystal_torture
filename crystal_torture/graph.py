#from crystal_torture.cluster import  Cluster
from crystal_torture.pymatgen_interface import clusters_from_file

class Graph:
    """
    Graph class: group of disconnected clusters making up full graph
    """

    def __init__(self, clusters):
        """
        Initialise a graph.

        Args:
            clusters  (set(Clusters)): set of clusters in the graph

        """
        
        self.clusters = clusters
        

         
        
        

