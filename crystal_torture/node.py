"""Node class for representing sites in crystal structures."""
import warnings
from typing import Union


class Node:
    """Node class representing a site in a crystal structure."""

    def __init__(
        self, 
        index: int, 
        element: str, 
        labels: dict[str | int, str | bool] | None = None,
        neighbours_ind: set[int] | None = None, 
        neighbours: set['Node'] | None = None,
        # New optional parameters  
        uc_index: int | None = None,
        is_halo: bool | None = None
    ) -> None:
        self.index = index
        self.element = element
        self.neighbours_ind = neighbours_ind or set()
        self.neighbours = neighbours
        self.tortuosity: float | None = None
        self.dist: int = 0
        
        # Fix type annotations to allow None
        self.uc_index: int | None
        self.is_halo: bool | None
        
        # Set uc_index and is_halo (prefer new params, fall back to labels, then None)
        if uc_index is not None:
            self.uc_index = uc_index
        elif labels and "UC_index" in labels:
            self.uc_index = int(labels["UC_index"])
        else:
            self.uc_index = None
            
        if is_halo is not None:
            self.is_halo = is_halo
        elif labels and "Halo" in labels:
            self.is_halo = bool(labels["Halo"])  # Explicit cast to bool
        else:
            self.is_halo = None
        
        # Keep original labels for backward compatibility
        self._original_labels = labels

    @property  
    def labels(self) -> dict:
        """Legacy labels interface (deprecated)."""
        result = dict(self._original_labels or {})
        if self.uc_index is not None:
            result["UC_index"] = str(self.uc_index)
        if self.is_halo is not None:
            result["Halo"] = self.is_halo
        return result
        