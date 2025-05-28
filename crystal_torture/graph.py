"""Graph class for representing groups of disconnected clusters making up full graph."""

from pymatgen.core import Structure
from crystal_torture.minimal_cluster import minimal_Cluster
from types import ModuleType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from crystal_torture.cluster import Cluster

# Module variable with proper type hint
tort: ModuleType | None

try:
    from . import tort
except ImportError:
    tort = None


class Graph:
    """Graph class: group of disconnected clusters making up full graph."""

    def __init__(self, clusters: set['Cluster'], structure: Structure | None = None) -> None:
        """Initialise a graph. 
        
        The graph is a 3x3x3 representation of the unit cell so there will be clusters 
        within it which are not necessarily unique. However only the unit cell nodes 
        within each cluster are tortured, so there is no repetition.

        Args:
            clusters: Set of clusters in the graph.
            structure: The pymatgen Structure object the graph has been formed from.
        """
        self.clusters = clusters
        self.tortuosity: dict[str, float] | None = None
        self.min_clusters: list[minimal_Cluster] | None = None
        self.structure = structure

    def set_site_tortuosity(self) -> None:
        """Set a dict containing the site by site tortuosity for sites in the graph unit cell."""
        tortuosity: dict[str, float] = {}
        for cluster in self.clusters:
            for node in cluster.return_key_nodes(key="Halo", value=False):
                if node.tortuosity is not None:
                    tortuosity[str(node.labels["UC_index"])] = node.tortuosity

        self.tortuosity = tortuosity

    def set_minimal_clusters(self) -> None:
        """Access to the information on unique unit cell clusters.
        
        Cycles through the halo clusters, gets a set unique cluster sites and sets up 
        minimal_Cluster object to store and access the data.

        Sets:
            self.min_clusters: A list of minimal_Cluster objects for unit cell in graph.
        """
        site_sets: list[frozenset[int]] = []
        for cluster in self.clusters:
            indices = frozenset(
                [int(node.labels["UC_index"]) for node in cluster.nodes]
            )
            site_sets.append(indices)

        unique_site_sets = set(site_sets)

        self.min_clusters = []

        for sites in unique_site_sets:
            self.min_clusters.append(
                minimal_Cluster(site_indices=list(sites), size=len(sites))
            )

        for cluster in self.clusters:
            for min_clus in self.min_clusters:
                if min_clus.site_indices[0] in set(
                    [int(node.labels["UC_index"]) for node in cluster.nodes]
                ):
                    min_clus.periodic = cluster.periodic

        for min_clus in self.min_clusters:
            if min_clus.periodic is not None and min_clus.periodic > 0:
                min_clus.tortuosity = 0
                for site_index in min_clus.site_indices:
                    if self.tortuosity is not None and str(site_index) in self.tortuosity:
                        min_clus.tortuosity += self.tortuosity[str(site_index)]
                min_clus.tortuosity = min_clus.tortuosity / min_clus.size

    def torture(self) -> None:
        """Torture the graph and set node tortuosity for UC nodes in cluster.
        
        This only tortures UC nodes in each cluster, but the graph contains
        a halo of clusters.
        """
        for cluster in self.clusters:
            if cluster.periodic is not None and cluster.periodic > 0:
                cluster.torture_fort()

        self.set_site_tortuosity()
        self.set_minimal_clusters()

    def torture_py(self) -> None:
        """Torture the graph and set node tortuosity for UC nodes in cluster.
        
        This only tortures UC nodes in each cluster, but the graph contains
        a halo of clusters. Uses pure Python implementation.
        """
        for cluster in self.clusters:
            if cluster.periodic is not None and cluster.periodic > 0:
                cluster.torture_py()

        self.set_site_tortuosity()
        self.set_minimal_clusters()

    def output_clusters(self, fmt: str, periodic: bool | None = None) -> None:
        """Output the unique unit cell clusters from the graph.

        Args:
            fmt: Output format for pymatgen structures set up from clusters.
            periodic: Whether to output only periodic clusters.

        Outputs:
            CLUS_*.{fmt}: A cluster structure file for each cluster in the graph.
        """
        if fmt == "poscar":
            tail = "vasp"
        else:
            tail = fmt

        site_sets: list[frozenset[int]] = []

        for cluster in self.clusters:
            if periodic:
                if cluster.periodic is not None and cluster.periodic > 0:
                    site_sets.append(
                        frozenset(
                            [int(node.labels["UC_index"]) for node in cluster.nodes]
                        )
                    )
            else:
                site_sets.append(
                    frozenset([int(node.labels["UC_index"]) for node in cluster.nodes])
                )

        unique_site_sets = set(site_sets)

        if self.structure is None:
            raise ValueError("Structure is required for output_clusters")

        for index, site_list in enumerate(unique_site_sets):
            cluster_structure = Structure(
                lattice=self.structure.lattice, species=[], coords=[]
            )
            symbols = [species for species in self.structure.symbol_set]
            if "X" in set(symbols):
                symbols.remove("X")
                symbols.append("X0+")
            for symbol in symbols:
                for site_index in site_list:

                    periodic_site = self.structure.sites[site_index]

                    if periodic_site.species_string == symbol:
                        cluster_structure.append(
                            symbol, periodic_site.coords, coords_are_cartesian=True
                        )

            cluster_structure.to(fmt=fmt, filename="CLUS_" + str(index) + "." + tail)  # type: ignore[arg-type]

    def return_periodic_structure(self, fmt: str) -> Structure:
        """Gather all periodic clusters in the graph as a single pymatgen Structure.

        Args:
            fmt: Output format for pymatgen structure set up from cluster.

        Returns:
            Structure object containing all periodic clusters.
        """
        site_sets: list[frozenset[int]] = []

        for cluster in self.clusters:
            if cluster.periodic is not None and cluster.periodic > 0:
                site_sets.append(
                    frozenset([int(node.labels["UC_index"]) for node in cluster.nodes])
                )

        unique_site_sets = set(site_sets)
        
        if self.structure is None:
            raise ValueError("Structure is required for return_periodic_structure")
            
        cluster_structure = Structure(
            lattice=self.structure.lattice, species=[], coords=[]
        )

        for index, site_list in enumerate(unique_site_sets):
            symbols = [species for species in self.structure.symbol_set]
            if "X" in set(symbols):
                symbols.remove("X")
                symbols.append("X0+")
            for symbol in symbols:
                for site_index in site_list:

                    periodic_site = self.structure.sites[site_index]

                    if periodic_site.species_string == symbol:
                        cluster_structure.append(
                            symbol, periodic_site.coords, coords_are_cartesian=True
                        )

        return cluster_structure

    def return_frac_percolating(self) -> float:
        """Calculate the fraction of nodes in the graph that are in a periodic cluster.

        Returns:
            Fraction: nodes in graph in periodic clusters / total number of nodes.
        """
        total_nodes = 0
        periodic_nodes = 0

        for cluster in self.clusters:

            total_nodes += len(cluster.return_key_nodes(key="Halo", value=False))

            if cluster.periodic is not None and cluster.periodic > 0:
                periodic_nodes += len(cluster.return_key_nodes(key="Halo", value=False))

        return periodic_nodes / total_nodes if total_nodes > 0 else 0.0

    @property
    def minimal_clusters(self) -> list[minimal_Cluster]:
        """Get minimal clusters.
        
        Returns:
            List of minimal cluster objects.
            
        Raises:
            ValueError: If minimal_clusters is not set until graph.torture() or 
                       graph.torture_py() have been called.
        """
        if self.min_clusters is None:
            raise ValueError(
                "minimal_clusters is not set until graph.torture() or graph.torture_py() have been called"
            )
        else:
            return self.min_clusters