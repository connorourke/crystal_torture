
from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from crystal_torture.dist import dist
from pymatgen import Structure, Molecule
import itertools
import math
import dist
import copy

"Functions for setting up a node, cluster and graph using pymatgen"

def shift_index(index,x_d,y_d,z_d,shift):
   """
   Takes a pymatgen site index, and image and shifts the original index to the apropriate
   site index for the given supercell structure

   Args:
       index (int): original site index
       x_d (int): x dimension of supercell
       y_d (int): y dimension of supercell
       z_d (int): z dimension of supercell
       shift (list[int,int,int]): image to shift to

   Returns:
       new_index (int): index of the site in the new supercell structure
     
   """
   new_x=((int(index/y_d*z_d))%x_d+shift[0])%x_d
   new_y=((int(index/y_d))%y_d+shift[1])%y_d
   new_z=(index%z_d+shift[2])%z_d
   new_index = int(x_d*y_d*z_d*int(index/x_d*y_d*z_d)+(new_x%x_d*y_d*z+new_y%y_d*z_d+new_z%z_d))

   return new_index

def map_index(uc_neighbours, uc_index, x_d, y_d, z_d):
    """
    Takes a list of neighbour indices for sites in the original unit cell, 
    and maps them on to all of the supercell sites.

    Args:
        uc_neighbours(list(list(int))): list of lists containing neighbour inndices for the sites
        that are in the primitive cell
      
        uc_index(list(int)): list of indices corresponding to the primitive cell sites
        x_d (int): x dimension of supercell
        y_d (int): y dimension of supercell
        z_d (int): z dimension of supercell


    Returns:
    

    """

    no_atoms = len(uc_index)
    count = -1
    neigh = []
    for i,index in enumerate(uc_index):
       for x in range(0,x_d,1):
         for y in range(0,y_d,1):
            for z in range(0,z_d,1):
               count+=1

               neigh.append([shift_index(neighbour,[x,y,z]) for neighbour in uc_neighbours[i]])

    return neigh

def get_all_neighbors_and_image(structure, r, include_index=False):

        """
        Modified from pymatgen
        (http://pymatgen.org/_modules/pymatgen/core/structure.html#IStructure.get_all_neighbors) 

        to return image (used for mapping to supercell), and to use the f2py wrapped
        dist subroutine to get the distances (smaller memory footprint and faster
        than numpy).

        Get neighbors for each atom in the unit cell, out to a distance r
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
            r (float): Radius of sphere.
            include_index (bool): Whether to include the non-supercell site
                in the returned data

        Returns:
            A list of a list of nearest neighbors for each site, i.e.,
            [[(site, dist, index, image) ...], ..]
            Index only supplied if include_index = True.
            The index is the index of the site in the original (non-supercell)
            structure. This is needed for ewaldmatrix by keeping track of which
            sites contribute to the ewald sum.


        """
        # Use same algorithm as get_sites_in_sphere to determine supercell but
        # loop over all atoms in crystal
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


def reorder_supercell(structure,neighbours,no_sites):
    """
    Takes a 3x3x3 supercell structure, and a list of site neighbours and 
    reorders so the central unit cell is at the start of the structure
    and the neighbour indices are at the start of the neighbour list.

    Args:
        structure (Structure): pymatgen Structure object
        neighbours (list(int)): list of neighbour indices for each site
        no_sites (int): number of sites in the unit cell

    
    """

    uc_index = [((site * 27 ) +13) for index in range(no_sites)]
    uc_index.reverse()

    structure_sorted=Structure(lattice=structure.lattice,species=[],coords=[])
    neighbours_sorted = []
    for index in uc_index:
       structure_sorted.sites.append(structure.sites[index])
       neighbours_sorted.append(neighbours[index])
       del structure.sites[index]
       del neighbours[index]

    structure_sorted.sites.reverse()
    neighbour_sorted.reverse()

    for index,site in structure.sites:
        structure_sorted.sites.append(site)
        neighbour_sorted.append(neighbours[index])

    return structure_sorted, neighbouor_sorted


def create_halo(structure, neigbours):
    """
    Takes a pymatgen structure object, sets up a halo by making a 3x3x3 supercell,
    and reorders the structure to put original unit cell sites (now in centre of supercell) at
    start of the structure object.

    Args:
        structure (Structure): pymatgen Structure object
        neighbours  [[(site, dist, index, image) ...], ..]: list of neighbours for sites in structure
    Returns:
        None
    """
    x = 3
    y = 3
    z = 3
    no_sites = len(structure.sites)
    

    for i in range(no_sites):#,site in enumerate(structure.sites):
       neighbours[i] = [shift_index((x*y*z*neighbour[2]),neighbour[3]) for neighbour in neighbours[i]]
  
    uc_index = [((site * x*y*z )) for site in range(len(structure.sites))]
    structure.make_supercell([x,y,z])
    neighbours = map_index_proper(neighbours,uc_index,x,y,z)

    structure,neighbours = reorder_supercell(structure,neighbours,no_sites)

        
    return structure, neighbours


def nodes_from_structure(structure, rcut, get_halo=False):
    """
    Takes a structure file and converts to Nodes for interogation.

    Args:
        structure (Structure): pymatgen Structure object
        rcut (float): cut-off radius for crystal site neighbour set-up
        halo (bool): whether to set up halo nodes (i.e. 3x3x3 supercell)

    Returns:
        nodes (set(Nodes)): set of Node objects representing structure sites
  
    """
    structure.add_site_property("UC_index", [str(i) for i in range(len(structure.sites))] )
    neighbours = get_all_neighbors_and_image(structure,rcut,include_index=True)
    nodes = []

    no_nodes = len(structure.sites)
    if get_halo == True:
       structure,neighbours = create_halo(structure, neighbours)


    for index,site  in enumerate(structure.sites):
        if index < no_nodes:
           halo_node = False
        else:
           halo_node = True

        node_neighbours_ind =set([n[2] for n in neighbours[index]])

        nodes.append(Node(index = index, element = site.species_string, labels = {"UC_index":site.properties["UC_index"], "Halo":halo_node} , neighbours_ind = node_neighbours_ind))


    for node in nodes:
       node.neighbours = set()
       for neighbour_ind in node.neighbours_ind:
           node.neighbours.add(nodes[neighbour_ind])

    return set(nodes)


def set_cluster_periodic(clusters, structure, rcut):
    """


    """

    for cluster in clusters:
      nodes=cluster.return_key_nodes(key="Halo",value=False)
      species = [structure.sites[node.index].species_string for node in nodes]
      coords = [(structure.sites[node.index].coords) for node in nodes]


      for axis in range(3):
          temp = Structure(structure.lattice,species,coords,coords_are_cartesian=True)
          super_scale = [1,1,1]
          super_scale[axis]+=1
          temp.make_supercell(super_scale)

          temp_nodes = nodes_from_structure(temp, rcut, get_halo=False)
          temp_clusters = set()

          while temp_nodes:
             temp_cluster = Cluster({temp_nodes.pop()})
             temp_cluster.grow_cluster()
             temp_nodes.difference_update(temp_cluster.nodes)
             temp_clusters.add(temp_cluster)

          if len(temp_clusters) > 1:
             cluster.periodic[axis] = False
          else:
             cluster.periodic[axis] = True


def clusters_from_file(filename, rcut):# elements):
    """



    """

    structure = Structure.from_file(filename)

    elements={"Li","X","X0+"}
    all_elements = set([species for species in structure.symbol_set])
    remove_elements = [x for x in all_elements if x not in elements]

    structure.remove_species(remove_elements)

    nodes = nodes_from_structure(structure, rcut, get_halo=True)
    clusters = set()

    while nodes:
         node=nodes.pop()

         if node.labels["Halo"]==False :
            cluster = Cluster({node})
            cluster.grow_cluster(key="Halo",value=False)
            nodes.difference_update(cluster.nodes)
            clusters.add(cluster)

    set_cluster_periodic(clusters, Structure.from_file(filename), rcut)

    # add halo nodes to clusters
    for cluster in clusters:
        cluster.grow_cluster()


        print(cluster.periodic)

    return clusters

