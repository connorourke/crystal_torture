"""Node class for representing sites in crystal structures."""


class Node:
    """Node class representing a site in a crystal structure."""

    def __init__(
        self, 
        index: int, 
        element: str, 
        labels: dict[str | int, str | bool], 
        neighbours_ind: set[int], 
        neighbours: set['Node'] | None = None
    ) -> None:
        """Initialise a Node.

        Args:
            index: Node index.
            element: Element on node.
            labels: Dictionary of labels associated to the node.
            neighbours_ind: Set of neighbour indices for the node in unit cell.
            neighbours: Set of neighbour Nodes for the node in unit cell.
        """
        self.index = index
        self.element = element
        self.labels = labels
        self.neighbours_ind = neighbours_ind
        self.neighbours = neighbours
        self.tortuosity: float | None = None
        self.dist: int = 0