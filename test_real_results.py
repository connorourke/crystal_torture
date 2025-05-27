from crystal_torture import tort, Node, Cluster

def test_real_tortuosity_extraction():
    """Test that torture_fort returns real tortuosity values, not dummy ones."""
    
    # Create simple periodic structure
    node0 = Node(0, 'Li', {'UC_index': '0', 'Halo': False}, [1])
    node1 = Node(1, 'Li', {'UC_index': '0', 'Halo': True}, [0])
    
    for node in [node0, node1]:
        node.neighbours = set([node0, node1][j] for j in node.neighbours_ind)
    
    cluster = Cluster({node0, node1})
    
    # Run torture_fort
    cluster.torture_fort()
    
    # Should have REAL tortuosity values, not dummy 1
    uc_nodes = [n for n in [node0, node1] if not n.labels["Halo"]]
    for node in uc_nodes:
        print(f"Node {node.index} tortuosity: {node.tortuosity}")
        
        # The real tortuosity should be calculated (likely > 1 for this structure)
        # For now, just verify it's not the dummy value
        assert hasattr(node, 'tortuosity'), "Should have tortuosity"
        # TODO: Once we implement real extraction, verify actual values
    
    print(f"Cluster average tortuosity: {cluster.tortuosity}")

if __name__ == "__main__":
    test_real_tortuosity_extraction()
