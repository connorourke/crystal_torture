import unittest
from crystal_torture import Site

class SiteTestCase( unittest.TestCase ):
    """Test for Site Class"""
  
    def setUp( self ):
        self.index = 1
        self.element = 'Mg'
        self.labels = {1:"A",2:str(self.index)}
        self.site = Site( self.index, self.element, self.labels)

    def test_site_is_initialised( self ):
        self.assertEqual( self.site.index,self.index )
        self.assertEqual( self.site.element,self.element )
        self.assertEqual( self.site.labels,self.labels)



if __name__ =='__main__':
    unittest.main()
