# Quick Start Guide

This guide shows how to perform basic tortuosity analysis on crystal structures using `crystal-torture`.

The typical analysis involves loading a crystal structure, creating a graph representation, analysing tortuosity, and extracting results.

## Example: Lithium Diffusion Analysis

Here's a complete example analysing lithium diffusion pathways:

```python
import crystal_torture
from pymatgen.core import Structure, Lattice

# Create a simple cubic lithium structure for demonstration
lattice = Lattice.cubic(4.0)  # 4 Å lattice parameter
species = ["Li", "Li", "Li", "Li"]
coords = [
    [0.0, 0.0, 0.0],
    [0.5, 0.5, 0.0], 
    [0.5, 0.0, 0.5],
    [0.0, 0.5, 0.5]
]
structure = Structure(lattice, species, coords)

# Create graph representation
# rcut: cutoff distance for site connectivity (Ångstroms)
# elements: which elements to include in the analysis
graph = crystal_torture.graph_from_structure(
    structure=structure,
    rcut=3.0,
    elements={"Li"}  # Analyse lithium sites only
)

# Perform tortuosity analysis
graph.torture()  # Automatically uses fastest available method

# Extract results
print(f"Number of clusters: {len(graph.clusters)}")
print(f"Fraction of percolating sites: {graph.return_frac_percolating():.3f}")

# Get detailed results for each cluster
for i, cluster in enumerate(graph.minimal_clusters):
    print(f"Cluster {i}:")
    print(f"  Size: {cluster.size} sites")
    print(f"  Periodic: {cluster.periodic}D")
    if cluster.tortuosity is not None:
        print(f"  Average tortuosity: {cluster.tortuosity:.1f} steps")
```

## Working with Files

For real structures, load from common crystallographic file formats:

```python
# Load from POSCAR, CIF, or other formats supported by pymatgen
graph = crystal_torture.graph_from_file(
    filename="POSCAR",  # or "structure.cif", etc.
    rcut=3.5,
    elements={"Li", "Na"}  # Multiple elements
)

graph.torture()

# Output clusters as separate structure files
graph.output_clusters(fmt="poscar", periodic=True)
# Creates CLUS_0.vasp, CLUS_1.vasp, etc.
```

## Understanding the Results

Clusters are groups of connected sites that allow ion transport. The size tells you how many sites are in the cluster, and the periodic value indicates the dimensionality of transport: 0D means isolated, 1D is linear chains, 2D is planar networks, and 3D represents bulk diffusion.

Tortuosity measures the number of steps along the connected network to reach a periodic image. Lower values indicate more direct pathways, while higher values suggest more indirect, tortuous routes.

The percolation fraction shows what proportion of sites participate in long-range transport, which is useful for comparing different compositions or structures.
