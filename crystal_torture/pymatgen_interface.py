
from crystal_torture.node import Node
from crystal_torture.cluster import Cluster
from pymatgen import Structure

"Functions for setting up a node, cluster and graph using pymatgen"

def nodes_from_file(filename, rcut):
    """
    Takes a structure file and converts to Nodes for interogation

    Args:
        filename (str): name of pymatgen compatible file
        rcut (float): cut-off radius for crystal site neighbour set-up
    """ 
    
    structure = Structure.from_file(filename)
    nodes = []

    for i,site  in enumerate(structure.sites):

        node_neighbours_ind = [n[:][2] for n in structure.get_neighbors(site, rcut, include_index = True)]
        nodes.append(Node(index = i, element = site.species_string, labels = site.species_string, neighbours_ind = set(node_neighbours_ind)))

        
    for node in nodes:
       node.neighbours = set()
       for neighbour_ind in node.neighbours_ind:
           node.neighbours.add(nodes[neighbour_ind])

    return set(nodes)

