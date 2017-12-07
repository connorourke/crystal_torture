from crystal_torture.node import  Node


class Cluster:
    """
    Cluster class: group of connected nodes within graph
    """

    def __init__(self,nodes):
        """
        Initialise a cluster.

        Args:
            nodes (list(Node)): list of nodes in the cluster.
        """

        self.nodes = nodes
        
    def merge(self, other_cluster):
        """
        Merge to clusters into one
 
        Args:
            other_cluster (Cluster): cluster to be joined
        """

        new_cluster = Cluster( self.nodes + other_cluster.nodes )

        return new_cluster



 
