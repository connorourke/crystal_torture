"""Simple functions for manipulating and doping a pymatgen structure."""

import random
from pymatgen.core import Structure, Molecule, PeriodicSite


def count_sites(structure: Structure, species: set[str] | None = None, labels: set[str] | None = None) -> int:
    """Count sites in structure by species and/or labels.
    
    Given structure object and either specie string or label string, it counts and returns the 
    number of sites with that species or label (or both) in the structure.

    Args:
        structure: Pymatgen structure object.
        species: Site species to count.
        labels: Site labels to count.

    Returns:
        Number of sites occupied by species or label (or both) in structure.
        
    Raises:
        ValueError: If neither species nor labels are provided.
    """
    if labels and species:
        return len(
            [
                i
                for i, site in enumerate(structure)
                if ((site.label in labels) and (site.species_string in species))
            ]
        )
    elif species and not labels:
        return len(
            [i for i, site in enumerate(structure) if site.species_string in species]
        )
    elif labels and not species:
        return len([i for i, site in enumerate(structure) if site.label in labels])
    else:
        raise ValueError("Need to supply either specie, or label to count_sites")


def index_sites(structure: Structure, species: set[str] | None = None, labels: set[str] | None = None) -> list[int]:
    """Return site indices occupied by specie or label (or both).
    
    Args:
        structure: Pymatgen structure object.
        species: Site species to find.
        labels: Site labels to find.

    Returns:
        List with site indices occupied by species or label (or both) in structure.
        
    Raises:
        ValueError: If neither species nor labels are provided.
    """
    if labels and species:
        return [
            i
            for i, site in enumerate(structure)
            if ((site.label in labels) and (site.species_string in species))
        ]
    elif species and not labels:
        return [i for i, site in enumerate(structure) if site.species_string in species]
    elif labels and not species:
        return [i for i, site in enumerate(structure) if site.label in labels]
    else:
        raise ValueError("Need to supply either specie, or label to index_sites")


def sort_structure(structure: Structure, order: list[str]) -> Structure:
    """Sort structure species so their indices sit side by side in given order.
    
    Given a pymatgen structure object sort the species so that their indices
    sit side by side in the structure, in given order - allows for POSCAR file to 
    be written in a readable way after doping.

    Args:
        structure: Pymatgen structure object.
        order: List of species str in order to sort.

    Returns:
        Ordered pymatgen Structure object.
        
    Raises:
        ValueError: If order elements don't match structure elements.
    """
    symbols = [species for species in structure.symbol_set]

    if "X" in set(symbols):
        symbols.remove("X")
        symbols.append("X0+")

    if set(symbols) == set(order):
        structure_sorted = Structure(lattice=structure.lattice, species=[], coords=[])
        for symbol in symbols:
            for i, site in enumerate(structure.sites):
                if site.species_string == symbol:
                    structure_sorted.append(
                        symbol,
                        site.coords,
                        coords_are_cartesian=True,
                        properties=site.properties,
                    )
    else:
        error_msg = "Error: sort structure elements in list passed in order does not match that found in POSCAR\n"
        error_msg += "Passed: {}\n".format(order)
        error_msg += "POSCAR: {}\n".format(symbols)
        raise ValueError(error_msg)
    return structure_sorted


def dope_structure(
    structure: Structure, 
    conc: float, 
    species_to_rem: str, 
    species_to_insert: list[str], 
    label_to_remove: str | None = None
) -> Structure:
    """Dope a pymatgen structure object to a particular concentration.
    
    Removes conc * no(species_to_remove) from structure and inserts species to insert in 
    their place. Does so at random (excepting when label_to_remove is passed).

    Args:
        structure: Pymatgen structure object.
        conc: Fractional percentage of sites to remove.
        species_to_rem: The species to remove from structure.
        species_to_insert: A list of species to equally distribute over sites that are removed.
        label_to_remove: Label of sites to select for removal.
        
    Returns:
        The doped structure.
        
    Raises:
        ValueError: If species_to_rem is not in structure.
    """
    if {species_to_rem}.issubset(structure.symbol_set):
        no_sites = count_sites(
            structure, species={species_to_rem}, labels={label_to_remove} if label_to_remove else None
        )
        site_indices = index_sites(
            structure, species={species_to_rem}, labels={label_to_remove} if label_to_remove else None
        )
        no_dopants = int(round(conc * no_sites) / len(species_to_insert))
        random.shuffle(site_indices)
        for species in species_to_insert:
            for dopant in range(no_dopants):
                structure[site_indices.pop()] = species
        structure = sort_structure(
            structure=structure, order=[species for species in structure.symbol_set]
        )
        return structure
    else:
        raise ValueError("dope_structure: species_to_rem is not in structure")


def dope_structure_by_no(
    structure: Structure, 
    no_dopants: int, 
    species_to_rem: str, 
    species_to_insert: list[str], 
    label_to_remove: str | None = None
) -> Structure:
    """Dope a pymatgen structure object by swapping a specific number of sites.
    
    Removes no_dopants of species_to_remove from structure and inserts species to insert in 
    their place. Does so at random (excepting when label_to_remove is passed).

    Args:
        structure: Pymatgen structure object.
        no_dopants: Number of each type of dopant to insert.
        species_to_rem: The species to remove from structure.
        species_to_insert: A list of species to equally distribute over sites that are removed.
        label_to_remove: Label of sites to select for removal.
        
    Returns:
        The doped structure.
        
    Raises:
        ValueError: If species_to_rem is not in structure.
    """
    if {species_to_rem}.issubset(structure.symbol_set):
        no_sites = count_sites(
            structure, species={species_to_rem}, labels={label_to_remove} if label_to_remove else None
        )
        site_indices = index_sites(
            structure, species={species_to_rem}, labels={label_to_remove} if label_to_remove else None
        )
        random.shuffle(site_indices)

        for species in species_to_insert:
            for dopant in range(no_dopants):
                structure[site_indices.pop()] = species
        structure = sort_structure(
            structure=structure, order=[species for species in structure.symbol_set]
        )

        return structure
    else:
        raise ValueError("dope_struture_by_no: species_to_rem is not in structure")


def set_site_labels(structure: Structure, labels: list[str]) -> None:
    """Set site labels using the built-in label property.
    
    Args:
        structure: Pymatgen structure object.
        labels: List of labels to assign to sites.
        
    Raises:
        ValueError: If number of labels doesn't match number of sites.
    """
    if len(labels) != len(structure.sites):
        raise ValueError(f"Number of labels ({len(labels)}) must match number of sites ({len(structure.sites)})")
    
    for site, label in zip(structure.sites, labels):
        site.label = label