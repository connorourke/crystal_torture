"""Distance calculation module - ctypes wrapper for Fortran distance functions."""
import ctypes
import numpy as np
from pathlib import Path
import numpy.typing as npt

_dist_lib: ctypes.CDLL | None
_DIST_AVAILABLE: bool

# Try to load the compiled Fortran library using ctypes
try:
    # Find the library file
    package_dir = Path(__file__).parent
    
    # Look for the extension (platform-specific naming)
    import platform
    if platform.system() == "Darwin":  # macOS
        lib_patterns = ["libdist*.dylib", "libdist*.so"]
    elif platform.system() == "Windows":
        lib_patterns = ["libdist*.dll", "libdist*.pyd"]
    else:  # Linux and others
        lib_patterns = ["libdist*.so"]
    
    lib_file = None
    for pattern in lib_patterns:
        lib_files = list(package_dir.glob(pattern))
        if lib_files:
            # Sort to get the most specific match first
            lib_files.sort(key=lambda x: len(x.name), reverse=True)
            lib_file = lib_files[0]
            break
    
    if lib_file and lib_file.exists():
        # Load the library
        _dist_lib = ctypes.CDLL(str(lib_file))
        
        # Define function signatures for dist functions
        # The Fortran functions are already C-compatible, so we can call them directly
        
        # subroutine dist(coord1, coord2, n, dist_matrix)
        # Note: Fortran passes arrays by reference, and we need to handle this carefully
        _dist_lib.dist_.argtypes = [
            ctypes.POINTER(ctypes.c_float),  # coord1
            ctypes.POINTER(ctypes.c_float),  # coord2  
            ctypes.POINTER(ctypes.c_int),    # n
            ctypes.POINTER(ctypes.c_float)   # dist_matrix (output)
        ]
        _dist_lib.dist_.restype = None
        
        # subroutine shift_index(index_n, shift, new_index)
        _dist_lib.shift_index_.argtypes = [
            ctypes.POINTER(ctypes.c_int),    # index_n
            ctypes.POINTER(ctypes.c_int),    # shift (array of 3 ints)
            ctypes.POINTER(ctypes.c_int)     # new_index (output)
        ]
        _dist_lib.shift_index_.restype = None
        
        _DIST_AVAILABLE = True
    else:
        _dist_lib = None
        _DIST_AVAILABLE = False
        
except Exception:
    _dist_lib = None
    _DIST_AVAILABLE = False


def dist(coord1: npt.ArrayLike, coord2: npt.ArrayLike, n: int) -> npt.NDArray[np.floating]:
    """Compute distance matrix between two sets of coordinates.
    
    Uses Fortran implementation if available, otherwise falls back to Python implementation.
    
    Args:
        coord1: Array of coordinates (n x 3).
        coord2: Array of coordinates (n x 3).
        n: Number of coordinates.
        
    Returns:
        Distance matrix (n x n).
    """
    if not _DIST_AVAILABLE:
        # Fallback to Python implementation
        from .pymatgen_interface import _python_dist
        # Convert to numpy arrays for type safety
        coord1_array = np.asarray(coord1, dtype=np.float64)
        coord2_array = np.asarray(coord2, dtype=np.float64)
        return _python_dist(coord1_array, coord2_array, n)
    
    if _dist_lib is None:
        raise RuntimeError("Distance library not available")
    
    # Convert to numpy arrays and ensure correct dtype and layout
    coord1 = np.asarray(coord1, dtype=np.float32, order='F')
    coord2 = np.asarray(coord2, dtype=np.float32, order='F')
    
    # Create output array
    dist_matrix = np.zeros((n, n), dtype=np.float32, order='F')
    
    # Convert to ctypes
    coord1_ptr = coord1.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    coord2_ptr = coord2.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    n_ptr = ctypes.byref(ctypes.c_int(n))
    dist_ptr = dist_matrix.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    
    # Call Fortran function
    _dist_lib.dist_(coord1_ptr, coord2_ptr, n_ptr, dist_ptr)
    
    return dist_matrix.astype(np.float64)


def shift_index(index_n: int, shift: list[int]) -> int:
    """Shift the index of a site in the unit cell to the corresponding index in the 3x3x3 halo supercell.
    
    Used when getting neighbour list for supercell from unit cell neighbour list.
    
    Args:
        index_n: Original index (must be non-negative).
        shift: Shift vector [x, y, z].
        
    Returns:
        New shifted index for image site in supercell.
        
    Raises:
        ValueError: If index_n is negative.
    """
    if index_n < 0:
        raise ValueError(f"shift_index received negative index: {index_n}. This indicates an upstream bug.")
    
    if not _DIST_AVAILABLE:
        # Fallback to Python implementation
        from .pymatgen_interface import _python_shift_index
        return _python_shift_index(index_n, shift)
    
    if _dist_lib is None:
        raise RuntimeError("Distance library not available")
    
    # Convert inputs to ctypes - ensure integers
    index_n_c = ctypes.c_int(int(index_n))  # Convert to int first
    shift_ints = [int(x) for x in shift]    # Convert numpy.float64 to int
    shift_array = (ctypes.c_int * 3)(*shift_ints)
    new_index_c = ctypes.c_int()
    
    # Call Fortran function
    _dist_lib.shift_index_(
        ctypes.byref(index_n_c),
        shift_array,
        ctypes.byref(new_index_c)
    )
    
    return new_index_c.value