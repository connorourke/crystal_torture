"""Module for edge-weighted graph percolation analysis.

This module provides functionality for:
- Loading and saving edge data in JSON format
- Filtering edges by weight thresholds
- Generating edge data from crystal structures
- Constructing graphs from explicit edge lists for percolation analysis
"""

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from pymatgen.core import Structure, PeriodicSite

from crystal_torture.node import Node
from crystal_torture.cluster import clusters_from_nodes
from crystal_torture.graph import Graph
from crystal_torture.pymatgen_interface import get_all_neighbors_and_image


@dataclass
class Edge:
    """Represents a single edge between two nodes.

    Attributes:
        nodes: Tuple of two node indices (i, j) where i < j (canonical ordering).
        weight: Optional weight value for the edge. If None, edge is unweighted.
    """
    nodes: tuple[int, int]
    weight: float | None = None


@dataclass
class EdgeData:
    """Container for edge data with validation and filtering capabilities.

    Attributes:
        num_nodes: Total number of nodes in the graph.
        edges: List of Edge objects defining connections.
    """
    num_nodes: int
    edges: list[Edge]

    def __post_init__(self) -> None:
        """Validate edge data after initialisation.

        Raises:
            ValueError: If num_nodes is not positive.
            ValueError: If any edge references an invalid node index.
            ValueError: If edges are not in canonical order (i < j).
            ValueError: If duplicate edges exist.
            ValueError: If edge weights are inconsistent (some with, some without).
        """
        # Validate num_nodes is positive
        if self.num_nodes <= 0:
            raise ValueError(f"num_nodes must be positive, got {self.num_nodes}")

        seen_edges: set[tuple[int, int]] = set()

        for edge in self.edges:
            i, j = edge.nodes

            # Validate node indices are non-negative
            if i < 0 or j < 0:
                raise ValueError(
                    f"Edge node index must be non-negative, got edge ({i}, {j})"
                )

            # Validate node indices are within range
            if i >= self.num_nodes or j >= self.num_nodes:
                raise ValueError(
                    f"Edge node index out of range: edge ({i}, {j}) "
                    f"but num_nodes is {self.num_nodes}"
                )

            # Validate canonical ordering
            if i >= j:
                raise ValueError(
                    f"Edge nodes must be in canonical order (i < j), "
                    f"got edge ({i}, {j})"
                )

            # Check for duplicates
            if edge.nodes in seen_edges:
                raise ValueError(f"Duplicate edge found: ({i}, {j})")
            seen_edges.add(edge.nodes)

        # Validate weight consistency
        if self.edges:
            has_weight = [e.weight is not None for e in self.edges]
            if any(has_weight) and not all(has_weight):
                raise ValueError(
                    "Edge weights are inconsistent: all edges must have weights "
                    "or none must have weights"
                )

    @property
    def weighted(self) -> bool:
        """Return True if edges have weights assigned.

        Returns:
            True if all edges have numeric weights, False if edges are unweighted
            or if there are no edges.
        """
        if not self.edges:
            return False
        return self.edges[0].weight is not None

    def filter(self, predicate: Callable[[Edge], bool]) -> 'EdgeData':
        """Return new EdgeData containing only edges matching predicate.

        Args:
            predicate: Function that takes an Edge and returns True to keep it.

        Returns:
            New EdgeData instance with filtered edges. num_nodes is preserved.

        Example:
            >>> filtered = edge_data.filter(lambda e: e.weight <= 0.5)
            >>> by_node = edge_data.filter(lambda e: 0 in e.nodes)
        """
        filtered_edges = [e for e in self.edges if predicate(e)]
        # Use object.__new__ to bypass __post_init__ validation temporarily,
        # then set attributes directly. This avoids re-validation of edges
        # that were already validated.
        result = object.__new__(EdgeData)
        result.num_nodes = self.num_nodes
        result.edges = filtered_edges
        return result


def load_edges(filename: str | Path) -> EdgeData:
    """Load edge data from JSON file.

    Args:
        filename: Path to JSON file.

    Returns:
        EdgeData instance.

    Raises:
        ValueError: If JSON is malformed or invalid.
        ValueError: If required fields are missing.
        ValueError: If edges have inconsistent weights (some with, some without).
    """
    try:
        with open(filename, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    # Validate required fields
    if "num_nodes" not in data:
        raise ValueError("Missing required field: num_nodes")
    if "edges" not in data:
        raise ValueError("Missing required field: edges")

    num_nodes = data["num_nodes"]
    edges = []

    for edge_dict in data["edges"]:
        nodes = tuple(edge_dict["nodes"])
        weight = edge_dict.get("weight")
        edges.append(Edge(nodes=nodes, weight=weight))

    return EdgeData(num_nodes=num_nodes, edges=edges)


def save_edges(edge_data: EdgeData, filename: str | Path) -> None:
    """Write edge data to JSON file.

    Args:
        edge_data: EdgeData to save.
        filename: Output path.
    """
    edges_list = []
    for edge in edge_data.edges:
        # Convert numpy types to native Python types for JSON serialization
        nodes = [int(edge.nodes[0]), int(edge.nodes[1])]
        edge_dict: dict = {"nodes": nodes}
        if edge.weight is not None:
            edge_dict["weight"] = float(edge.weight)
        edges_list.append(edge_dict)

    data = {
        "num_nodes": int(edge_data.num_nodes),
        "edges": edges_list,
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def edges_from_structure(
    structure: Structure,
    rcut: float,
    weight_fn: Callable[[PeriodicSite, PeriodicSite, float], float] | None = None,
) -> EdgeData:
    """Generate EdgeData from structure geometry.

    Args:
        structure: Pymatgen Structure.
        rcut: Cutoff radius for edges.
        weight_fn: Function(site_i, site_j, distance) -> weight.
                   Sites passed in canonical order (lower index first).
                   If None, edges have no weights (weight=None).

    Returns:
        EdgeData with edges for all site pairs within rcut.
    """
    neighbours = get_all_neighbors_and_image(structure, rcut, include_index=True)

    # Collect unique edges with canonical ordering
    seen_edges: set[tuple[int, int]] = set()
    edges: list[Edge] = []

    for i, site_neighbours in enumerate(neighbours):
        for neighbour_info in site_neighbours:
            # neighbour_info is (PeriodicSite, distance, index, image)
            neighbour_site, distance, j, _ = neighbour_info
            j = int(j)  # Convert numpy int64 to Python int

            # Skip self-edges
            if i == j:
                continue

            # Canonical ordering: i < j
            if i < j:
                edge_key = (i, j)
                site_i = structure.sites[i]
                site_j = neighbour_site
            else:
                edge_key = (j, i)
                site_i = neighbour_site
                site_j = structure.sites[i]

            # Skip if we've already added this edge
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)

            # Calculate weight if weight function provided
            if weight_fn is not None:
                weight = weight_fn(site_i, site_j, distance)
            else:
                weight = None

            edges.append(Edge(nodes=edge_key, weight=weight))

    # Sort edges for consistent ordering
    edges.sort(key=lambda e: e.nodes)

    return EdgeData(num_nodes=len(structure.sites), edges=edges)


def edges_from_labels(
    structure: Structure,
    rcut: float,
    label_weights: dict[tuple[str, str], float],
) -> EdgeData:
    """Generate EdgeData from structure with weights based on site labels.

    Convenience wrapper around edges_from_structure for the common case
    where edge weights are determined by the labels of the connected sites.
    Handles symmetry automatically: if (l1, l2) not found, tries (l2, l1).

    Args:
        structure: Pymatgen Structure with labelled sites.
        rcut: Cutoff radius for edges.
        label_weights: Dict mapping (label1, label2) -> weight.

    Returns:
        EdgeData with weighted edges for all site pairs within rcut.

    Raises:
        KeyError: If a label pair is not found in label_weights (in either order).
    """
    def weight_fn(site_i: PeriodicSite, site_j: PeriodicSite, d: float) -> float:
        label_i = site_i.properties["label"]
        label_j = site_j.properties["label"]

        # Try both orders
        if (label_i, label_j) in label_weights:
            return label_weights[(label_i, label_j)]
        elif (label_j, label_i) in label_weights:
            return label_weights[(label_j, label_i)]
        else:
            raise KeyError(
                f"Label pair ({label_i}, {label_j}) not found in label_weights "
                f"(tried both orders)"
            )

    return edges_from_structure(structure, rcut, weight_fn)


def graph_from_edges(
    structure: Structure,
    edge_data: EdgeData,
) -> Graph:
    """Construct graph from structure and edge list.

    Uses structure geometry to determine periodic boundary handling.
    The search radius is automatically determined from the lattice dimensions
    to find all relevant periodic images for proper periodicity detection.

    Args:
        structure: Pymatgen Structure (for geometry/PBC).
        edge_data: Edges to include in graph.

    Returns:
        Graph ready for percolation analysis.

    Raises:
        ValueError: If edge_data.num_nodes does not match structure sites.
    """
    from crystal_torture.pymatgen_interface import (
        create_halo,
        set_fort_nodes,
    )

    # Validate that edge_data matches structure
    if edge_data.num_nodes != len(structure.sites):
        raise ValueError(
            f"edge_data.num_nodes ({edge_data.num_nodes}) does not match "
            f"structure sites ({len(structure.sites)})"
        )

    working_structure = deepcopy(structure)
    num_sites = len(working_structure.sites)

    # Add UC_index property to track original unit cell site
    working_structure.add_site_property(
        "UC_index", [str(i) for i in range(num_sites)]
    )

    # Build set of edge pairs from edge data (canonical ordering)
    edge_set: set[tuple[int, int]] = set()
    for edge in edge_data.edges:
        i, j = int(edge.nodes[0]), int(edge.nodes[1])
        edge_set.add((min(i, j), max(i, j)))

    # Calculate search radius from the minimum lattice vector length
    # In a periodic structure, the minimum image of any neighbour must be
    # within half the smallest cell dimension (otherwise a closer image exists)
    # We use this as the search radius to find all relevant periodic images
    lattice = working_structure.lattice
    search_radius = min(lattice.a, lattice.b, lattice.c) / 2.0 + 0.1
    if not edge_data.edges:
        search_radius = 0.1

    # Find all neighbours with image information
    neighbours_with_images = get_all_neighbors_and_image(
        working_structure, search_radius, include_index=True
    )

    # Filter to only keep neighbours that correspond to edges in edge_data
    # Keep the tuple format expected by create_halo: (site, distance, index, image)
    neighbours: list[list[tuple]] = [[] for _ in range(num_sites)]
    for i in range(num_sites):
        for neighbour_info in neighbours_with_images[i]:
            neighbour_site, distance, j, image = neighbour_info
            # Check if this edge exists in edge_data (canonical ordering)
            edge_key = (min(i, int(j)), max(i, int(j)))
            if edge_key in edge_set:
                neighbours[i].append(neighbour_info)

    # Use existing create_halo to handle supercell construction
    working_structure, neighbours_mapped = create_halo(
        working_structure, neighbours
    )

    # Central unit cell indices
    uc_index_set = set([(index * 27) + 13 for index in range(num_sites)])

    # Create nodes
    nodes: list[Node] = []
    for index, site in enumerate(working_structure.sites):
        is_halo = index not in uc_index_set
        node_neighbours_ind = set(neighbours_mapped[index])
        nodes.append(
            Node(
                index=index,
                element=site.species_string,
                uc_index=int(site.properties["UC_index"]),
                is_halo=is_halo,
                neighbours_ind=node_neighbours_ind,
            )
        )

    # Set up neighbour references
    for node in nodes:
        node.neighbours = set()
        for neighbour_ind in node.neighbours_ind:
            node.neighbours.add(nodes[neighbour_ind])

    # Set up Fortran module if available (for torture())
    try:
        set_fort_nodes(set(nodes))
    except Exception:
        pass  # Fortran not available, torture_py() will still work

    # Create clusters from nodes
    clusters = clusters_from_nodes(set(nodes))

    return Graph(clusters=clusters, structure=structure)
