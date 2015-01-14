__author__ = 'chenzheng'

import itertools
from pymatgen import Element, Structure, get_el_sp, write_structure, PeriodicSite

NaMnCoO2_441_Structure = Structure.from_file('Na8Mn4Co4O16_0/Na8Mn4Co4O16.cif')
NaMnCoO2_441_Structure.sites[10].species_and_occu.keys()