#!/usr/bin/env python

"""
A master convenience script with many tools for vasp and structure analysis.
"""

__author__ = "Chen Zheng"
__copyright__ = "Copyright 2014, Personal use"
__version__ = "1.0"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__date__ = "Dec 23, 2014"

import argparse
import os

def Check_CONTCAR_Relax2_File():


def Energy_Proxifilter_profile():



def Stability_Check():


def Restore_to_Initial_Vasp_set()



def main():
    parser = argparse.ArgumentParser(description="""
    tscc_master is a convenient script that perform many
    tscc folder operation, stability_check and energy_proxifilter analysis. This script works based on
    several sub-commands with their own options. To see the options for the
    sub-commands, type "pmg sub-command -h".""",
                                     epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    subparsers = parser.add_subparsers()

    #Block Shyue Ping used subparser
    parser_vasp = subparsers.add_parser("analyze", help="Vasp run analysis.")
    parser_vasp.add_argument("directories", metavar="dir", default=".",
                             type=str, nargs="*",
                             help="directory to process (default to .)")
    parser_vasp.add_argument("-e", "--energies", dest="get_energies",
                             action="store_true", help="Print energies")
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
    parser_vasp.set_defaults(func=parse_vasp)



    #Check CONTCAR.relax2 file existence
    parser_contcar = subparsers.add_parser('contcar_2',help='Run CONTCAR check.')
    parser_contcar.add_argument("directories", metavar="dir",type=str, nargs="+",
                                help="directories to process")
    parser_contcar.add_argument("-me", "--move",type=str,choices=["No", "Yes"],
                                default='No',help="choices about whether move file to"
                                                  "a new folder")
    parser_contcar.add_argument("-mvdic", "--movedirectory",metavar="dir",
                                type=str,help="subdirectory to move folder that "
                                              "does not contain CONTCAR.relax2 file")



    #To Initiate args
    args = parser.parse_args()
    args.func(args)



if __name__=='__main__':
    main()
