from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from crystal_torture.graph import Graph
from crystal_torture import dist
from crystal_torture import tort
from pymatgen import Structure, Molecule, PeriodicSite
import numpy as np
import itertools
import math
import copy
import sys
import time

"Functions for setting up a node, cluster and graph using pymatgen"

def map_index(uc_neighbours, uc_index, x_d, y_d, z_d):
    """
    Takes a list of neighbour indices for sites in the original unit cell, 
    and maps them on to all of the supercell sites.
    
    Args:

        - uc_neighbours(list(list(int))): list of lists containing neighbour indices for the nodes that are in the primitive cell
        - uc_index(list(int)): list of indices corresponding to the primitive cell nodes
        - x_d (int): x dimension of supercell
        - y_d (int): y dimension of supercell
        - z_d (int): z dimension of supercell


    
    Returns:

        - neigh ([[int]...[int]]): list of neighbour indices for all nodes

    """

    no_atoms = len(uc_index)
    count = -1
    neigh = []
    append = neigh.append
    for i,index in enumerate(uc_index):
       for x in range(0,x_d,1):
         for y in range(0,y_d,1):
            for z in range(0,z_d,1):
               count+=1
               append([dist.shift_index(neighbour,[x,y,z]) for neighbour in uc_neighbours[i]])
    return neigh

def get_all_neighbors_and_image(structure, r, include_index=False):

    """
    Modified from `pymatgen 
    <http://pymatgen.org/_modules/pymatgen/core/structure.html#IStructure.get_all_neighbors>`_ 
    to return image (used for mapping to supercell), and to use the f2py wrapped
    OpenMP dist subroutine to get the distances (smaller memory footprint and faster
    than numpy).

    Get neighbours for each atom in the unit cell, out to a distance r
    Returns a list of list of neighbors for each site in structure.
    Use this method if you are planning on looping over all sites in the
    crystal. If you only want neighbors for a particular site, use the
    method get_neighbors as it may not have to build such a large supercell
    However if you are looping over all sites in the crystal, this method
    is more efficient since it only performs one pass over a large enough
    supercell to contain all possible atoms out to a distance r.
    The return type is a [(site, dist) ...] since most of the time,
    subsequent processing requires the distance.

    
    Args:
        - r (float): Radius of sphere.
        - include_index (bool): Whether to include the non-supercell site
        - in the returned data

    Returns:
        - A list of a list of nearest neighbors for each site, i.e., 
        [[(site, dist, index, image) ...], ..]. Index only supplied if include_index = True.
        The index is the index of the site in the original (non-supercell)
        structure. This is needed for ewaldmatrix by keeping track of which
        sites contribute to the ewald sum.


    """
    recp_len = np.array(structure.lattice.reciprocal_lattice.abc)
    maxr = np.ceil((r + 0.15) * recp_len / (2 * math.pi))
    nmin = np.floor(np.min(structure.frac_coords, axis=0)) - maxr
    nmax = np.ceil(np.max(structure.frac_coords, axis=0)) + maxr

    all_ranges = [np.arange(x, y) for x, y in zip(nmin, nmax)]

    latt = structure._lattice
    neighbors = [list() for i in range(len(structure._sites))]
    all_fcoords = np.mod(structure.frac_coords, 1)
    coords_in_cell = latt.get_cartesian_coords(all_fcoords)
    site_coords = structure.cart_coords

    indices = np.arange(len(structure))
    for image in itertools.product(*all_ranges):
        coords = latt.get_cartesian_coords(image) + coords_in_cell
        all_dists = dist.dist(coords, site_coords, len(coords))
        all_within_r = np.bitwise_and(all_dists <= r, all_dists > 1e-8)

        for (j, d, within_r) in zip(indices, all_dists, all_within_r):
            nnsite = PeriodicSite(structure[j].species_and_occu, coords[j],
                                    latt, properties=structure[j].properties,
                                    coords_are_cartesian=True)
            for i in indices[within_r]:
                item = (nnsite, d[i], j, image) if include_index else (
                    nnsite, d[i])
                neighbors[i].append(item)
    return neighbors


def create_halo(structure, neighbours):
    """
    Takes a pymatgen structure object, sets up a halo by making a 3x3x3 supercell,
    

    Args:

        - structure (Structure): pymatgen Structure object
        - neighbours  [[(site, dist, index, image) ...], ..]: list of neighbours for sites in structure

    Returns:

        - structure (Structure): 3x3x3x supercell pymatgen Structure object
        - neighbours  [[(site, dist, index, image) ...], ..]: new list of neighbours for sites in supercell structure


    """
    x = 3
    y = 3
    z = 3

    no_sites = len(structure.sites)
    for i in range(no_sites):
       neighbours[i]=[dist.shift_index((27*neighbour[2]),neighbour[3]) for neighbour in neighbours[i]]
      
    uc_index = [((site * 27)) for site in range(len(structure.sites))]
    structure.make_supercell([x,y,z])
    neighbours = map_index(neighbours,uc_index,x,y,z)
    
     

    return structure, neighbours

#@profile
def nodes_from_structure(structure, rcut, get_halo=False):
    """
    Takes a pymatgen structure object and converts to Nodes for interogation.

    Args:

        - structure (Structure): pymatgen Structure object
        - rcut (float): cut-off radius for crystal site neighbour set-up
        - halo (bool): whether to set up halo nodes (i.e. 3x3x3 supercell)

    Returns:
        - nodes (set(Nodes)): set of Node objects representing structure sites
  
    """
    structure.add_site_property("UC_index", [str(i) for i in range(len(structure.sites))] )
    neighbours = get_all_neighbors_and_image(structure,rcut,include_index=True)
    nodes = []


    no_nodes = len(structure.sites)
    if get_halo == True:
       structure,neighbours = create_halo(structure, neighbours)
       uc_index = set([((index * 27 ) +13) for index in range(no_nodes)])
    else:
       uc_index =  set([range(no_nodes)])
       neighbours_temp = []
       for index,neigh in enumerate(neighbours):
           neighbours_temp.append([neigh_ind[2] for neigh_ind in neigh])        
       neighbours = neighbours_temp
            

    append = nodes.append
 
    for index,site  in enumerate(structure.sites):
         
        if index in uc_index:
           halo_node = False
        else:
           halo_node = True
        node_neighbours_ind = set(neighbours[index])
        append(Node(index = index, element = site.species_string, labels = {"UC_index":site.properties["UC_index"], "Halo":halo_node} , neighbours_ind = node_neighbours_ind))

    for node in nodes:
       node.neighbours = set()
       for neighbour_ind in node.neighbours_ind:
           node.neighbours.add(nodes[neighbour_ind])


    return set(nodes)

#@profile
def set_cluster_periodic(cluster):
    """
    Sets the periodicty of the cluster by counting through the number of 
    labelled UC nodes it contains

    Args:

        - None

    Returns:

       - None

    Sets:

       - cluster.periodic (int): periodicity of the cluster (1=1D,2=2D,3=3D)

    """


    node = cluster.nodes.pop()
    cluster.nodes.add(node)

    key = node.labels["UC_index"]
    no_images = len(cluster.return_key_nodes("UC_index",key))

    if no_images == 27:
       cluster.periodic = 3
    elif no_images == 9:
       cluster.periodic = 2
    elif no_images == 3:
       cluster.periodic = 1
    else:
       cluster.periodic = 0

def set_fort_nodes(nodes):
    """
    Sets up a copy of the nodes and the neighbour indices in the tort.f90 Fortran module
    to allow access if using the Fortran tortuosity routines.

    Args:
       - None
    Returns:
       - None
    Sets:
       - tort.tort_mod.nodes(:) : allocates space to hold node indices for full graph
       - tort.tort_mod.uc_tort(:) : allocates space to hold unit cell node tortuosity for full graph
  
    """

    tort.tort_mod.allocate_nodes(len(nodes),len([node for node in nodes if node.labels["Halo"]==False]))
    for node in nodes:
        tort.tort_mod.set_neighbours(node.index,int(node.labels["UC_index"]),len(node.neighbours_ind),[ind for ind in node.neighbours_ind])


def clusters_from_file(filename, rcut, elements):
    """
    Take a pymatgen compatible file, and converts it to a cluster object

    Args:

        - filename (str): name of file to set up graph from
        - rcut (float):   cut-off radii for node-node connections in forming clusters
        - elements ([str,str,.....]): list of elements to include in setting up graph

    Returns:
        - clusters ({clusters}): set of clusters 

    """
    
    structure = Structure.from_file(filename)
    symbols = set([species for species in structure.symbol_set])
    if set(elements).issubset(symbols):

       sites = [site.to_unit_cell for site in structure.sites]
       structure = Structure.from_sites(sites)

       all_elements = set([species for species in structure.symbol_set])
       remove_elements = [x for x in all_elements if x not in elements]

       structure.remove_species(remove_elements)
       nodes = nodes_from_structure(structure, rcut, get_halo=True)
       set_fort_nodes(nodes)

       clusters = set()

       uc_nodes = set([node for node in nodes if node.labels["Halo"]==False])


       while uc_nodes:
            node=uc_nodes.pop()
            if node.labels["Halo"]==False :
               cluster = Cluster({node})
               cluster.grow_cluster()
               uc_nodes.difference_update(cluster.nodes)
               clusters.add(cluster)
               set_cluster_periodic(cluster)

       return clusters
    else:
       print("The element set fed to 'clusters_from_file' is not a subset of the elements in the file")
       raise ValueError

def clusters_from_structure(structure, rcut, elements):
    """
    Take a pymatgen structure, and converts it to a graph object

    Args:

        - structure (Structure): pymatgen structure object to set up graph from
        - rcut (float):   cut-off radii for node-node connections in forming clusters
        - elements ({str,str,.....}): set of element strings to include in setting up graph

    Returns:

        - clusters ({clusters}): set of clusters 

    """

    
    
    symbols = set([species for species in structure.symbol_set])

    if elements.issubset(structure.symbol_set):

       sites = [site.to_unit_cell for site in structure.sites]
       structure = Structure.from_sites(sites)

       all_elements = set([species for species in structure.symbol_set])
       remove_elements = [x for x in all_elements if x not in elements]

       structure.remove_species(remove_elements)
       nodes = nodes_from_structure(structure, rcut, get_halo=True)
       set_fort_nodes(nodes)

       clusters = set()

       uc_nodes = set([node for node in nodes if node.labels["Halo"]==False])


       while uc_nodes:
            node=uc_nodes.pop()
            if node.labels["Halo"]==False :
               cluster = Cluster({node})
               cluster.grow_cluster()
               uc_nodes.difference_update(cluster.nodes)
               clusters.add(cluster)
               set_cluster_periodic(cluster)

       return clusters
    else:
       print("The element set fed to 'clusters_from_file' is not a subset of the elements in the file")
       raise ValueError

def graph_from_structure(structure,rcut,elements):
    """
    Takes a pymatgen compatible file, an converts it to a graph object

    Args:

        - structure (Structure): pymatgen Structure object to set up graph from
        - rcut (float): cut-off radius node-node connections in forming clusters
        - elements ([str,str,.....]): list of elements to include in setting up graph

    Returns:
        - graph (Graph): graph object for structure
  
    """
    clusters = clusters_from_structure(structure=structure,rcut=rcut,elements=elements)
#    print(elements)

    all_elements = set([species for species in structure.symbol_set])
    remove_elements = [x for x in all_elements if x not in elements]
#    print(structure)
    print("***********")
    structure.remove_species(remove_elements)
#    print(structure)
    graph = Graph(clusters=clusters, structure=structure)

    return graph

def graph_from_file(filename,rcut,elements):
    """
    Takes a pymatgen compatible file, an converts it to a graph object

    Args:

        - filename (str): name of file to set up graph from
        - rcut (float): cut-off radius node-node connections in forming clusters
        - elements ([str,str,.....]): list of elements to include in setting up graph

    Returns:
        - graph (Graph): graph object for structure

    """
    clusters = clusters_from_file(filename=filename,rcut=rcut,elements=elements)
    structure = Structure.from_file(filename)

    all_elements = set([species for species in structure.symbol_set])
    remove_elements = [x for x in all_elements if x not in elements]

    structure.remove_species(remove_elements)
    print(structure)
    graph = Graph(clusters=clusters, structure=structure)

    return graph


