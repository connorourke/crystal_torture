"""Cluster class for representing groups of connected nodes within a graph."""
from __future__ import annotations

from crystal_torture.node import Node
from crystal_torture.exceptions import FortranNotAvailableError
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

    def merge(self, other_cluster: Cluster) -> Cluster:
        """Merge two clusters into one.
 
        Args:
            other_cluster: Cluster to be joined.
            
        Returns:
            New cluster containing nodes from both clusters.
        """
        new_cluster = Cluster(self.nodes | other_cluster.nodes)
        return new_cluster

    def is_neighbour(self, other_cluster: Cluster) -> bool:
        """Check if one cluster of nodes is connected to another.
        
        Args:
            other_cluster: Cluster to check for connection.
            
        Returns:
            True if clusters share any nodes, False otherwise.
        """
        return bool(self.nodes & other_cluster.nodes)

    def grow_cluster(self) -> None:
        """Grow cluster by adding all connected neighbours.
        
        Uses breadth-first search to find all nodes connected to the current cluster
        and adds them to the cluster. This expands the cluster to include the full
        connected component in the graph.
        """
        if not self.nodes:
            return
        
        # Start BFS from any node in the current cluster
        nodes_to_visit = {self.nodes.pop()}
        visited: set[Node] = set()
        
        while nodes_to_visit:
            current_node = nodes_to_visit.pop()
            
            if current_node not in visited:
                visited.add(current_node)
                
                # Add all unvisited neighbours to the queue
                if current_node.neighbours is not None:
                    unvisited_neighbours = current_node.neighbours - visited
                    nodes_to_visit.update(unvisited_neighbours)
        
        self.nodes = visited
        
    @property
    def uc_nodes(self) -> set[Node]:
        """Return unit cell nodes (is_halo=False)."""
        return {node for node in self.nodes if not node.is_halo}
    
    @property  
    def halo_nodes(self) -> set[Node]:
        """Return halo nodes (is_halo=True)."""
        return {node for node in self.nodes if node.is_halo}

    @property
    def uc_indices(self) -> set[int]:
        """Return the unit-cell indices of nodes in a cluster."""
        return {node.uc_index for node in self.nodes}

    def return_index_node(self, index: int) -> Node:
        """Return the node with the specified index.
        
        Args:
            index: Index of the node to return.
            
        Returns:
            Node with the specified index.
            
        Raises:
            ValueError: If no node with the specified index is found.
        """
        try:
            return next(node for node in self.nodes if node.index == index)
        except StopIteration:
            raise ValueError(f"No node found with index {index}")

    def torture_py(self) -> None:
        """Perform tortuosity analysis on nodes in cluster in pure Python using BFS.
        
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.
        
        Sets:
        node.tortuosity: Tortuosity for each node.
        self.tortuosity: Average tortuosity for cluster.
        """
        uc = self.uc_nodes
        while uc:
            node_stack = [uc.pop()]
            visited = set()
            uc_index = node_stack[0].uc_index
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
                if (node.uc_index == uc_index) and (node.index != index):  # Changed from labels["UC_index"]
                    root_node.tortuosity = next_dist - 1
                    break
                visited.add(node)
        
        uc_nodes = self.uc_nodes
        valid_tortuosities = [node.tortuosity for node in uc_nodes if node.tortuosity is not None]
        self.tortuosity = sum(valid_tortuosities) / len(valid_tortuosities) if valid_tortuosities else 0.0

    def torture_fort(self) -> None:
        """Perform tortuosity analysis on nodes in cluster using BFS in Fortran90 and OpenMP.
        
        Significantly faster than the Python version above for large systems.
        Calculates the integer number of node-node steps it requires to get from a 
        node to its periodic image.
        
        Sets:
        node.tortuosity: Tortuosity for each node.
        self.tortuosity: Average tortuosity for cluster.
        
        Raises:
            FortranNotAvailableError: If Fortran extensions are not available.
            RuntimeError: If Fortran nodes have not been allocated.
        """
        if tort is None or tort.tort_mod is None:
            raise FortranNotAvailableError()
        
        # Check if nodes are allocated
        if not tort.tort_mod._is_allocated:
            raise RuntimeError("Fortran nodes must be allocated before calling torture_fort. "
                            "Use graph_from_structure() or call set_fort_nodes() first.")
        
        # Get the UC node indices for this cluster
        uc_node_indices = [node.index for node in self.uc_nodes]
        
        # Run the torture algorithm
        tort.tort_mod.torture(len(uc_node_indices), uc_node_indices)
        
        # Get results
        for node in self.uc_nodes:
            node.tortuosity = tort.tort_mod.uc_tort[node.uc_index]
        
        uc_nodes = self.uc_nodes
        valid_tortuosities = [node.tortuosity for node in uc_nodes if node.tortuosity is not None]
        self.tortuosity = sum(valid_tortuosities) / len(valid_tortuosities) if valid_tortuosities else 0.0
        
    def set_periodic(self) -> None:
        """Set the periodicity of the cluster by counting UC nodes with same UC_index.
        
        Determines cluster periodicity by counting how many periodic images of the 
        same unit cell site are connected in the cluster.
        
        Sets:
            self.periodic: 0=isolated, 1=1D periodic, 2=2D periodic, 3=3D periodic
        """
        if not self.nodes:
            self.periodic = 0
            return
            
        # Get any node to find its UC_index
        node = next(iter(self.nodes))
        uc_index = node.uc_index
        
        # Count nodes with same UC_index
        no_images = len([n for n in self.nodes if n.uc_index == uc_index])
        
        if no_images == 27:
            self.periodic = 3
        elif no_images == 9:
            self.periodic = 2
        elif no_images == 3:
            self.periodic = 1
        else:
            self.periodic = 0
        
def clusters_from_nodes(nodes: set[Node]) -> set[Cluster]:
    """Create clusters from a set of nodes using connected components algorithm.
    
    Forms clusters by growing from unit cell nodes (is_halo=False) using graph 
    traversal to find all connected nodes. Each cluster represents one connected
    component in the node graph.
    
    Args:
        nodes: Set of Node objects with neighbour relationships established.
        
    Returns:
        Set of Cluster objects, each containing one connected component.
        
    Algorithm:
        1. Identify all unit cell nodes (is_halo=False) as potential seeds
        2. For each unprocessed UC node:
           - Create cluster with that node as seed
           - Use graph traversal to find all connected nodes
           - Calculate cluster periodicity
           - Add to results
    """
    
    if not nodes:
        return set()
    
    clusters = set()
    # Get all unit cell nodes (only these seed clusters)
    uc_nodes = set([node for node in nodes if node.is_halo == False])
    
    while uc_nodes:
        node = uc_nodes.pop()
        if not node.is_halo:  # Double-check (should always be true here)
            cluster = Cluster({node})
            cluster.grow_cluster()
            # Remove all nodes in this cluster from unprocessed set
            uc_nodes.difference_update(cluster.nodes)
            clusters.add(cluster)
            cluster.set_periodic()
    
    return clusters