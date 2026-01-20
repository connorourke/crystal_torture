# Edge-Weighted Percolation Analysis

This guide shows how to perform percolation analysis using explicit edge lists with optional weights, enabling threshold-based analysis to find percolation thresholds.

## Overview

The edges module provides an alternative to distance-cutoff-based graph construction. Instead of defining connectivity by a single cutoff radius, you can:

* Generate edge data from structure geometry
* Assign weights to edges (e.g., migration barriers)
* Filter edges by weight threshold
* Find percolation thresholds by sweeping across weight values
* Save and load edge data in JSON format

This is useful when edge weights represent physical quantities like migration barriers, allowing you to determine the minimum barrier at which a structure percolates.

## Basic Usage

### Generating Edges from Structure

```python
from pymatgen.core import Structure
from crystal_torture import edges_from_structure, graph_from_edges
from crystal_torture.pymatgen_interface import filter_structure_by_species

# Load structure and filter to species of interest
structure = Structure.from_file("POSCAR")
li_structure = filter_structure_by_species(structure, ["Li"])

# Generate edges within a cutoff radius
edge_data = edges_from_structure(li_structure, rcut=4.0)
print(f"Generated {len(edge_data.edges)} edges")

# Build graph and analyse percolation
graph = graph_from_edges(li_structure, edge_data)
frac = graph.return_frac_percolating()
print(f"Fraction percolating: {frac:.3f}")
```

### Weighted Edges

Assign weights to edges using a weight function:

```python
# Weight = distance between sites
edge_data = edges_from_structure(
    li_structure,
    rcut=5.0,
    weight_fn=lambda site_i, site_j, distance: distance,
)

# Inspect edge weights
for edge in edge_data.edges[:5]:
    print(f"Edge {edge.nodes}: weight = {edge.weight:.3f}")
```

## Finding Percolation Thresholds

The key application is sweeping across weight thresholds to find where percolation occurs:

```python
# Generate weighted edges
edge_data = edges_from_structure(
    li_structure,
    rcut=5.0,
    weight_fn=lambda s1, s2, d: d,
)

# Sweep thresholds
thresholds = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

for threshold in thresholds:
    # Filter edges by weight threshold
    filtered = edge_data.filter(lambda e: e.weight <= threshold)

    # Build graph and check percolation
    graph = graph_from_edges(li_structure, filtered)
    frac = graph.return_frac_percolating()

    print(f"Threshold {threshold:.1f} Å: {len(filtered.edges)} edges, {frac:.3f} percolating")
```

## Label-Based Weights

For structures with labelled sites (e.g., octahedral vs tetrahedral), assign weights based on site type pairs:

```python
from crystal_torture import edges_from_labels

# Structure must have 'label' site property
# e.g., structure.add_site_property("label", ["Oct", "Tet", "Oct", ...])

# Define weights for label pairs (e.g., migration barriers)
label_weights = {
    ("Oct", "Oct"): 0.2,  # Easy Oct-Oct hop
    ("Oct", "Tet"): 0.5,  # Medium Oct-Tet hop
    ("Tet", "Tet"): 0.8,  # Difficult Tet-Tet hop
}

edge_data = edges_from_labels(
    labelled_structure,
    rcut=3.0,
    label_weights=label_weights,
)
```

## Saving and Loading Edge Data

Edge data can be saved to JSON for later use:

```python
from crystal_torture import save_edges, load_edges

# Save edges
save_edges(edge_data, "edges.json")

# Load edges
loaded_edges = load_edges("edges.json")
```

The JSON format is human-readable:

```json
{
  "num_nodes": 8,
  "edges": [
    {"nodes": [0, 1], "weight": 0.35},
    {"nodes": [0, 2], "weight": 0.52},
    {"nodes": [1, 3], "weight": 0.41}
  ]
}
```

## Custom Weight Functions

Weight functions receive both sites and the distance, allowing flexible weight calculations:

```python
def barrier_weight(site_i, site_j, distance):
    """Example: weight based on distance and site properties."""
    # Access site properties
    label_i = site_i.properties.get("label", "unknown")
    label_j = site_j.properties.get("label", "unknown")

    # Calculate weight based on labels and distance
    base_barrier = 0.3 if label_i == label_j else 0.5
    return base_barrier + 0.1 * distance

edge_data = edges_from_structure(
    structure,
    rcut=4.0,
    weight_fn=barrier_weight,
)
```

## Tortuosity Analysis

Graphs built from edges support the same tortuosity analysis as standard graphs:

```python
edge_data = edges_from_structure(li_structure, rcut=4.0)
graph = graph_from_edges(li_structure, edge_data)

# Run tortuosity analysis
graph.torture()  # Or graph.torture_py() for pure Python

# Access results
print(f"Tortuosity calculated for {len(graph.tortuosity)} sites")
for cluster in graph.minimal_clusters:
    if cluster.tortuosity is not None:
        print(f"Cluster tortuosity: {cluster.tortuosity:.1f}")
```

## API Reference

The main functions are:

* `edges_from_structure(structure, rcut, weight_fn=None)` - Generate edges from geometry
* `edges_from_labels(structure, rcut, label_weights)` - Generate edges with label-based weights
* `graph_from_edges(structure, edge_data)` - Build graph from edge list
* `save_edges(edge_data, filename)` - Save to JSON
* `load_edges(filename)` - Load from JSON
* `EdgeData.filter(predicate)` - Filter edges by predicate function

See the [API documentation](mod/edges) for full details.
