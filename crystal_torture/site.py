

class Site:
    """
    Site class
    """

    def __init__(self, index, element, labels):
        """
        Initialise a site.

        Args:
            index (Int): site index
            element (Str): element on site
            label(Dict(Int:Str)): dictionary of labels associated to the site. 
        """    
        self.index = index
        self.element = element
        self.labels = labels

    
