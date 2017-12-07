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
        

