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

# Crystal Site Connectivity and Tortuosity

Diffusion through crystal structures is of fundmental importance to many problems in material science. One such example is the diffusion of Li<sup>+</sup> ions in lithium battery electrodes and solid electrolytes. 

Typically the tortuosity, when defined in the context of ionic conductivity, relates to the transport through porous structures, and is used with a measure of the porosity to scale the bulk diffusion coefficient and thus obtain an effective diffusion coefficient. However porous polycrystalline electrolytes have several potential pitfalls, for example short-circuiting as a result of dendrites forming within the porous electrolyte. Single crystal electrolytes offer a potential solution to this problem [Kataoka-2018], and the diffusion coefficients of these single crystal electrolytes will depend upon the crystal site connectivity and crystal tortuousity.

Taking vacancy mediated diffusion of a Li<sup>+</sup> dopant through a solid electrolyte as an example, in the case where the atoms of the original crystal lattice are immobile and form blocks on the network of crystal sites. Li<sup>+</sup> diffusion in this instance will proceed along the network of connected sites occupied by Li<sup>+</sup> and \[Vac\]. Long range diffusion, and therefore the viability of the material as a solid electrolyte, depends on the Li<sup>+</sup>-\[Vac\] occupied sites forming a percolation network (i.e. the probability of Li<sup>+</sup>-\[Vac\] site occupancy surpassing the critical percolation threshold). Establishing the connectivity of clusters formed by different doping regimes in this context therefore allows statistics to be generated on the concentration required to surpass this percolation threshold, and provides a computationally inexpensive approach for checking if a particular crystal structure is a suitable candidate as a solid Li<sup>+</sup> electrolyte. 


<div id="image-table">
    <table>
	    <tr>
    	    <td style="padding:5px">
        	    <img src="paper/Images/direct.png">
        	      <figcaption>Direct pathway</figcaption>
      	    </td>
            <td style="padding:5px">
            	<img src="paper/Images/tortuous.png">
            	  <figcaption style="center">Tortuous pathway</figcaption>
             </td>
        </tr>
   </table>
</div>


The relative bulk crystal tortuosity, &tau;<sub>rel</sub>, can be defined as the ratio of the length of the shortest possible diffusion pathway through the crystal from a site to its periodic image, to the length of the direct path. In our case we are considering atoms on crystal sites as our nodes, so the tortuosity may be defined as the number of inter-nodal steps between two periodic site images in the actual pathway to that in an idealised direct pathway:

$$\tau_{rel}= \frac{n^{steps}_{path}}{n^{steps}_{direct}}$$

# `crystal_torture`

``crystal_torture`` is a Python, Fortran and OpenMP module that enables network analysis to be performed on crystal structures. The code includes an interface with `pymatgen` `Structure` objects [OngEtAl_CompMaterSci2013], allowing graphs to be set-up from crystal structures. These graphs can then be interogated to obtain connected clusters within the graph, which can be output as `pymatgen` `Structure` objects. The code can check if these clusters are periodic across the crystal structure, calculate the periodicity, and therefore establish whether these clusters form percolation networks. 

It can perform a breadth-first-search to calculate the crystal site tortuosity of the percolation networks: for each site in a periodic cluster the code can calculate the shortest possible pathway for a diffusing ion on this site to pass through the crystal and return to a periodic image of the site. This is the metric for establishing the tortuosity of the site.

Also included are simple doping routines which when coupled with the network analysis can be quickly used to build up statistics on the connectivty and tortuousity of particular doping regimes, and thereby determine the viability of particular doping strategies in the production of conductive crystals. 

For example, in a potential solid electrolyte in which doping with Li results in symmetrically inequivalent structures, we can take a large set of randomly doped structures at a given concentration and examine the connectvity and site tortuosity to produce the data in Figure 2.

<div id="image-table">
    <table>
	    <tr>
    	    <td style="padding:5px">
        	    <img src="paper/Images/stats.png">
        	      <figcaption>Figure 2: Cumulative distribution of the inverse average site tortuosity for 1000 (20x20x20) supercells of a potential solid Li<sup>+</sup> electrolyte at varying lithium concentrations. </figcaption>
      	    </td>
        </tr>
   </table>
</div>

An inverse tortuosity value of 0 tells us there are no percolation networks formed, while a value of 1 tells us there are direct routes through the crystal. From the data produced we can see that in order for the percolation threshold to be crossed, the dopant concentration *x*<sub>Li</sub> ≈  0.425, and even for this high concentration very few of the LI ions are in percolation networks. Performing this analysis  provides a simple and quick way of establishing whether a potential material is viable as an ionic conductor.






 












