#from crystal_torture.node import  Node
#import copy
#import sys
#import pathos.multiprocessing as mp
#from queue import Queue
#from crystal_torture import tort
#from threading import Thread
#import numpy as np

class minimal_Cluster:
    """
    minimal_Cluster class: minimal cluster object for returning tortuosity data from graph
    """

    def __init__(self,site_indices,size):
        """
        Initialise a minimal cluster.

        Args:
            - site_indices ((int)): set of site indices in the cluster.
            - periodicity (int): degree of periodicity in cluster
            - tortuosity (real): average tortuosity of cluster
            
        """

        self.site_indices = site_indices
        self.periodic = None
        self.tortuosity = None 
        self.size = size
