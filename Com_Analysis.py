#!/usr/bin/env python

from __future__ import division, unicode_literals

"""
A master convenience script with many tools for vasp and structure analysis.
"""

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "3.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "ongsp@ucsd.edu"
__date__ = "Sep 9, 2014"

import argparse
import os
import re
import logging
import multiprocessing
import sys
import datetime

from collections import OrderedDict

from pymatgen import Structure
from pymatgen.io.vaspio import Outcar, Vasprun, Chgcar
from pymatgen.util.string_utils import str_aligned
from pymatgen.apps.borg.hive import SimpleVaspToComputedEntryDrone, \
    VaspToComputedEntryDrone
from pymatgen.apps.borg.queen import BorgQueen
from pymatgen.electronic_structure.plotter import DosPlotter
from pymatgen.io.vaspio import Poscar
from pymatgen.io.cifio import CifParser, CifWriter
from pymatgen.io.vaspio_set import MPVaspInputSet, MITVaspInputSet
from pymatgen.io.cssrio import Cssr
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.alchemy.materials import TransformedStructure
from pymatgen.analysis.diffraction.xrd import XRDCalculator
from prettytable import PrettyTable

SAVE_FILE = "vasp_data.gz"


def get_energies(rootdir, reanalyze, verbose, detailed, sort, formulaunit, debug,hull):
    """
    Doc string.
    """
    if (verbose and not debug):
        FORMAT = "%(relativeCreated)d msecs : %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)

    elif debug:
        logging.basicConfig(level=logging.DEBUG)

    if not detailed:
        drone = SimpleVaspToComputedEntryDrone(inc_structure=True)
    else:
        drone = VaspToComputedEntryDrone(inc_structure=True,
                                         data=["filename",
                                               "initial_structure"])

    ncpus = multiprocessing.cpu_count()
    logging.info("Detected {} cpus".format(ncpus))
    queen = BorgQueen(drone, number_of_drones=ncpus)
    if os.path.exists(SAVE_FILE) and not reanalyze:
        msg = "Using previously assimilated data from {}.".format(SAVE_FILE) \
            + " Use -f to force re-analysis."
        queen.load_data(SAVE_FILE)
    else:
        if ncpus > 1:
            queen.parallel_assimilate(rootdir)
        else:
            queen.serial_assimilate(rootdir)
        msg = "Analysis results saved to {} for faster ".format(SAVE_FILE) + \
              "subsequent loading."
        queen.save_data(SAVE_FILE)

    entries = queen.get_data()
    if sort == "energy_per_atom":
        entries = sorted(entries, key=lambda x: x.energy_per_atom)
    elif sort == "filename":
        entries = sorted(entries, key=lambda x: x.data["filename"])

    logging.debug('First Energy entry is {}'.format(entries[0]))

    base_energy = entries[0].energy
    logging.debug("Lowest energy entry's energy is: {}".format(entries[0].energy))



    all_data = []
    energy_diff = []

    for e in entries:
        if not detailed:
            delta_vol = "{:.2f}".format(e.data["delta_volume"] * 100)
        else:
            delta_vol = e.structure.volume / \
                e.data["initial_structure"].volume - 1
            delta_vol = "{:.2f}".format(delta_vol * 100)
        all_data.append((e.data["filename"].replace("./", ""),
                         re.sub("\s+", "", e.composition.formula),
                         "{:.5f}".format(e.energy),
                         "{:.5f}".format(1000*(e.energy-base_energy)/int(formulaunit)),
                         "{:.5f}".format(e.energy_per_atom),
                         delta_vol))
        energy_diff.append("{:.5f}".format(1000*(e.energy-base_energy)/int(formulaunit)))

    if len(all_data) > 0:
        headers = ("Directory", "Formula", "Energy", "Energy Diff (meV)/F.U.","E/Atom", "% vol chg")
        t = PrettyTable(headers)
        t.align["Directory"] = "l"
        for d in all_data:
            logging.debug('data row in all data is: \n {}'.format(d))
            t.add_row(d)
        print(t)
        print(msg)
    else:
        print("No valid vasp run found.")

    if hull:
        print 'Energy above hull is: \n'
        print map(lambda x: x.encode('ascii'), energy_diff)


def get_magnetizations(mydir, ion_list):
    data = []
    max_row = 0
    for (parent, subdirs, files) in os.walk(mydir):
        for f in files:
            if re.match("OUTCAR*", f):
                try:
                    row = []
                    fullpath = os.path.join(parent, f)
                    outcar = Outcar(fullpath)
                    mags = outcar.magnetization
                    mags = [m["tot"] for m in mags]
                    all_ions = list(range(len(mags)))
                    row.append(fullpath.lstrip("./"))
                    if ion_list:
                        all_ions = ion_list
                    for ion in all_ions:
                        row.append(str(mags[ion]))
                    data.append(row)
                    if len(all_ions) > max_row:
                        max_row = len(all_ions)
                except:
                    pass

    for d in data:
        if len(d) < max_row + 1:
            d.extend([""] * (max_row + 1 - len(d)))
    headers = ["Filename"]
    for i in range(max_row):
        headers.append(str(i))
    print(str_aligned(data, headers))

def get_ave_magnetization(mydir,ave_list):


    ave_list_dic = {}
    data = []
    keylist = []

    if ave_list:
        for key in ave_list:
            (start, end) = [int(i) for i in re.split("-", key)]
            value = list(range(start, end + 1))
            ave_list_dic[key] = value
            keylist.append(key)
            logging.debug('Key value is {}'.format(key))
    else:
        keylist.append('Average All')
        logging.debug('Key value is {}'.format(keylist))

    for (parent, subdirs, files) in os.walk(mydir):
        for f in files:
            if re.match("OUTCAR*", f):
                try:
                    row = []
                    fullpath = os.path.join(parent, f)
                    outcar = Outcar(fullpath)
                    mags = outcar.magnetization
                    mags = [m["tot"] for m in mags]
                    all_ions = list(range(len(mags)))
                    row.append(fullpath.lstrip("./"))

                    if ave_list:
                        for ele in keylist:
                            all_ions = ave_list_dic[ele]
                            magdata = []
                            logging.debug('ion list is {}\n'.format(all_ions))
                            for ion in all_ions:
                                magdata.append(mags[ion])
                            avg_mag = sum(magdata)/len(magdata)
                            row.append(avg_mag)
                        data.append(row)

                    else:
                        magdata = []
                        for ion in all_ions:
                            magdata.append(mags[ion])
                        logging.debug('The magdata list is: {}'.format(magdata))
                        logging.debug('The magdata list length is: {}'.format(len(magdata)))
                        avg_mag = sum(magdata)/len(magdata)
                        row.append(avg_mag)
                        data.append(row)
                except:
                    pass

    headers = ["Filename"]
    headers.extend(keylist)
    print(str_aligned(data, headers))


def voltage_calculation(args):
#     if (verbose and not debug):
#         FORMAT = "%(relativeCreated)d msecs : %(message)s"
#         logging.basicConfig(level=logging.INFO, format=FORMAT)
#
#     elif debug:
#         logging.basicConfig(level=logging.DEBUG)
#
#     if not detailed:
#         drone = SimpleVaspToComputedEntryDrone(inc_structure=True)
#     else:
#         drone = VaspToComputedEntryDrone(inc_structure=True,
#                                          data=["filename",
#                                                "initial_structure"])
#
#     ncpus = multiprocessing.cpu_count()
#     logging.info("Detected {} cpus".format(ncpus))
#     queen = BorgQueen(drone, number_of_drones=ncpus)
#     if os.path.exists(SAVE_FILE) and not reanalyze:
#         msg = "Using previously assimilated data from {}.".format(SAVE_FILE) \
#             + " Use -f to force re-analysis."
#         queen.load_data(SAVE_FILE)
#     else:
#         if ncpus > 1:
#             queen.parallel_assimilate(rootdir)
#         else:
#             queen.serial_assimilate(rootdir)
#         msg = "Analysis results saved to {} for faster ".format(SAVE_FILE) + \
#               "subsequent loading."
#         queen.save_data(SAVE_FILE)
#
#     entries = queen.get_data()
    pass

def parse_vasp(args):

    default_energies = not (args.get_energies or args.ion_list or args.ion_avg_list)

    if args.get_energies or default_energies:
        for d in args.directories:
            get_energies(d, args.reanalyze, args.verbose,
                         args.detailed, args.sort[0],args.formulaunit,args.debug,args.hull)
    if args.ion_list:
        if args.ion_list[0] == "All":
            ion_list = None
        else:
            (start, end) = [int(i) for i in re.split("-", args.ion_list[0])]
            ion_list = list(range(start, end + 1))
        for d in args.directories:
            get_magnetizations(d, ion_list)

    #Return a dic to store the average value of mag and relative ion list
    if args.ion_avg_list:

        if args.debug:
            logging.basicConfig(level=logging.DEBUG)

        if args.ion_avg_list[0] == "All":
            ion_list = None
        else:
            ion_list = args.ion_avg_list
        for d in args.directories:
            get_ave_magnetization(d,ion_list)

        logging.info('The passed in ion_avg_list is {}\n'.format(args.ion_avg_list))
        # logging.debug('The length of passed in ion_avg_list is{}\n'.format(len(args.ion_avg_list)))

        pass



def main():
    parser = argparse.ArgumentParser(description="""
    pmg is a convenient script that uses pymatgen to perform many
    analyses, plotting and format conversions. This script works based on
    several sub-commands with their own options. To see the options for the
    sub-commands, type "pmg sub-command -h".""",
                                     epilog="""
    Author: Shyue Ping Ong
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    subparsers = parser.add_subparsers()

    parser_vasp = subparsers.add_parser("analyze", help="Vasp run analysis.")
    parser_vasp.add_argument("directories", metavar="dir", default=".",
                             type=str, nargs="*",
                             help="directory to process (default to .)")
    parser_vasp.add_argument("-e", "--energies", dest="get_energies",
                             action="store_true", help="Print energies")
    parser_vasp.add_argument("-hu", "--hull", dest="hull",
                             action="store_true", help="Print energies above lowest structure list")
    parser_vasp.add_argument("-m", "--mag", dest="ion_list", type=str, nargs=1,
                             help="Print magmoms. ION LIST can be a range "
                             "(e.g., 1-2) or the string 'All' for all ions.")
    parser_vasp.add_argument("-f", "--force", dest="reanalyze",
                             action="store_true",
                             help="Force reanalysis. Typically, vasp_analyzer"
                             " will just reuse a vasp_analyzer_data.gz if "
                             "present. This forces the analyzer to reanalyze "
                             "the data.")
    parser_vasp.add_argument("-v", "--verbose", dest="verbose",
                             action="store_true",
                             help="verbose mode. Provides detailed output on "
                             "progress.")
    parser_vasp.add_argument("-d", "--detailed", dest="detailed",
                             action="store_true",
                             help="Detailed mode. Parses vasprun.xml instead "
                             "of separate vasp input. Slower.")
    parser_vasp.add_argument("-s", "--sort", dest="sort", type=str, nargs=1,
                             default=["energy_per_atom"],
                             help="Sort criteria. Defaults to energy / atom.")

    parser_vasp.add_argument("-fu", "--formulaunit", dest="formulaunit", type=str,
                             default=1,
                             help="Formula unit defined by user")

    parser_vasp.add_argument("-avl", "--averlist", dest="ion_avg_list", type=str, nargs='*',
                             help="Return average magmons value of ions. ION LIST can be a range "
                             "(e.g., 1-2, 3-4) or the string 'All' for all ions.")

    parser_vasp.add_argument("-db", "--debug", dest="debug", action="store_true",
                             help="Debug mode, provides information used for debug")
    parser_vasp.set_defaults(func=parse_vasp)

    parser_voltage = subparsers.add_parser("voltage", help="Run analysis and get voltage plateau")
    parser_voltage.add_argument("directories", metavar="dir", default=".",
                             type=str, nargs="*",
                             help="directory to process (default to .)")
    parser_voltage.add_argument("-ak", "--alkali", dest="alkali", type=str,
                             help="Alkali metal specified for voltage plateau calculation")
    parser_voltage.add_argument("-f", "--force", dest="reanalyze",
                             action="store_true",
                             help="Force reanalysis. Typically, vasp_analyzer"
                             " will just reuse a vasp_analyzer_data.gz if "
                             "present. This forces the analyzer to reanalyze "
                             "the data.")
    parser_voltage.add_argument("-v", "--verbose", dest="verbose",
                             action="store_true",
                             help="verbose mode. Provides detailed output on "
                             "progress.")
    parser_voltage.add_argument("-d", "--detailed", dest="detailed",
                             action="store_true",
                             help="Detailed mode. Parses vasprun.xml instead "
                             "of separate vasp input. Slower.")
    parser_voltage.add_argument("-fu", "--formulaunit", dest="formulaunit", type=int,
                             default=1,
                             help="Formula unit defined by user")
    parser_voltage.add_argument("-db", "--debug", dest="debug", action="store_true",
                             help="Debug mode, provides information used for debug")
    parser_voltage.set_defaults(func=voltage_calculation)




    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
