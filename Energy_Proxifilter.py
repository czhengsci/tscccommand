#!/usr/bin/env python

__author__ = "Chen Zheng"
__version__ = "1.0"
__email__ = "chz022@ucsd.edu"
__date__ = "Dec 10, 2014"

from pymatgen.core.structure import Structure
from pymatgen.io.vaspio.vasp_output import Vasprun
from pymatgen.alchemy.filters import SpecieProximityFilter
import operator
import os
import argparse

def energy_profiler(dictname,args,strucdic):

    atomnumber = args.atom
    vasprunpath = dictname + '/vasprun.xml.relax2.gz'
    vobj = Vasprun(vasprunpath)
    strucdic[dictname]=vobj.final_energy/atomnumber


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        Energy profiler is a convenient script to calculate structure energy per atom""",
        epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("directories", metavar="dir",
                        type=str, nargs="+",
                        help="directories to process")
    parser.add_argument("-atom", type=int,
                        nargs="?",
                        help="Atom number of compound to specify")


    args = parser.parse_args()

    structuredic = {}

    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            energy_profiler(parent, args, structuredic)

        #Sort and return structure list based on the order of each structure's energy per atom
    structuredicsorted = sorted(structuredic.items(),key=operator.itemgetter(1))

    #Return the structure file ID with lowest energy per atom
    #print structuredicsorted[0][0]
    print structuredicsorted
