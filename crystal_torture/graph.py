from crystal_torture.node import  Node


class Graph:
    """
    Graph class
    """

    def __init__(self,nodes):
        """
        Initialise a graph.

        Args:
            nodes (list(Node)): list of nodes in the graph.
        """

        self.nodes = nodes
        
