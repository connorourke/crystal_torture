from crystal_torture.node import  Node
import copy
import sys

class Cluster:
    """
    Cluster class: group of connected nodes within graph
    """

    def __init__(self,nodes):
        """
        Initialise a cluster.

        Args:
            nodes (set(Node)): set of nodes in the cluster.
        """

        self.nodes = nodes
        self.periodic = [False, False, False]

    def merge(self, other_cluster):
        """
        Merge two clusters into one
 
        Args:
            other_cluster (Cluster): cluster to be joined
        """
        
        new_cluster =  Cluster(self.nodes|other_cluster.nodes )
        
        return new_cluster

    def is_neighbour(self, other_cluster):
        """
        Check if one cluster of nodes is connected to another
        """

        return bool( self.nodes & other_cluster.nodes ) 

    def grow_cluster(self,key=None,value=None):
        """
        Grow cluster by adding neighbours
 
        Args:
            key (str): label key to selectively choose nodes in cluster
            value : value for label to selectively choose nodes in cluster
        """

        nodes_to_visit = [ self.nodes.pop() ]

        
        visited = set()      
        
        while nodes_to_visit:
            node = nodes_to_visit.pop(0)
            if key:
                  if node not in visited and node.labels[key]==value:
                     nodes_to_visit += [ node for node in node.neighbours ]
                     visited.add(node)   
            else:
              if node not in visited:
                 nodes_to_visit += [ node for node in node.neighbours ]
              visited.add(node)
        
        self.nodes = visited
        print("Nodes in cluster",len(self.nodes))


    def return_key_nodes(self,key,value):
        """
        Returns the nodes in a cluster corresponding to a particular label

        Args:
           key (str): Dictionary key for filtering nodes
           value    : value held in dictionary for label key

        Returns:
           key_nodes (set(Node)): set of nodes in cluster for which (node.labels[key] == value)
       
        """

        key_nodes=set([node for node in self.nodes if node.labels[key]==value])
 
        return key_nodes
            


    
    def torture(self):
        """
        Calculates the average tortuosity of the cluster
        """
        print("about to torture")
 
        uc = self.return_key_nodes(key="Halo",value=False)

        while uc:
           path_stack = [[uc.pop()]]
           index = path_stack[0][0].index
           steps = 0    
         
           visited = set()
           dist = [0]*len(self.nodes)        

           while path_stack:
           
               path = path_stack.pop(0)
               node = path[-1]
               next_dist = dist[node.index] + 1

               if node not in visited:
                  print("visiting node",node.index)
                  if int(node.labels["UC_index"]) == index and node.index != index:
                      for node in path:
                          if node.tortuosity == None:
                            # node.tortuosity = next_dist-1
                             for node in self.return_key_nodes(key="UC_index",value=index):
                                 node.tortuosity = next_dist-1

                          elif node.tortuosity != next_dist -1:
                             sys.exit("Error in torture. Calculated tortuosity doesn't match for node")
                      print("Path",[node.index for node in path],next_dist-1)

                      break 
            
                  for neighbour in node.neighbours:
                      if dist[neighbour.index] == 0:
                         dist[neighbour.index] = next_dist

                      new_path = list(path)
                      new_path.append(neighbour)
                      path_stack.append(new_path)
                  visited.add(node)

       
        for node in self.nodes:
            print("Tortuosity",node.index,node.tortuosity) 
              

#    def torture_multi(self):

#        pool_size

          



