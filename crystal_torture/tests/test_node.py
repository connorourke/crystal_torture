import unittest
from crystal_torture import Node

class NodeTestCase( unittest.TestCase ):
    """Test for Site Class"""
  
    def setUp( self ):
        self.index = 1
        self.element = 'Mg'
        self.labels = {1:"A",2:str(self.index)}
        self.neighbours_ind = [1,2,9,10]
        self.node = Node( self.index, self.element, self.labels, self.neighbours_ind)

    def test_node_is_initialised( self ):
        self.assertEqual( self.node.index,self.index )
        self.assertEqual( self.node.element,self.element )
        self.assertEqual( self.node.labels,self.labels)
        self.assertEqual( self.node.neighbours_ind, self.neighbours_ind)

         
        
    

if __name__ =='__main__':
    unittest.main()
