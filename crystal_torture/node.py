

class Node:
    """
    Node class
    """

    def __init__(self, index, element, labels, neighbours_ind, neighbours = None):
        """
        Initialise a Node.

        Args:
            index (Int): node index
            element (Str): element on node
            labels(Dict(Int:Str)): dictionary of labels associated to the node.
            neighbours_ind(set{int}): set of neighbours indices for the node  
        """    
        self.index = index
        self.element = element
        self.labels = labels
        self.neighbours_ind = neighbours_ind
        self.neighbours = neighbours


    
