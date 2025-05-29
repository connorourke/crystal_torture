"""Cluster class for representing groups of connected nodes within a graph."""

from crystal_torture.node import Node
import copy
import sys
from queue import Queue
from threading import Thread
import numpy as np
from types import ModuleType
from typing import cast

# Module variable with proper type hint
tort: ModuleType | None

try:
    from . import tort
except ImportError:
    tort = None


class Cluster:
    """Cluster class: group of connected nodes within graph."""

    def __init__(self,
        nodes: set[Node]) -> None:
        """Initialise a cluster.

        Args:
            nodes: Set of nodes in the cluster.
        """
        self.nodes = nodes
        self.periodic: int | None = None
        self.tortuosity: float | None = None

    def merge(self, other_cluster: 'Cluster') -> 'Cluster':
        """Merge two clusters into one.
 
        Args:
            other_cluster: Cluster to be joined.
            
        Returns:
            New cluster containing nodes from both clusters.
        """
        new_cluster = Cluster(self.nodes | other_cluster.nodes)
        return new_cluster

    def is_neighbour(self, other_cluster: 'Cluster') -> bool:
        """Check if one cluster of nodes is connected to another.
        
        Args:
            other_cluster: Cluster to check for connection.
            
        Returns:
            True if clusters share any nodes, False otherwise.
        """
        return bool(self.nodes & other_cluster.nodes)

    def grow_cluster(self, key: str | None = None, value: str | None = None) -> None:
        """Grow cluster by adding neighbours.
 
        Args:
            key: Label key to selectively choose nodes in cluster.
            value: Value for label to selectively choose nodes in cluster.
        """
        nodes_to_visit = set([self.nodes.pop()])

        visited: set[Node] = set()
        add = visited.add

        if key:
            while nodes_to_visit:
                node = nodes_to_visit.pop()
                if node.neighbours is not None:
                    nodes_to_visit = nodes_to_visit.union(
                        set(
                            [
                                neigh
                                for neigh in node.neighbours
                                if (neigh not in visited and neigh.labels[key] == value)
                            ]
                        )
                    )
                add(node)
        else:
            while nodes_to_visit:
                node = nodes_to_visit.pop()
                if node.neighbours is not None:
                    nodes_to_visit = nodes_to_visit.union(
                        set([neigh for neigh in node.neighbours if neigh not in visited])
                    )
                add(node)

        self.nodes = visited

    def return_key_nodes(self, key: str, value: str | bool) -> set[Node]:
        """Return the nodes in a cluster corresponding to a particular label.

        Args:
           key: Dictionary key for filtering nodes.
           value: Value held in dictionary for label key.

        Returns:
           Set of nodes in cluster for which (node.labels[key] == value).
        """
        key_nodes = set([node for node in self.nodes if node.labels[key] == value])
        return key_nodes

    def return_uc_indices(self) -> set[str]:
        """Return the unit-cell indices of nodes in a cluster.
        
        Reduces the full list of uc_indices included in the unit-cell and the halo 
        to contain the indices only once.

        Returns:
            Set of unit-cell indices for nodes in cluster.
        """
        uc_indices = set([cast(str, node.labels["UC_index"]) for node in self.nodes])
        return uc_indices

    def return_index_node(self, index: int) -> Node:
        """Return the node with the specified index.
        
        Args:
            index: Index of the node to return.
            
        Returns:
            Node with the specified index.
        """
        index_node = [node for node in self.nodes if node.index == index]
        return index_node[0]

    def torture_py(self) -> None:
        """Perform tortuosity analysis on nodes in cluster in pure Python using BFS.
        
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.

        Sets:
           node.tortuosity: Tortuosity for each node.
           self.tortuosity: Average tortuosity for cluster.
        """
        uc = self.return_key_nodes(key="Halo", value=False)
        while uc:

            node_stack = [uc.pop()]

            visited = set()
            uc_index = node_stack[0].labels["UC_index"]
            index = node_stack[0].index
            root_node = node_stack[0]

            for node in self.nodes:
                node.dist = 0

            while node_stack:

                node = node_stack.pop(0)
                next_dist = node.dist + 1
                if node not in visited:

                    if node.neighbours is not None:
                        for neigh in node.neighbours:
                            if neigh.dist == 0:
                                neigh.dist = next_dist
                                node_stack.append(neigh)
                if (node.labels["UC_index"] == uc_index) and (node.index != index):
                    root_node.tortuosity = next_dist - 1
                    break
                visited.add(node)

        uc_nodes = self.return_key_nodes(key="Halo", value=False)
        valid_tortuosities = [node.tortuosity for node in uc_nodes if node.tortuosity is not None]
        self.tortuosity = sum(valid_tortuosities) / len(valid_tortuosities) if valid_tortuosities else 0.0

    def torture_fort(self) -> None:
        """Perform tortuosity analysis on nodes in cluster using BFS in Fortran90 and OpenMP.
        
        Significantly faster than the python version above for large systems.
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.
        
        Sets:
        node.tortuosity: Tortuosity for each node.
        self.tortuosity: Average tortuosity for cluster.
        
        Raises:
            ImportError: If Fortran extensions are not available.
        """
        if tort is None or tort.tort_mod is None:
            raise ImportError("Fortran extensions not available. Use torture_py() instead.")
        
        # Set up Fortran module with node data
        all_nodes = list(self.nodes)
        uc_node_indices = [node.index for node in self.return_key_nodes(key="Halo", value=False)]
        
        # Allocate Fortran arrays
        tort.tort_mod.allocate_nodes(len(all_nodes), len(uc_node_indices))
        
        # Set up each node's data in Fortran module
        for node in all_nodes:
            neigh_indices = list(node.neighbours_ind)
            tort.tort_mod.set_neighbours(
                node.index,
                int(node.labels["UC_index"]),
                len(neigh_indices),
                neigh_indices
            )
        
        # Now run the torture algorithm
        tort.tort_mod.torture(len(uc_node_indices), uc_node_indices)
        
        for node in self.return_key_nodes(key="Halo", value=False):
            node.tortuosity = tort.tort_mod.uc_tort[int(node.labels["UC_index"])]
        
        uc_nodes = self.return_key_nodes(key="Halo", value=False)
        valid_tortuosities = [node.tortuosity for node in uc_nodes if node.tortuosity is not None]
        self.tortuosity = sum(valid_tortuosities) / len(valid_tortuosities) if valid_tortuosities else 0.0