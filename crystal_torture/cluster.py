from crystal_torture.node import  Node
import copy

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
        
     #   if not key:
         #  print("****************************** halo************")

        while nodes_to_visit:
            node = nodes_to_visit.pop(0)
            if key:

               if node.labels[key]==value:
              
                 # print("growing pains",key,node.labels,node.labels[key],value,node.labels[key]==value)
               
                  if node not in visited:# and node.labels[key]==value:
                     nodes_to_visit += [ node for node in node.neighbours ]
                    # print("Neighbours",node.neighbours)
                #     print([node.labels for node in node.neighbours])
                #     print("Adding",node.index)
                     visited.add(node)        
               #      print("Visited",[node.index for node in visited])     
            else:
              #print("growing pains","NO KEY",node.labels)
              if node not in visited:
                # print([node.labels for node in node.neighbours])
                 nodes_to_visit += [ node for node in node.neighbours ]
                # print("Adding",node.index)
                 visited.add(node)
                # print("Visited",[node.index for node in visited])

        
        self.nodes = visited
        print("Nodes in cluster",len(self.nodes))


    def return_key_nodes(self,key,value):

        key_nodes=set([node for node in self.nodes if node.labels[key]==value])
 
        return key_nodes
            


    def torture(self):
        """
        Calculates the average tortuosity of the graph
        """

        





