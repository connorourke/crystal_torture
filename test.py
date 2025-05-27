from crystal_torture.pymatgen_interface import _python_dist
import numpy as np

coord1 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
coord2 = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])

result = _python_dist(coord1, coord2, 2)
print('Python fallback type:', type(result))
print('Python fallback dtype:', result.dtype if hasattr(result, 'dtype') else 'No dtype')
print('Python fallback shape:', result.shape if hasattr(result, 'shape') else 'No shape') 
print('Sample values:', result[0, :])
print('Value types:', [type(x) for x in result[0, :]])
