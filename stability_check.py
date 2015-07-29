#!/usr/bin/env python

__author__ = "Shyue Ping Ong"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__version__ = "1.0"
__date__ = "Sep 21, 2012"

import argparse
import sys

from pymatgen.matproj.rest import MPRester
from pymatgen.phasediagram.pdmaker import PhaseDiagram
from pymatgen.apps.borg.hive import VaspToComputedEntryDrone
from pymatgen.phasediagram.pdanalyzer import PDAnalyzer
from pymatgen.entries.compatibility import MaterialsProjectCompatibility


def calculate_phase_stability(args):
    #This initializes the REST adaptor.
    a = MPRester(args.api_key)

    drone = VaspToComputedEntryDrone()
    entry = drone.assimilate(args.directory)

    compat = MaterialsProjectCompatibility()
    entry = compat.process_entry(entry)

    if not entry:
        print "Calculation parameters are not consistent with Materials " + \
            "Project parameters."
        sys.exit()

    syms = [el.symbol for el in entry.composition.elements]
    #This gets all entries belonging to the relevant system.
    entries = a.get_entries_in_chemsys(syms)
    entries.append(entry)

    #Process entries with Materials Project compatibility.
    entries = compat.process_entries(entries)

    print [e.composition.reduced_formula for e in entries]

    pd = PhaseDiagram(entries)

    analyzer = PDAnalyzer(pd)
    ehull = analyzer.get_e_above_hull(entry) * 1000

    print "Run contains formula {} with corrected energy {:.3f} eV.".format(
        entry.composition, entry.energy
    )
    print "Energy above convex hull = {:.1f} meV".format(ehull)
    if ehull < 1:
        print "Entry is stable."
    elif ehull < 30:
        print "Entry is metastable and could be stable at finite temperatures."
    elif ehull < 50:
        print "Entry has a low probability of being stable."
    else:
        print "Entry is very unlikely to be stable."

    if ehull > 0:
        decomp = analyzer.get_decomposition(entry.composition)
        print {e.composition.formula: k for e, k in decomp.items()}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This is a simple phase stability estimation script which utilizes the
    Materials API and pymatgen to calculate the phase stability of a single
    material.""",
    epilog="""
    Author: Shyue Ping Ong
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("directory", metavar="dir", type=str,
                        help="directory containing vasp run to process")
    parser.add_argument("-k", "--key", dest="api_key", type=str, required=True,
                        help="User's Materials API key.")

    args = parser.parse_args()
    calculate_phase_stability(args)
