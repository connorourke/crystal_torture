
from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from pymatgen import Structure
import copy

"Functions for setting up a node, cluster and graph using pymatgen"

def create_halo(structure):
    """
    Takes a pymatgen structure object, sets up a halo by making a 3x3x3 supercell,
    and reorders the structure to put original unit cell sites (now in centre of supercell) at
    start of the structure object.

    Args:
        structure (Structure): pymatgen Structure object
    Returns:
        None
    """

#    structure.add_site_property("UC_index", [str(i) for i in range(len(structure.sites))] )

    uc_index = [((site * 3**3 ) +13) for site in range(len(structure.sites))]
    uc_index.reverse()

    structure.make_supercell([3,3,3])

    structure_sorted=Structure(lattice=structure.lattice,species=[],coords=[])

    for site in uc_index:
       structure_sorted.sites.append(structure.sites[site])
       del structure.sites[site]

    structure_sorted.sites.reverse()

    for site in structure.sites:
        structure_sorted.sites.append(site)

    return structure_sorted

#    print("Structure inside",structure)

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
    nodes = []

    no_nodes = len(structure.sites)
    if get_halo == True:
       structure = create_halo(structure)

    for index,site  in enumerate(structure.sites):
        if index < no_nodes:
           halo_node = False
        else:
           halo_node = True

        node_neighbours_ind = {n[:][2] for n in structure.get_neighbors(site, rcut, include_index = True)}
        nodes.append(Node(index = index, element = site.species_string, labels = {"UC_index":site.properties["UC_index"], "Halo":halo_node} , neighbours_ind = node_neighbours_ind))
        
    for node in nodes:
       node.neighbours = set()
       for neighbour_ind in node.neighbours_ind:
           node.neighbours.add(nodes[neighbour_ind])
     
    for node in nodes:
       print(node.index, node.labels,node.neighbours_ind)

    return set(nodes)


def set_cluster_periodic(clusters, structure, rcut):

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


def clusters_from_file(filename, rcut):
    
    structure = Structure.from_file(filename)
    structure_temp = Structure.from_file(filename) 
     
    nodes = nodes_from_structure(structure, rcut, get_halo=True)
    clusters = set()
   
    while nodes:
         node=nodes.pop()
         
         if node.labels["Halo"]==False :
            cluster = Cluster({node})
            cluster.grow_cluster(key="Halo",value=False)
            nodes.difference_update(cluster.nodes)
            clusters.add(cluster)
   
    set_cluster_periodic(clusters, structure_temp, rcut)

    # add halo nodes to clusters
    for cluster in clusters:
        cluster.grow_cluster()
  

        print(cluster.periodic) 

    return clusters

