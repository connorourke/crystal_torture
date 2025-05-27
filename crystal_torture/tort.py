from __future__ import print_function, absolute_import, division
import logging
import ctypes
import ctypes.util
from pathlib import Path
import warnings

# Try to load the compiled Fortran library using ctypes
try:
    # Find the library file
    package_dir = Path(__file__).parent
    
    # Look for the extension (platform-specific naming)
    import platform
    if platform.system() == "Darwin":  # macOS
        lib_patterns = ["_tort*.dylib", "_tort*.so"]
    elif platform.system() == "Windows":
        lib_patterns = ["_tort*.dll"]
    else:  # Linux and others
        lib_patterns = ["_tort*.so"]
    
    lib_file = None
    for pattern in lib_patterns:
        lib_files = list(package_dir.glob(pattern))
        if lib_files:
            lib_file = lib_files[0]
            break
    
    if lib_file and lib_file.exists():
        # Load the library
        _tort_lib = ctypes.CDLL(str(lib_file))
        
        # Define function signatures for our C interface
        # void allocate_nodes(int n, int n2)
        _tort_lib.allocate_nodes.argtypes = [ctypes.c_int, ctypes.c_int]
        _tort_lib.allocate_nodes.restype = None
        
        # void tear_down()
        _tort_lib.tear_down.argtypes = []
        _tort_lib.tear_down.restype = None
        
        # void set_neighbours(int ind, int uc_ind, int n, int* neigh)
        _tort_lib.set_neighbours.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        _tort_lib.set_neighbours.restype = None
        
        # void torture(int n, int* uc_nodes)
        _tort_lib.torture.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        _tort_lib.torture.restype = None
        
        # int get_uc_tort(int index)
        _tort_lib.get_uc_tort.argtypes = [ctypes.c_int]
        _tort_lib.get_uc_tort.restype = ctypes.c_int
        
        # int get_uc_tort_size()
        _tort_lib.get_uc_tort_size.argtypes = []
        _tort_lib.get_uc_tort_size.restype = ctypes.c_int
        
        _FORT_AVAILABLE = True
    else:
        _tort_lib = None
        _FORT_AVAILABLE = False
        warnings.warn("Fortran extensions not available. Only Python implementations will work.", 
                      UserWarning)
        
except Exception as e:
    _tort_lib = None
    _FORT_AVAILABLE = False
    warnings.warn(f"Fortran extensions not available ({e}). Only Python implementations will work.", 
                  UserWarning)


class Tort_Mod:
    """
    Module tort_mod - ctypes wrapper for Fortran functions
    """
    
    def __init__(self):
        if not _FORT_AVAILABLE:
            raise ImportError("Fortran extensions not available. Use torture_py() instead.")
        self._uc_tort_data = None
    
    def allocate_nodes(self, n, n2):
        """
        allocate_nodes(n, n2)
        
        Parameters
        ----------
        n : int
        n2 : int
        """
        _tort_lib.allocate_nodes(n, n2)
    
    def tear_down(self):
        """
        tear_down()
        """
        _tort_lib.tear_down()
        self._uc_tort_data = None
    
    def set_neighbours(self, ind, uc_ind, n, neigh):
        """
        set_neighbours(ind, uc_ind, n, neigh)
        
        Parameters
        ----------
        ind : int
        uc_ind : int
        n : int
        neigh : list of int
        """
        # Convert Python list to ctypes array
        neigh_array = (ctypes.c_int * len(neigh))(*neigh)
        _tort_lib.set_neighbours(ind, uc_ind, n, neigh_array)
    
    def torture(self, n, uc_nodes):
        """
        torture(n, uc_nodes)
        
        Parameters
        ----------
        n : int
        uc_nodes : list of int
        """
        # Convert Python list to ctypes array
        uc_nodes_array = (ctypes.c_int * len(uc_nodes))(*uc_nodes)
        _tort_lib.torture(n, uc_nodes_array)
    
    @property
    def uc_tort(self):
        """
        Access to uc_tort array data
        """
        if not _FORT_AVAILABLE:
            return None
            
        # Get the size of the array
        size = _tort_lib.get_uc_tort_size()
        if size <= 0:
            return []
        
        # Create a list with the tortuosity values
        result = []
        for i in range(size):
            tort_value = _tort_lib.get_uc_tort(i)
            result.append(tort_value if tort_value >= 0 else 0)
        
        return result


# Create the module instance
if _FORT_AVAILABLE:
    tort_mod = Tort_Mod()
else:
    tort_mod = None