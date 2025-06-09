"""Minimal cluster objects for returning tortuosity data from graph analysis."""

from typing import Optional


class minimal_Cluster:
    """Minimal cluster object for returning tortuosity data from graph."""

    def __init__(self,
        site_indices: list[int],
        size: int) -> None:
        """Initialise a minimal cluster.

        Args:
            site_indices: List of site indices in the cluster.
            size: Number of sites in the cluster.
        """
        self.site_indices = site_indices
        self.periodic: int | None = None
        self.tortuosity: float | None = None
        self.size = size