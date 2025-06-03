"""Node class for representing sites in crystal structures."""
import warnings


class Node:
    """A node representing an atomic site in a crystal structure for percolation analysis.
    
    Each Node represents one atomic site from the input crystal structure. To properly
    handle periodic boundary conditions, the analysis uses a 3×3×3 supercell containing
    the original unit cell surrounded by 26 periodic images. This creates nodes for
    both the original sites and their periodic copies.
    
    Every Node has a unique index in the supercell. Multiple nodes share the same
    uc_index because they represent the same original unit cell site in different
    locations. The is_halo flag distinguishes between sites in the central unit cell
    (is_halo=False) and their periodic images (is_halo=True). Only unit cell sites
    are used to seed cluster formation during the percolation analysis.
    
    Nodes are connected to other nodes within a cutoff distance, forming the graph
    used for percolation analysis. The tortuosity value represents the minimum number
    of edges traversed for a unit cell node to reach one of its periodic images.
    
    Attributes:
        index: Unique node identifier in the supercell.
        element: Chemical element symbol ('Li', 'Mg', 'O', etc.).
        uc_index: Original unit cell site index this node represents.
        is_halo: True if periodic image, False if central unit cell site.
        neighbours_ind: Set of connected node indices.
        neighbours: Set of connected Node objects.
        tortuosity: Minimum edges traversed to reach a periodic image (set by analysis).
        dist: Temporary distance for graph algorithms.
    """

    def __init__(
        self, 
        index: int, 
        element: str, 
        uc_index: int,
        is_halo: bool,
        neighbours_ind: set[int] | None = None, 
        neighbours: set['Node'] | None = None
    ) -> None:
        """Create a Node representing a site in the crystal structure.
        
        Args:
            index: Unique identifier for this node in the supercell.
            element: Chemical element symbol.
            uc_index: Index of the original unit cell site this represents.
            is_halo: True if this is a periodic image, False if unit cell site.
            neighbours_ind: Set of connected node indices.
            neighbours: Set of connected Node objects.
        """
        self.index = index
        self.element = element
        self.uc_index: int = uc_index
        self.is_halo: bool = is_halo
        self.neighbours_ind = neighbours_ind or set()
        self.neighbours = neighbours
        self.tortuosity: float | None = None
        self.dist: int = 0

    @property  
    def labels(self) -> dict:
        """Legacy labels interface for backward compatibility.
        
        Deprecated:
            The labels interface is deprecated and will be removed in v2.0. 
            Use node.uc_index and node.is_halo directly instead.
        
        Returns:
            Dictionary containing UC_index and Halo values for compatibility with legacy code.
        """
        import warnings
        warnings.warn(
            "Node.labels is deprecated and will be removed in v2.0. "
            "Use node.uc_index and node.is_halo directly instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return {
            "UC_index": str(self.uc_index),
            "Halo": self.is_halo
        }
        