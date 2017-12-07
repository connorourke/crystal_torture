

class Node:
    """
    Node class
    """

    def __init__(self, index, element, labels, neighbours):
        """
        Initialise a Node.

        Args:
            index (Int): node index
            element (Str): element on node
            label(Dict(Int:Str)): dictionary of labels associated to the node. 
        """    
        self.index = index
        self.element = element
        self.labels = labels
        self.neighbours = neighbours


    
