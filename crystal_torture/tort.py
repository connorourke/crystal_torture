from crystal_torture import _tort
import f90wrap.runtime
import logging

class Tort_Mod(f90wrap.runtime.FortranModule):
    """
    Module tort_mod
    
    
    Defined at tort.f90 lines 1-80
    
    """
    class Test_Node(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=test_node)
        
        
        Defined at tort.f90 lines 7-10
        
        """
        def __init__(self, handle=None):
            """
            self = Test_Node()
            
            
            Defined at tort.f90 lines 7-10
            
            
            Returns
            -------
            this : Test_Node
            	Object to be constructed
            
            
            Automatically generated constructor for test_node
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            self._handle = _tort.f90wrap_test_node_initialise()
        
        def __del__(self):
            """
            Destructor for class Test_Node
            
            
            Defined at tort.f90 lines 7-10
            
            Parameters
            ----------
            this : Test_Node
            	Object to be destructed
            
            
            Automatically generated destructor for test_node
            """
            if self._alloc:
                _tort.f90wrap_test_node_finalise(this=self._handle)
        
        @property
        def neigh_ind(self):
            """
            Element neigh_ind ftype=integer pytype=int
            
            
            Defined at tort.f90 line 9
            
            """
            array_ndim, array_type, array_shape, array_handle = \
                _tort.f90wrap_test_node__array__neigh_ind(self._handle)
            if array_handle in self._arrays:
                neigh_ind = self._arrays[array_handle]
            else:
                neigh_ind = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                        self._handle,
                                        _tort.f90wrap_test_node__array__neigh_ind)
                self._arrays[array_handle] = neigh_ind
            return neigh_ind
        
        @neigh_ind.setter
        def neigh_ind(self, neigh_ind):
            self.neigh_ind[...] = neigh_ind
        
        def __str__(self):
            ret = ['<test_node>{\n']
            ret.append('    neigh_ind : ')
            ret.append(repr(self.neigh_ind))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    @staticmethod
    def set_nodes(n, indices):
        """
        set_nodes(n, indices)
        
        
        Defined at tort.f90 lines 19-33
        
        Parameters
        ----------
        n : int
        indices : int array
        
        """
        _tort.f90wrap_set_nodes(n=n, indices=indices)
    
    @staticmethod
    def set_neighbours(ind, n, neigh):
        """
        set_neighbours(ind, n, neigh)
        
        
        Defined at tort.f90 lines 35-49
        
        Parameters
        ----------
        ind : int
        n : int
        neigh : int array
        
        """
        _tort.f90wrap_set_neighbours(ind=ind, n=n, neigh=neigh)
    
    @staticmethod
    def torture(n):
        """
        torture(n)
        
        
        Defined at tort.f90 lines 51-80
        
        Parameters
        ----------
        n : int
        
        """
        _tort.f90wrap_torture(n=n)
    
    _dt_array_initialisers = []
    

tort_mod = Tort_Mod()

