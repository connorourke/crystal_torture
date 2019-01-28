---
title: 'crystal-torture: A crystal tortuosity module'
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
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Benjamin J. Morgan
    orcid: 0000-0002-3056-8233
    affiliation: "1, 2"
affiliations:
 - name: Department of Chemistry, University of Bath, Bath, BA2 7AX, United Kingdom
   index: 1
 - name: The Faraday Institution, Quad One, Harwell Science and Innovation Campus, Didcot, United Kingdom
   index: 2
date: 12 January 2019
bibliography: paper.bib
---

`crystal-torture` is a Python, Fortran, and OpenMP module for the analysis of diffusion networks in crystal structures.

The transport of mobile ions through crystalline solids is a fundamental process underlying phenomena such as solid-state reactions, and the behaviour of devices such as batteries and fuel cells. Quantitative descriptions of microscopic ionic transport are often derived by considering ionic trajectories as sequences of discrete &ldquo;hops&rdquo; made by individual ions moving between lattice sites in the host crystal structure [@Vineyard_JPhysChemSolids1957; @Catlow_AnnuRevMaterSci1986; @VanDerVenEtAl_AccChemRes2013; @Morgan_RSocOpenSci2017]. In a perfect crystal structure, the crystal symmetry means the full lattice can be constructed by periodically tiling a unit cell, containing a minimal number of lattice sites [@Glazer_IntroductionBook]. In conventional ionic conductors, ion diffusion on this periodic lattice can be modelled as a stochastic random walk, allowing derivation of simple quantitative relationships between the average microscopic hop rate and macroscopic transport coefficients, such as diffusion coefficient and ionic conductivities [@Catlow_SolStatIonics1983; @Catlow_AnnuRevMaterSci1986; @MorganAndMadden_PhysRevLett2014; @Morgan_RSocOpenSci2017; @MantinaEtAl_PhysRevLett2008]. This model is complicated in highly disordered crystal structures where some proportion of the host lattice sites are occupied by immobile atoms, which block the diffusion of nominally mobile ionic species. The long-ranged diffusion of mobile ions now depends on the proportion and arrangement of blocked sites, and the degree to which the mobile ions can access percolating paths through the crystal structure \[Fig. 1\]  [@GarciaDazaEtAl_ACSApplMaterInter2018; @Rustad_arXiv2016; @DengEtAl_ChemMater2015; @UrbanEtAl_AdvEnergyMater2014; @LeeEtAl_Science2014]. 
If the proportion of blocked sites, $p_\mathrm{b}$, exceeds $1-p$, where $p$ is the site-percolation threshold for that crystal lattice, then no continuous paths exist and the diffusion coefficient and ionic conductivity for the mobile ions are zero. 
If the proportion of blocked sites falls below this threshold ($0<p_b<1-p$) at least one percolating path exists and the mobile-ion transport coefficients are non-zero, but are decreased relative to the corresponding values for the ideal fully open lattice ($p_b=0$).
This decreased ion mobility has two causes. 
First, the available continuous paths are more *tortuous* than in a more open lattice: a mobile ion must move through more lattice sites to diffuse an equivalent end-to-end distance.
Second, some mobile ions may be trapped in non-percolating paths, and can not contribute to long-ranged transport.
`crystal-torture` has been written to perform statistical analysis of these path-blocking effects in disordered crystal lattices. The main analysis output is the per-site *microscopic tortuosity*, which provides a quantitative measure of the degree to which diffusion paths become indirect, relative to an ideal open lattice.

![Schematic showing the effect of progressively blocking lattice sites on ion diffusion pathways. (a) ideal lattice: all lattice sites are accessible and ions follow a random walk. (b) partially blocked lattice: Long ranged diffusion is still possible, but diffusive pathways are tortuous (blue arrows). Not all mobile ions can participate in long-ranged diffusion (orange arrows). (c) fully blocked lattice: The proportion of available sites is below the site percolation threshold. No long ranged diffusion is possible.](Images/lattice_blocking.pdf)

The concept of *tortuosity* has been extensively used in modelling macroscopic transport through porous media [@GhanbarianEtAl_SoilSciSocAmJ2013; @ShenAndChen_ChemEngSci2007]. `crystal-torture` allows the calculation of &ldquo;microscopic tortuosities&rdquo;, which we define for each lattice site as the length of the shortest possible path between a that site and its periodic images, divided by the minimum-image distance in the corresponding ideal (unblocked) lattice. 
If all lattice-lattice jumps are of equal distance, the microscopic tortuosity can equivalently be defined as the minimum number of inter-nodal steps between a pair of site periodic images, divided by the minimum number of steps between these sites in an ideal lattice:

$$\tau^\mathrm{micro}_i= \frac{\min n_{i\to i^\prime}}{\min n^\mathrm{ideal}_{i\to i^\prime}}$$

The microscopic tortuosity is a microscopic analogue of the &ldquo;geometric tortuosity&rdquo; [@Clennell_GeogSocLon1997].

`crystal-torture` provides a [Python API](https://crystal-torture.readthedocs.io/en/latest/) for interrogating site connectivity and diffusion pathways in partially blocked crystal structures. An interface is provided for parsing `pymatgen` `Structure` objects [@OngEtAl_CompMaterSci2013] as inputs, which are used to construct network graphs of connected sites. These graphs can be interogated to identify sets of sites forming connected clusters, which can be converted to `pymatgen` `Structure` objects for visualisation or further processing. `crystal-torture` can identify which clusters are periodic along one of more lattice directions, thereby identifying the clusters that form percolating networks. For each cluster, the microscopic tortuosity can be calculated, using a breadth-first-search algorithm. For each site in a periodic cluster, this finds the shortest periodic pathway to that site's periodic image. The number of nodes visited along this pathway is used to calculate the microscopic tortuosity. The code also includes routines for introducing varying proportions of blocked sites into a parent crystal structure, which allows automated analysis of how site connectivity and microscopic tortuosity varies with stoichiometry, for example under varying concentrations of dopant atoms.

# Acknowledgements

This work was funded by EPSRC Grant No. EP/N004302/1, and was supported with funding from the Faraday Institution ([faraday.ac.uk](http://faraday.ac.uk); EP/S003053/1), grant number FIRG003.
B.J.M. acknowledges support from the Royal Society (UF130329).

# References
