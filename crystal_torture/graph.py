from crystal_torture.cluster import  Cluster

class Graph:
    """
    Graph class: group of disconnected clusters making up full graph
    """

    def __init__(self,clusters):
        """
        Initialise a graph.

        Args:
            nodes (set(Cluster)): set of clusters in the graph.
        """

        self.clusters = clusters

