from crystal_torture.node import  Node
import copy
import sys
#import pathos.multiprocessing as mp
from queue import Queue
from crystal_torture import tort
from threading import Thread
import numpy as np

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
        self.periodic = None
        self.tortuosity = None 

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

        nodes_to_visit = set([ self.nodes.pop() ])

        
        visited = set()      
        add = visited.add        
 
        if key:
           
           while nodes_to_visit:
               node = nodes_to_visit.pop()
               nodes_to_visit = nodes_to_visit.union(set([ neigh for neigh in node.neighbours if (neigh not in visited and neigh.labels[key]==value)]))

               add(node)
        else:
           while nodes_to_visit:
               node = nodes_to_visit.pop()
               nodes_to_visit = nodes_to_visit.union(set([ neigh for neigh in node.neighbours if neigh not in visited]))
               add(node)

        self.nodes = visited


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
            
    def return_uc_indices(self):
        """
        Returns the unit-cell indices of nodes in a cluster (i.e. reduces the full list of uc_indices
        included in the unit-cell and the halo to contain the indices only once)

        Args: None

        Returns:
            uc_nodes (set(Int)): set of unit-cell indices for nodes in cluster

        """


        uc_indices = set([node.labels["UC_index"] for node in self.nodes])

        return uc_indices


    def return_index_node(self,index):
       
        index_node = [node for node in self.nodes if node.index == index]

        return index_node[0]


    def torture_py(self):
        '''
        Performs tortuosity analysis on nodes in cluster in pure python using a BFS:
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.

        Args:
           None

        Returns:
           None
        
        Sets:
           node.tortuosity (int): tortuosity for node
           self.tortuosity (int): average tortuosity for cluster

        

        '''

        uc = self.return_key_nodes(key="Halo",value=False)
        while uc:

            
           node_stack = [uc.pop()]
           
           visited = set()
           uc_index = node_stack[0].labels["UC_index"]
           index = node_stack[0].index
           root_node = node_stack[0]

           for node in self.nodes:
               node.dist = 0

           while node_stack:
 
             
              node=node_stack.pop(0)
              next_dist = node.dist + 1
              if node not in visited:
                
                 for neigh in node.neighbours:
                     if neigh.dist == 0:
                        neigh.dist = next_dist 
                        node_stack.append(neigh)
              if (node.labels["UC_index"] == uc_index) and (node.index != index):
                 root_node.tortuosity = next_dist-1
                 break
              visited.add(node)
        
        self.tortuosity = sum([node.tortuosity for node in self.return_key_nodes(key="Halo",value=False)])/len(self.return_key_nodes(key="Halo",value=False)
)


    def torture_fort(self):
        '''
        Performs tortuosity analysis on nodes in cluster using BFS in Fortran90 and OpenMP:
        Significantly faster than the python version above for large systems.
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.

        Args:
           None

        Returns:
           None
        
        Sets:
           node.tortuosity (int): tortuosity for node
           self.tortuosity (int): average tortuosity for cluster


        '''

       

        uc_nodes = [node.index for node in self.return_key_nodes(key="Halo",value=False)]
        tort.tort_mod.torture(len(uc_nodes),uc_nodes)

        for node in self.return_key_nodes(key="Halo",value=False):
            node.tortuosity = tort.tort_mod.uc_tort[int(node.labels["UC_index"])]

        self.tortuosity = sum([node.tortuosity for node in self.return_key_nodes(key="Halo",value=False)])/len(uc_nodes)

