"""Functions for setting up a node, cluster and graph using pymatgen."""

from crystal_torture.node import Node
from crystal_torture.cluster import Cluster, clusters_from_nodes
from crystal_torture.graph import Graph
from crystal_torture.exceptions import FortranNotAvailableError
import numpy as np
import itertools
import math
from copy import deepcopy
import sys
import time
from pymatgen.core import Structure, Molecule, PeriodicSite
from types import ModuleType
import numpy.typing as npt

# Module variables with proper type hints
dist: ModuleType | None
tort: ModuleType | None

try:
    from . import dist
except ImportError:
    dist = None

try:
    from . import tort
except ImportError:
    tort = None


def _python_dist(coord1: npt.NDArray[np.floating], coord2: npt.NDArray[np.floating], n: int) -> npt.NDArray[np.floating]:
    """Pure Python fallback for distance calculation when Fortran dist module is not available.
    
    Args:
        coord1: Array of coordinates.
        coord2: Array of coordinates.  
        n: Number of coordinates.
        
    Returns:
        Distance matrix.
    """
    # Use numpy broadcasting for vectorized calculation
    # coord1[:, None, :] creates shape (n, 1, 3)
    # coord2[None, :, :] creates shape (1, n, 3)  
    # Subtraction creates shape (n, n, 3)
    # np.linalg.norm computes distances along axis=2
    return np.linalg.norm(coord1[:, None, :] - coord2[None, :, :], axis=2)

def _python_shift_index(index_n: int, shift: list[int]) -> int:
    """Pure Python fallback for index shifting when Fortran dist module is not available.
    
    Args:
        index_n: Original index (must be non-negative).
        shift: Shift vector [x, y, z].
        
    Returns:
        New shifted index.
        
    Raises:
        ValueError: If index_n is negative.
    """
    if index_n < 0:
        raise ValueError(f"shift_index received negative index: {index_n}. This indicates an upstream bug.")
        
    new_x = (int(index_n // 9) % 3 + shift[0]) % 3
    new_y = (int(index_n // 3) % 3 + shift[1]) % 3  
    new_z = (index_n % 3 + shift[2]) % 3
    
    new_index = int(27 * int(index_n // 27) + (new_x % 3) * 9 + (new_y % 3) * 3 + (new_z % 3))
    return new_index


def map_index(
    uc_neighbours: list[list[int]], 
    uc_index: list[int], 
    x_d: int, 
    y_d: int, 
    z_d: int
) -> list[list[int]]:
    """Take a list of neighbour indices for sites in the original unit cell and map them onto all supercell sites.
    
    Args:
        uc_neighbours: List of lists containing neighbour indices for the nodes that are in the primitive cell.
        uc_index: List of indices corresponding to the primitive cell nodes.
        x_d: X dimension of supercell.
        y_d: Y dimension of supercell.
        z_d: Z dimension of supercell.
    
    Returns:
        List of neighbour indices for all nodes.
    """
    if dist is None:
        shift_func = _python_shift_index
    else:
        shift_func = dist.shift_index

    no_atoms = len(uc_index)
    count = -1
    neigh: list[list[int]] = []
    append = neigh.append
    for i, index in enumerate(uc_index):
        for x in range(0, x_d, 1):
            for y in range(0, y_d, 1):
                for z in range(0, z_d, 1):
                    count += 1
                    append(
                        [
                            shift_func(neighbour, [x, y, z])
                            for neighbour in uc_neighbours[i]
                        ]
                    )
    return neigh


def get_all_neighbors_and_image(structure: Structure, r: float, include_index: bool = False) -> list[list[tuple]]:
    """Get neighbours for each atom in the unit cell, out to a distance r.
    
    Modified from pymatgen to return image (used for mapping to supercell), and to use the f2py wrapped
    OpenMP dist subroutine to get the distances (smaller memory footprint and faster than numpy).

    Returns a list of list of neighbors for each site in structure.
    Use this method if you are planning on looping over all sites in the
    crystal. If you only want neighbors for a particular site, use the
    method get_neighbors as it may not have to build such a large supercell
    However if you are looping over all sites in the crystal, this method
    is more efficient since it only performs one pass over a large enough
    supercell to contain all possible atoms out to a distance r.
    
    Args:
        structure: Pymatgen Structure object.
        r: Radius of sphere.
        include_index: Whether to include the non-supercell site in the returned data.

    Returns:
        A list of a list of nearest neighbors for each site, i.e., 
        [[(site, dist, index, image) ...], ..]. Index only supplied if include_index = True.
        The index is the index of the site in the original (non-supercell)
        structure. This is needed for ewaldmatrix by keeping track of which
        sites contribute to the ewald sum.
    """
    # Choose distance calculation function based on availability
    if dist is None:
        dist_func = _python_dist
    else:
        dist_func = dist.dist
    
    recp_len = np.array(structure.lattice.reciprocal_lattice.abc)
    maxr = np.ceil((r + 0.15) * recp_len / (2 * math.pi))
    nmin = np.floor(np.min(structure.frac_coords, axis=0)) - maxr
    nmax = np.ceil(np.max(structure.frac_coords, axis=0)) + maxr

    all_ranges = [np.arange(x, y) for x, y in zip(nmin, nmax)]

    latt = structure._lattice
    neighbors: list[list[tuple]] = [list() for i in range(len(structure._sites))]
    all_fcoords = np.mod(structure.frac_coords, 1)
    coords_in_cell = latt.get_cartesian_coords(all_fcoords)
    site_coords = structure.cart_coords

    indices = np.arange(len(structure))
    for image in itertools.product(*all_ranges):
        coords = latt.get_cartesian_coords(image) + coords_in_cell
        all_dists = dist_func(coords, site_coords, len(coords))
        all_within_r = np.bitwise_and(all_dists <= r, all_dists > 1e-8)

        for (j, d, within_r) in zip(indices, all_dists, all_within_r):
            nnsite = PeriodicSite(
                structure[j].specie,
                coords[j],
                latt,
                properties=structure[j].properties,
                coords_are_cartesian=True,
            )
            for i in indices[within_r]:
                item = (nnsite, d[i], j, image) if include_index else (nnsite, d[i])
                neighbors[i].append(item)
    return neighbors


def create_halo(structure: Structure, neighbours: list[list[tuple]]) -> tuple[Structure, list[list[int]]]:
    """Take a pymatgen structure object and set up a halo by making a 3x3x3 supercell.
    
    Args:
        structure: Pymatgen Structure object.
        neighbours: List of neighbours for sites in structure (from get_all_neighbors_and_image).
    
    Returns:
        Tuple containing:
            - structure: 3x3x3 supercell pymatgen Structure object.
            - neighbours: New list of neighbours for sites in supercell structure.
    """
    if dist is None:
        shift_func = _python_shift_index
    else:
        shift_func = dist.shift_index
        
    x = 3
    y = 3
    z = 3
    
    no_sites = len(structure.sites)
    new_neighbours: list[list[int]] = []
    for i in range(no_sites):
        new_neighbours.append([
            shift_func((27 * neighbour[2]), neighbour[3])
            for neighbour in neighbours[i]
        ])
    
    uc_index = [((site * 27)) for site in range(len(structure.sites))]
    structure.make_supercell([x, y, z])
    neighbours_mapped = map_index(new_neighbours, uc_index, x, y, z)
    
    return structure, neighbours_mapped

def nodes_from_structure(structure: Structure, rcut: float, get_halo: bool = False) -> set[Node]:
    """Take a pymatgen structure object and convert to Nodes for interrogation."""
    working_structure = deepcopy(structure)
    working_structure.add_site_property(
        "UC_index", [str(i) for i in range(len(working_structure.sites))]
    )
    neighbours = get_all_neighbors_and_image(working_structure, rcut, include_index=True)
    nodes: list[Node] = []
    
    no_nodes = len(working_structure.sites)
    if get_halo == True:
        working_structure, neighbours_mapped = create_halo(working_structure, neighbours)
        uc_index = set([((index * 27) + 13) for index in range(no_nodes)])
    else:
        uc_index = set(range(no_nodes))
        neighbours_temp: list[list[int]] = []
        for index, neigh in enumerate(neighbours):
            neighbours_temp.append([neigh_ind[2] for neigh_ind in neigh])
        neighbours_mapped = neighbours_temp
    
    append = nodes.append
    
    for index, site in enumerate(working_structure.sites):
        if index in uc_index:
            halo_node = False
        else:
            halo_node = True
        node_neighbours_ind = set(neighbours_mapped[index])
        append(
            Node(
                index=index,
                element=site.species_string,
                uc_index=int(site.properties["UC_index"]),
                is_halo=halo_node,
                neighbours_ind=node_neighbours_ind,
            )
        )
    
    for node in nodes:
        node.neighbours = set()
        for neighbour_ind in node.neighbours_ind:
            node.neighbours.add(nodes[neighbour_ind])
    
    return set(nodes)

def set_fort_nodes(nodes: set[Node]) -> None:
    """Set up a copy of the nodes and the neighbour indices in the tort.f90 Fortran module.
    
    This allows access if using the Fortran tortuosity routines.
    
    Args:
       nodes: Set of Node objects to set up in Fortran module.
       
    Sets:
       tort.tort_mod.nodes: Allocates space to hold node indices for full graph.
       tort.tort_mod.uc_tort: Allocates space to hold unit cell node tortuosity for full graph.
       
    Raises:
        FortranNotAvailableError: If Fortran extensions are not available.
    """
    if tort is None:
        raise FortranNotAvailableError()
    
    tort.tort_mod.allocate_nodes(
        len(nodes), len([node for node in nodes if node.is_halo == False])
    )
    for node in nodes:
        tort.tort_mod.set_neighbours(
            node.index,
            node.uc_index,
            len(node.neighbours_ind),
            [ind for ind in node.neighbours_ind],
        )


def clusters_from_file(filename: str,
        rcut: float,
        elements: set[str]) -> set[Cluster]:
    structure = Structure.from_file(filename)
    return clusters_from_structure(
        structure=structure,
        rcut=rcut,
        elements=elements
    )


def clusters_from_structure(structure: Structure, rcut: float, elements: set[str]) -> set[Cluster]:
    """Take a pymatgen structure and convert it to a graph object.
    
    Args:
        structure: Pymatgen structure object to set up graph from.
        rcut: Cut-off radii for node-node connections in forming clusters.
        elements: Set of element strings to include in setting up graph.
        
    Returns:
        Set of clusters.
    """
    working_structure = filter_structure_by_species(structure, list(elements))
    folded_structure = Structure.from_sites(working_structure.sites, to_unit_cell=True)
    nodes = nodes_from_structure(folded_structure, rcut, get_halo=True)
    set_fort_nodes(nodes)
    clusters = clusters_from_nodes(nodes)
    return clusters

def graph_from_structure(structure: Structure, rcut: float, elements: set[str]) -> Graph:
    """Create a graph from a pymatgen structure.
    
    Creates a Graph object containing clusters of connected nodes and a filtered
    structure. The clusters are formed by connecting sites within the cutoff
    radius, and only sites with the specified elements are included.
    
    Args:
        structure: Pymatgen Structure object to create graph from.
        rcut: Cutoff radius for node-node connections in forming clusters.
        elements: Set of element strings to include in the graph.
        
    Returns:
        Graph object containing clusters and filtered structure.
        
    Example:
        >>> structure = Structure(lattice, ["Li", "Mg", "O"], coords)
        >>> graph = graph_from_structure(structure, 3.0, {"Li", "O"})
        >>> graph.clusters  # Clusters containing only Li and O sites
    """
    clusters = clusters_from_structure(structure, rcut, elements)
    filtered_structure = filter_structure_by_species(structure, list(elements))
    return Graph(clusters=clusters, structure=filtered_structure)

def graph_from_file(filename: str, rcut: float, elements: set[str]) -> Graph:
    structure = Structure.from_file(filename)
    return graph_from_structure(structure, rcut, elements)
    
def filter_structure_by_species(structure: Structure, species_list: list[str]) -> Structure:
    """Filter structure to keep only specified species.
    
    Creates a new Structure containing only the sites with species that are
    in the provided species list. The original structure is not modified.
    
    Args:
        structure: Pymatgen Structure object to filter.
        species_list: List of element symbols to keep in the filtered structure.
            
    Returns:
        New Structure object containing only sites with species in species_list.
        
    Raises:
        ValueError: If species_list is empty.
        ValueError: If species_list contains elements not present in the structure.
        
    Example:
        >>> structure = Structure(lattice, ["Li", "Mg", "O"], coords)
        >>> filtered_structure = filter_structure_by_species(structure, ["Li", "O"])
        >>> filtered_structure.symbol_set  # {"Li", "O"}
    """
    if not species_list:
        raise ValueError("species_list cannot be empty")
    invalid_species = [spec for spec in species_list if spec not in structure.symbol_set]
    if invalid_species:
        raise ValueError(f"Species {invalid_species} not found in structure")
        
    filtered_structure = deepcopy(structure)
    species_to_remove = [spec for spec in structure.symbol_set if spec not in species_list]
    filtered_structure.remove_species(species_to_remove)    
    return filtered_structure