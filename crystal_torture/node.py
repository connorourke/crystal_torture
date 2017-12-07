

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
            labels(Dict(Int:Str)): dictionary of labels associated to the node.
            neighbours(list[int]): list of neighbours of the node  
        """    
        self.index = index
        self.element = element
        self.labels = labels
        self.neighbours = neighbours


    
