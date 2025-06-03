import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from crystal_torture.pymatgen_interface import (
    nodes_from_structure,
    clusters_from_file,
    graph_from_file,
)
from crystal_torture import Cluster, Node, tort, Graph
from crystal_torture.cluster import clusters_from_nodes
from ddt import ddt, data, unpack
# from crystal_torture.cluster import Cluster

# Get the directory containing this test file
TEST_DIR = Path(__file__).parent
STRUCTURE_FILES_DIR = TEST_DIR / "STRUCTURE_FILES"


@ddt
class ClusterTestCase(unittest.TestCase):
    """ Test for Cluster Class"""

    def setUp(self):

        self.labels = ["A", "B", "O", "A", "B", "O"]
        self.elements = ["Mg", "Al", "O", "Mg", "Al", "O"]
        self.node_ids = [0, 1, 2, 3, 4, 5]
        self.neighbours = [
            [1, 2, 3, 5],
            [0, 2, 4, 5],
            [1, 0, 4, 3],
            [0, 4, 5, 2],
            [1, 2, 3, 5],
            [4, 3, 0, 1],
        ]
        self.mock_nodes = [
            Mock(
                spec=Node,
                index=i,
                element=e,
                labels={"site label": l},
                neighbours_ind=n,
                neigbours=None,
            )
            for i, e, l, n in zip(
                self.node_ids, self.elements, self.labels, self.neighbours
            )
        ]

        for node in self.mock_nodes:
            node.neighbours = [self.mock_nodes[n] for n in node.neighbours_ind]
            node.neighbours = set(node.neighbours)

        self.cluster1 = Cluster(set(self.mock_nodes[0:4]))
        self.cluster2 = Cluster(set(self.mock_nodes[3:7]))

        self.mock_nodes = set(self.mock_nodes)
        self.cluster = Cluster(self.mock_nodes)

    def test_cluster_is_initialised(self):
        self.assertEqual(self.cluster.nodes, self.mock_nodes)

    def test_merge_cluster(self):
        combined_cluster = self.cluster1.merge(self.cluster2)
        self.assertEqual(combined_cluster.nodes, self.mock_nodes)

    def test_is_neighbour(self):
        self.assertTrue(self.cluster1.is_neighbour(self.cluster2))

    def test_grow_cluster(self):

        self.cluster1.grow_cluster()
        self.assertEqual(self.cluster1.nodes, self.cluster.nodes)
        
    def test_uc_indices_with_valid_indices(self):
        """Test uc_indices works correctly when all nodes have valid uc_index."""
        node1 = Mock(spec=Node)
        node1.uc_index = 0
        node2 = Mock(spec=Node)  
        node2.uc_index = 1
        node3 = Mock(spec=Node)
        node3.uc_index = 0  # Duplicate uc_index
        
        cluster = Cluster({node1, node2, node3})
        result = cluster.uc_indices
        
        self.assertEqual(result, {0, 1})

    @data("POSCAR_2_clusters.vasp")
    def test_torture_cluster(self, value):
        cluster = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / value), rcut=4.0, elements={"Li"}
        )
        clusterf = cluster.pop()
        clusterf.grow_cluster()
        clusterf.torture_fort()
        tort.tort_mod.tear_down()

        self.assertEqual(
            set(
                [
                    node.tortuosity
                    for node in clusterf.uc_nodes
                ]
            ),
            set([4, 3, 3, 3, 3, 3, 3, 3]),
        )

    @data("POSCAR_2_clusters.vasp")
    def test_minimal_cluster(self, value):

        graph = graph_from_file(
            filename=str(STRUCTURE_FILES_DIR / value), rcut=4.0, elements={"Li"}
        )

        cluster = clusters_from_file(
            filename=str(STRUCTURE_FILES_DIR / value), rcut=4.0, elements={"Li"}
        )
        clusterf = cluster.pop()
        clusterf.grow_cluster()
        clusterf.torture_fort()
        graph.torture()

        self.assertEqual(
            set([c.tortuosity for c in graph.minimal_clusters]),
            set([c.tortuosity for c in list(graph.clusters)]),
        )

    @data("POSCAR_2_clusters.vasp")
    def test_py_equals_fort(self, value):
        graph_p = graph_from_file(
            filename=str(STRUCTURE_FILES_DIR / value), rcut=4.0, elements={"Li"}
        )
        graph_p.torture_py()

        graph_f = graph_from_file(
            filename=str(STRUCTURE_FILES_DIR / value), rcut=4.0, elements={"Li"}
        )
        graph_f.torture()

        self.assertEqual(
            [c.tortuosity for c in list(graph_p.clusters)],
            [c.tortuosity for c in list(graph_f.clusters)],
        )
        
    def test_torture_fort_without_allocation_raises_error(self):
        """Test that torture_fort raises error when Fortran module not allocated."""
        
        node0 = Mock(index=0, uc_index=0, neighbours_ind=[1])
        node1 = Mock(index=1, uc_index=0, neighbours_ind=[0])
        
        cluster = Cluster({node0, node1})
        
        # Ensure clean state
        tort.tort_mod.tear_down()
        
        # Call the actual torture_fort method (bind it to our mock)
        with patch('crystal_torture.tort.tort_mod.torture') as mock_torture:
            with self.assertRaises(RuntimeError) as context:
                cluster.torture_fort()
                
    def test_clusters_from_nodes_single_connected_component(self):
        """Test clusters_from_nodes with all nodes in one connected component."""
        # Create 3 connected UC nodes using new API
        node0 = Node(0, "Li", uc_index=0, is_halo=False, neighbours_ind={1, 2})
        node1 = Node(1, "Li", uc_index=1, is_halo=False, neighbours_ind={0, 2}) 
        node2 = Node(2, "Li", uc_index=2, is_halo=False, neighbours_ind={0, 1})
        
        # Set up neighbour relationships
        nodes = [node0, node1, node2]
        for node in nodes:
            node.neighbours = {n for n in nodes if n.index in node.neighbours_ind}
        
        clusters = clusters_from_nodes(set(nodes))
        
        # Should get exactly one cluster containing all nodes
        self.assertEqual(len(clusters), 1)
        cluster = clusters.pop()
        self.assertEqual(len(cluster.nodes), 3)
    
    def test_clusters_from_nodes_multiple_disconnected_components(self):
        """Test clusters_from_nodes with multiple disconnected components."""
        # Create two disconnected pairs using new API
        node0 = Node(0, "Li", uc_index=0, is_halo=False, neighbours_ind={1})
        node1 = Node(1, "Li", uc_index=0, is_halo=True, neighbours_ind={0})
        node2 = Node(2, "Li", uc_index=1, is_halo=False, neighbours_ind={3})
        node3 = Node(3, "Li", uc_index=1, is_halo=True, neighbours_ind={2})
        
        # Set up neighbour relationships
        node0.neighbours = {node1}
        node1.neighbours = {node0}
        node2.neighbours = {node3}
        node3.neighbours = {node2}
        
        clusters = clusters_from_nodes({node0, node1, node2, node3})
        
        # Should get two clusters
        self.assertEqual(len(clusters), 2)
        cluster_sizes = {len(cluster.nodes) for cluster in clusters}
        self.assertEqual(cluster_sizes, {2})  # Both clusters have 2 nodes
    
    def test_clusters_from_nodes_single_isolated_node(self):
        """Test clusters_from_nodes with single isolated UC node."""
        node0 = Node(0, "Li", uc_index=0, is_halo=False, neighbours_ind=set())
        node0.neighbours = set()
        
        clusters = clusters_from_nodes({node0})
        
        # Should get one cluster with one node
        self.assertEqual(len(clusters), 1)
        cluster = clusters.pop()
        self.assertEqual(len(cluster.nodes), 1)
        self.assertEqual(cluster.nodes.pop(), node0)
    
    def test_clusters_from_nodes_mixed_halo_uc_nodes(self):
        """Test that only UC nodes seed clusters but halo nodes join them."""
        # UC node connected to halo node using new API
        uc_node = Node(0, "Li", uc_index=0, is_halo=False, neighbours_ind={1})
        halo_node = Node(1, "Li", uc_index=0, is_halo=True, neighbours_ind={0})
        
        uc_node.neighbours = {halo_node}
        halo_node.neighbours = {uc_node}
        
        clusters = clusters_from_nodes({uc_node, halo_node})
        
        # Should get one cluster containing both nodes (seeded by UC node)
        self.assertEqual(len(clusters), 1)
        cluster = clusters.pop()
        self.assertEqual(cluster.nodes, {uc_node, halo_node})
    
    def test_clusters_from_nodes_empty_set(self):
        """Test clusters_from_nodes with empty node set."""
        clusters = clusters_from_nodes(set())
        
        # Should return empty set
        self.assertEqual(clusters, set())
    
    def test_clusters_from_nodes_only_halo_nodes(self):
        """Test clusters_from_nodes with only halo nodes (no seeds)."""
        halo1 = Node(0, "Li", uc_index=0, is_halo=True, neighbours_ind={1})
        halo2 = Node(1, "Li", uc_index=0, is_halo=True, neighbours_ind={0})
        
        halo1.neighbours = {halo2}
        halo2.neighbours = {halo1}
        
        clusters = clusters_from_nodes({halo1, halo2})
        
        # Should return empty set (no UC nodes to seed clusters)
        self.assertEqual(clusters, set())
        
    def test_cluster_set_periodic_3d(self):
        """Test set_periodic identifies 3D periodic cluster (27 images)."""
        # Create 27 nodes with same uc_index (simulating 3x3x3 periodic images)
        nodes = set()
        for i in range(27):
            node = Node(i, "Li", uc_index=0, is_halo=(i != 13), neighbours_ind=set())
            nodes.add(node)
        
        cluster = Cluster(nodes)
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 3)
    
    def test_cluster_set_periodic_2d(self):
        """Test set_periodic identifies 2D periodic cluster (9 images)."""
        # Create 9 nodes with same uc_index (simulating 3x3 periodic images)
        nodes = set()
        for i in range(9):
            node = Node(i, "Li", uc_index=0, is_halo=(i != 4), neighbours_ind=set())
            nodes.add(node)
        
        cluster = Cluster(nodes)
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 2)
    
    def test_cluster_set_periodic_1d(self):
        """Test set_periodic identifies 1D periodic cluster (3 images)."""
        # Create 3 nodes with same uc_index (simulating linear periodic images)
        nodes = set()
        for i in range(3):
            node = Node(i, "Li", uc_index=0, is_halo=(i != 1), neighbours_ind=set())
            nodes.add(node)
        
        cluster = Cluster(nodes)
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 1)
    
    def test_cluster_set_periodic_0d_single_node(self):
        """Test set_periodic identifies isolated cluster (1 node)."""
        node = Node(0, "Li", uc_index=0, is_halo=False, neighbours_ind=set())
        cluster = Cluster({node})
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 0)
    
    def test_cluster_set_periodic_0d_multiple_nodes(self):
        """Test set_periodic identifies isolated cluster (multiple nodes, but not 3/9/27)."""
        # Create 5 nodes with same uc_index (doesn't match any periodic pattern)
        nodes = set()
        for i in range(5):
            node = Node(i, "Li", uc_index=0, is_halo=False, neighbours_ind=set())
            nodes.add(node)
        
        cluster = Cluster(nodes)
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 0)
    
    def test_cluster_set_periodic_empty_cluster(self):
        """Test set_periodic handles empty cluster."""
        cluster = Cluster(set())
        cluster.set_periodic()
        
        self.assertEqual(cluster.periodic, 0)
        
    def test_return_index_node_found(self):
        """Test return_index_node returns correct node when index exists."""
        node1 = Mock(spec=Node)
        node1.index = 5
        node2 = Mock(spec=Node)
        node2.index = 10
        node3 = Mock(spec=Node)
        node3.index = 15
        
        cluster = Cluster({node1, node2, node3})
        result = cluster.return_index_node(10)
        
        self.assertEqual(result, node2)
    
    def test_return_index_node_not_found_raises_error(self):
        """Test return_index_node raises ValueError when index doesn't exist."""
        node1 = Mock(spec=Node)
        node1.index = 5
        node2 = Mock(spec=Node)
        node2.index = 10
        
        cluster = Cluster({node1, node2})
        
        with self.assertRaises(ValueError) as context:
            cluster.return_index_node(99)
        
        self.assertIn("No node found with index 99", str(context.exception))
    
    def test_return_index_node_empty_cluster_raises_error(self):
        """Test return_index_node raises ValueError when cluster is empty."""
        cluster = Cluster(set())
        
        with self.assertRaises(ValueError) as context:
            cluster.return_index_node(1)
        
        self.assertIn("No node found with index 1", str(context.exception))
        
    def test_uc_nodes_property(self):
        """Test uc_nodes property returns only UC nodes."""
        uc_node1 = Mock(spec=Node)
        uc_node1.is_halo = False
        uc_node2 = Mock(spec=Node) 
        uc_node2.is_halo = False
        halo_node = Mock(spec=Node)
        halo_node.is_halo = True
        
        cluster = Cluster({uc_node1, uc_node2, halo_node})
        result = cluster.uc_nodes
        
        self.assertEqual(result, {uc_node1, uc_node2})
    
    def test_halo_nodes_property(self):
        """Test halo_nodes property returns only halo nodes."""
        uc_node = Mock(spec=Node)
        uc_node.is_halo = False
        halo_node1 = Mock(spec=Node)
        halo_node1.is_halo = True
        halo_node2 = Mock(spec=Node)
        halo_node2.is_halo = True
        
        cluster = Cluster({uc_node, halo_node1, halo_node2})
        result = cluster.halo_nodes
        
        self.assertEqual(result, {halo_node1, halo_node2})


if __name__ == "__main__":
    unittest.main()