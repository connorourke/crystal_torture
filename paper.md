---
title: 'crystal_torture: A crystal tortuosity module'
tags:
  - Python
  - Fortran
  - OpenMP
  - chemistry
  - diffusion
  - tortuosity
authors:
  - name: Conn O'Rourke
    orcid: 0000-0002-0703-8234
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Author 2
    orcid: 0000-0002-3056-8233
    affiliation: 1
affiliations:
 - name: Department of Chemistry, University of Bath, Bath, BA2 7AX, United Kingdom
   index: 1
date: 13 August 2017
bibliography: paper.bib
---

# Summary

``crystal_torture`` is a Python, Fortran and OpenMP module that enables network analysis to be performed on crystal structures. It allows connected clusters of nodes (i.e. crystal sites) to be retrieved and output, examined to see if they form percolation networks (i.e. are periodic across the crystal boundary) and the path tortuosity of connected nodes within these clusters to be calculated.

# Crystal Site Connectivity

Diffusion through crystal structures is of fundmental importance to many problems in material science. One such example is the diffusion of Li<sup>+</sup> ions in lithium battery electrodes and solid electrolytes. 

Taking vacancy mediated diffusion of a Li<sup>+</sup> dopant through a solid electrolyte as an example, in the case where the atoms of the original crystal lattice are immobile and form blocks on the network of crystal sites. Li<sup>+</sup> diffusion in this instance will proceed along the network of connected sites occupied by Li<sup>+</sup> and \[Vac\]. Long range diffusion depends on the Li<sup>+</sup>-\[Vac\] occupied sites forming a percolation network (i.e. the probability of Li<sup>+</sup>-\[Vac\] site occupancy surpassing the critical percolation threshold). Establishing the connectivity of clusters formed by different doping regimes in this context therefore elucidates the concentration required to surpass this percolation threshold, and provides a simple mechanism for checkinng if a particular crystal is a suitable candidate as a solid Li<sub>+</sub> electrolyte. 

# `crystal_torture`






 






 












