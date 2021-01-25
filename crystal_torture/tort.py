from __future__ import print_function, absolute_import, division
import _tort
import f90wrap.runtime
import logging

class Tort_Mod(f90wrap.runtime.FortranModule):
    """
    Module tort_mod
    
    
    Defined at tort.f90 lines 1-175
    
    """
    @f90wrap.runtime.register_class("tort.test_node")
    class test_node(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=test_node)
        
        
        Defined at tort.f90 lines 4-11
        
        """
        def __init__(self, handle=None):
            """
            self = Test_Node()
            
            
            Defined at tort.f90 lines 4-11
            
            
            Returns
            -------
            this : Test_Node
            	Object to be constructed
            
            
            Automatically generated constructor for test_node
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _tort.f90wrap_test_node_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Test_Node
            
            
            Defined at tort.f90 lines 4-11
            
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
            
            
            Defined at tort.f90 line 10
            
            """
            return _tort.f90wrap_test_node__get__node_index(self._handle)
        
        @node_index.setter
        def node_index(self, node_index):
            _tort.f90wrap_test_node__set__node_index(self._handle, node_index)
        
        @property
        def uc_index(self):
            """
            Element uc_index ftype=integer pytype=int
            
            
            Defined at tort.f90 line 10
            
            """
            return _tort.f90wrap_test_node__get__uc_index(self._handle)
        
        @uc_index.setter
        def uc_index(self, uc_index):
            _tort.f90wrap_test_node__set__uc_index(self._handle, uc_index)
        
        @property
        def neigh_ind(self):
            """
            Element neigh_ind ftype=integer pytype=int
            
            
            Defined at tort.f90 line 11
            
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
            ret.append(',\n    uc_index : ')
            ret.append(repr(self.uc_index))
            ret.append(',\n    neigh_ind : ')
            ret.append(repr(self.neigh_ind))
            ret.append('}')
            return ''.join(ret)
        
        _dt_array_initialisers = []
        
    
    @f90wrap.runtime.register_class("tort.queued_node")
    class queued_node(f90wrap.runtime.FortranDerivedType):
        """
        Type(name=queued_node)
        
        
        Defined at tort.f90 lines 13-19
        
        """
        def __init__(self, handle=None):
            """
            self = Queued_Node()
            
            
            Defined at tort.f90 lines 13-19
            
            
            Returns
            -------
            this : Queued_Node
            	Object to be constructed
            
            
            Automatically generated constructor for queued_node
            """
            f90wrap.runtime.FortranDerivedType.__init__(self)
            result = _tort.f90wrap_queued_node_initialise()
            self._handle = result[0] if isinstance(result, tuple) else result
        
        def __del__(self):
            """
            Destructor for class Queued_Node
            
            
            Defined at tort.f90 lines 13-19
            
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
            
            
            Defined at tort.f90 line 18
            
            """
            return _tort.f90wrap_queued_node__get__node_index(self._handle)
        
        @node_index.setter
        def node_index(self, node_index):
            _tort.f90wrap_queued_node__set__node_index(self._handle, node_index)
        
        @property
        def next_node(self):
            """
            Element next_node ftype=type(queued_node) pytype=Queued_Node
            
            
            Defined at tort.f90 line 19
            
            """
            next_node_handle = _tort.f90wrap_queued_node__get__next_node(self._handle)
            if tuple(next_node_handle) in self._objs:
                next_node = self._objs[tuple(next_node_handle)]
            else:
                next_node = tort_mod.queued_node.from_handle(next_node_handle)
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
    def allocate_nodes(n, n2):
        """
        allocate_nodes(n, n2)
        
        
        Defined at tort.f90 lines 24-34
        
        Parameters
        ----------
        n : int
        n2 : int
        
        """
        _tort.f90wrap_allocate_nodes(n=n, n2=n2)
    
    @staticmethod
    def tear_down():
        """
        tear_down()
        
        
        Defined at tort.f90 lines 36-50
        
        
        """
        _tort.f90wrap_tear_down()
    
    @staticmethod
    def set_neighbours(ind, uc_ind, n, neigh):
        """
        set_neighbours(ind, uc_ind, n, neigh)
        
        
        Defined at tort.f90 lines 52-66
        
        Parameters
        ----------
        ind : int
        uc_ind : int
        n : int
        neigh : int array
        
        """
        _tort.f90wrap_set_neighbours(ind=ind, uc_ind=uc_ind, n=n, neigh=neigh)
    
    @staticmethod
    def torture(n, uc_nodes):
        """
        torture(n, uc_nodes)
        
        
        Defined at tort.f90 lines 119-174
        
        Parameters
        ----------
        n : int
        uc_nodes : int array
        
        """
        _tort.f90wrap_torture(n=n, uc_nodes=uc_nodes)
    
    @property
    def uc_tort(self):
        """
        Element uc_tort ftype=integer pytype=int
        
        
        Defined at tort.f90 line 22
        
        """
        array_ndim, array_type, array_shape, array_handle = \
            _tort.f90wrap_tort_mod__array__uc_tort(f90wrap.runtime.empty_handle)
        if array_handle in self._arrays:
            uc_tort = self._arrays[array_handle]
        else:
            uc_tort = f90wrap.runtime.get_array(f90wrap.runtime.sizeof_fortran_t,
                                    f90wrap.runtime.empty_handle,
                                    _tort.f90wrap_tort_mod__array__uc_tort)
            self._arrays[array_handle] = uc_tort
        return uc_tort
    
    @uc_tort.setter
    def uc_tort(self, uc_tort):
        self.uc_tort[...] = uc_tort
    
    def __str__(self):
        ret = ['<tort_mod>{\n']
        ret.append('    uc_tort : ')
        ret.append(repr(self.uc_tort))
        ret.append('}')
        return ''.join(ret)
    
    _dt_array_initialisers = []
    

tort_mod = Tort_Mod()

