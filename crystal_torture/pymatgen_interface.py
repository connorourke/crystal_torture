
from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from pymatgen import Structure

"Functions for setting up a node, cluster and graph using pymatgen"

def nodes_from_structure(structure, rcut):
    """
    Takes a structure file and converts to Nodes for interogation.

    Args:
        filename (str): pymatgen compatible filename to read in
        rcut (float): cut-off radius for crystal site neighbour set-up

    Returns:
        nodes (set(Nodes)): set of unit-cell nodes of structure
        halo  (set(Nodes)): set of halo image nodes of structure
  
    """ 
    
    nodes = []

    for i,site  in enumerate(structure.sites):

        node_neighbours_ind = {n[:][2] for n in structure.get_neighbors(site, rcut, include_index = True)}
        nodes.append(Node(index = i, element = site.species_string, labels = site.species_string, neighbours_ind = node_neighbours_ind))

        
    for node in nodes:
       node.neighbours = set()
       for neighbour_ind in node.neighbours_ind:
           node.neighbours.add(nodes[neighbour_ind])

    
    return set(nodes)


def set_cluster_periodic(clusters, structure, rcut):

    for cluster in clusters:

      species = [structure.sites[node.index].species_string for node in cluster.nodes]
      coords = [structure.sites[node.index].coords for node in cluster.nodes]

      for axis in range(3):
          halo = Structure(structure.lattice,species,coords,coords_are_cartesian=True)
          super_scale = [1,1,1]
          super_scale[axis]+=1
          halo.make_supercell(super_scale)

          halo_nodes = nodes_from_structure (halo, rcut)
          temp_clusters = set()

          while halo_nodes:
             temp_cluster = Cluster({halo_nodes.pop()})
             temp_cluster.grow_cluster()
             halo_nodes.difference_update(temp_cluster.nodes)
             temp_clusters.add(temp_cluster)

          if len(temp_clusters) > 1:
             
             cluster.periodic[axis] = False
          else:
             cluster.periodic[axis] = True


def clusters_from_file(filename, rcut):
    
    structure = Structure.from_file(filename)
    
    nodes = nodes_from_structure( structure, rcut)
    
    clusters = set()

    while nodes:
         cluster = Cluster({nodes.pop()})
         cluster.grow_cluster()
         nodes.difference_update(cluster.nodes)
         clusters.add(cluster)

    set_cluster_periodic(clusters, structure, rcut)

    for cluster in clusters:
       print(cluster.periodic)

    return clusters
