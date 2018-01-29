from crystal_torture import _tort
import f90wrap.runtime
import logging

class Tort_Mod(f90wrap.runtime.FortranModule):
    """
    Module tort_mod
    
    
    Defined at tort.f90 lines 1-143
    
    """
    class Test_Node(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=test_node)
        
        
        Defined at tort.f90 lines 5-9
        
        """
        def __init__(self, handle=None):
            """
            self = Test_Node()
            
            
            Defined at tort.f90 lines 5-9
            
            
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
            
            
            Defined at tort.f90 lines 5-9
            
            Parameters
            ----------
            this : Test_Node
            	Object to be destructed
            
            
            Automatically generated destructor for test_node
            """
            if self._alloc:
                _tort.f90wrap_test_node_finalise(this=self._handle)
        
        @property
        def node_index(self):
            """
            Element node_index ftype=integer pytype=int
            
            
            Defined at tort.f90 line 6
            
            """
            return _tort.f90wrap_test_node__get__node_index(self._handle)
        
        @node_index.setter
        def node_index(self, node_index):
            _tort.f90wrap_test_node__set__node_index(self._handle, node_index)
        
        @property
        def neigh_ind(self):
            """
            Element neigh_ind ftype=integer pytype=int
            
            
            Defined at tort.f90 line 7
            
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
            ret.append('    node_index : ')
            ret.append(repr(self.node_index))
            ret.append(',\n    neigh_ind : ')
            ret.append(repr(self.neigh_ind))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    class Queued_Node(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=queued_node)
        
        
        Defined at tort.f90 lines 11-15
        
        """
        def __init__(self, handle=None):
            """
            self = Queued_Node()
            
            
            Defined at tort.f90 lines 11-15
            
            
            Returns
            -------
            this : Queued_Node
            	Object to be constructed
            
            
            Automatically generated constructor for queued_node
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            self._handle = _tort.f90wrap_queued_node_initialise()
        
        def __del__(self):
            """
            Destructor for class Queued_Node
            
            
            Defined at tort.f90 lines 11-15
            
            Parameters
            ----------
            this : Queued_Node
            	Object to be destructed
            
            
            Automatically generated destructor for queued_node
            """
            if self._alloc:
                _tort.f90wrap_queued_node_finalise(this=self._handle)
        
        @property
        def node_index(self):
            """
            Element node_index ftype=integer   pytype=int
            
            
            Defined at tort.f90 line 12
            
            """
            return _tort.f90wrap_queued_node__get__node_index(self._handle)
        
        @node_index.setter
        def node_index(self, node_index):
            _tort.f90wrap_queued_node__set__node_index(self._handle, node_index)
        
        @property
        def next_node(self):
            """
            Element next_node ftype=type(queued_node) pytype=Queued_Node
            
            
            Defined at tort.f90 line 13
            
            """
            next_node_handle = _tort.f90wrap_queued_node__get__next_node(self._handle)
            if tuple(next_node_handle) in self._objs:
                next_node = self._objs[tuple(next_node_handle)]
            else:
                next_node = tort_mod.Queued_Node.from_handle(next_node_handle)
                self._objs[tuple(next_node_handle)] = next_node
            return next_node
        
        @next_node.setter
        def next_node(self, next_node):
            next_node = next_node._handle
            _tort.f90wrap_queued_node__set__next_node(self._handle, next_node)
        
        def __str__(self):
            ret = ['<queued_node>{\n']
            ret.append('    node_index : ')
            ret.append(repr(self.node_index))
            ret.append(',\n    next_node : ')
            ret.append(repr(self.next_node))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    @staticmethod
    def set_nodes(n, indices):
        """
        set_nodes(n, indices)
        
        
        Defined at tort.f90 lines 23-35
        
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
        
        
        Defined at tort.f90 lines 37-50
        
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
        
        
        Defined at tort.f90 lines 105-143
        
        Parameters
        ----------
        n : int
        
        """
        _tort.f90wrap_torture(n=n)
    
    _dt_array_initialisers = []
    

tort_mod = Tort_Mod()

