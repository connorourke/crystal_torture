#from crystal_torture.cluster import  Cluster
#from crystal_torture.pymatgen_interface import clusters_from_file
from pymatgen import Structure
from crystal_torture.minimal_cluster import minimal_Cluster
from crystal_torture import tort

class Graph:
    """
    Graph class: group of disconnected clusters making up full graph
    """

    def __init__(self, clusters, structure=None):
        """
        Initialise a graph. The graph is a 3x3x3 representation of the unit cell
        so there will the clusters within it which are not necessarily unique. 
        However only the unit cell nodes within each cluster are tortured, so there 
        is no repetition.

        Args:
            - clusters  (set(Clusters)): set of clusters in the graph
            - tortuosity (dict (node_index:tortuosity)): dict to hold the tortuosity for each node
            - self.minimal_clusters (list[minimal_Cluster]): list of minimal clusters for cluster output
            - self.structure (Structure): the pymatgen Structure object the graph has been formed from

        """
        
        self.clusters = clusters

        self.tortuosity = None
        self.minimal_clusters = None 
        self.structure = structure

    def set_site_tortuosity(self):
        """
        Sets a dict containing the site by site tortuosity for sites in the graph unit cell
        """

        tortuosity={}
        for cluster in self.clusters:
            for node in cluster.return_key_nodes(key="Halo",value=False):
                tortuosity[str(node.labels["UC_index"])]=node.tortuosity

        self.tortuosity =  tortuosity

    def set_minimal_clusters(self):
        """
        Access to the information on unique unit cell clusters. Cycles through the halo clusters,
        gets a set unique cluster sites and sets up minimal_Cluster object to store and access the data

        Args:
            - None

        Output:
            - self.unit_clusters (set(minimal_Cluster)): a set of minimal_Cluster objects for unit cell in graph
             
        
        """
        site_sets=[] 
        for cluster in self.clusters:
             indices = frozenset([int(node.labels["UC_index"]) for node in cluster.nodes])
             site_sets.append(indices)

        site_sets = set(site_sets)
        
        self.minimal_clusters = []

        for sites in site_sets:
            self.minimal_clusters.append(minimal_Cluster(site_indices = list(sites), size = len(sites)))
        

        for cluster in self.clusters:
           for min_clus in self.minimal_clusters:
               if min_clus.site_indices[0] in set([int(node.labels["UC_index"]) for node in cluster.nodes]):
                  min_clus.periodic = cluster.periodic

        for min_clus in self.minimal_clusters:
            if min_clus.periodic > 0:
               min_clus.tortuosity = 0
               for site in min_clus.site_indices:
                   min_clus.tortuosity+=self.tortuosity[str(site)]
               min_clus.tortuosity = min_clus.tortuosity / min_clus.size


    def torture(self):
        """
        Torture the graph and set node tortuosity for UC nodes in cluster.
        This only tortures UC nodes in each cluster, but the graph contains
        a halo of clusters. 

        Args:
            - none
   
        """       
        for cluster in self.clusters:
            if cluster.periodic > 0:
               cluster.torture_fort()

        self.set_site_tortuosity()
        self.set_minimal_clusters()

    def torture_py(self):
        """
        Torture the graph and set node tortuosity for UC nodes in cluster.
        This only tortures UC nodes in each cluster, but the graph contains
        a halo of clusters.

        Args:
            - none

        """
        for cluster in self.clusters:
            if cluster.periodic > 0:
               cluster.torture_py()

        self.set_site_tortuosity()
        self.set_minimal_clusters()


    def output_clusters(self,fmt,periodic=None):
        """
        Outputs the unique unit cell clusters from the graph

        Args:
        fmt (str): output format for pymatgen structures set up from clusters
        periodic (Boolean): Whether to output only periodic clusters

        Outputs:
        CLUS_*."fmt": A cluster structure file for each cluster in the graph
        """   


        if fmt == 'poscar':
           tail = 'vasp'
        else:
           tail = fmt


        site_sets = []

        for cluster in self.clusters:
           if periodic:
              if cluster.periodic > 0:
                 site_sets.append(frozenset([int(node.labels["UC_index"]) for node in cluster.nodes]))
           else:
              site_sets.append(frozenset([int(node.labels["UC_index"]) for node in cluster.nodes]))

        site_sets = set(site_sets)

        for index,site_list in enumerate(site_sets):
            cluster_structure = Structure(lattice=self.structure.lattice,species=[],coords=[])
            symbols = [species for species in self.structure.symbol_set]
            if "X" in set(symbols):
                symbols.remove("X")
                symbols.append("X0+")
            for symbol in symbols:
                for site in site_list:
                    
                    site=self.structure.sites[site]
                
                    if site.species_string == symbol:
                       cluster_structure.append(symbol,site.coords,coords_are_cartesian=True)
          
            cluster_structure.to(fmt=fmt,filename="CLUS_"+str(index)+"."+tail)

    def return_frac_percolating(self):
        """
        Calculates the fraction of nodes in the graph that are in a periodic cluster

        Args:
            - None
        Returns:
            - frac(real): nodes in graph in periodic clusers / total number of nodes
        """
         
        total_nodes = 0
        periodic_nodes = 0 

        for cluster in self.clusters:
             
            total_nodes += len(cluster.return_key_nodes(key='Halo',value=False))
            
            if cluster.periodic > 0:
               periodic_nodes += len(cluster.return_key_nodes(key='Halo',value=False))

        return periodic_nodes/total_nodes

