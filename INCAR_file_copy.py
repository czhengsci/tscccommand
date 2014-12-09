#!/usr/bin/env python

"""
Convenient INCAR replacement script.
"""

__author__ = "Chen Zheng"
__version__ = "1.0"
__email__ = "chz022@ucsd.edu"
__date__ = "Dec 5, 2014"

import os
import subprocess
import argparse


CWD = os.getcwd()


def Incar_copy(d,args):

    Incarcopycommand = 'cp ' + str(args.pathofincar) + ' .'

    os.chdir(d)
    subprocess.call(Incarcopycommand,shell=True)
    os.chdir(CWD)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        restore is a convenient script for vasp input file restore.""",
        epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("directories", metavar="dir",
                        type=str, nargs="+",
                        help="directories to process")
    parser.add_argument('-Inc','--pathofincar',type=str, help='The path of INCAR file to pass in')

    args = parser.parse_args()
    print type(args.pathofincar)

    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            Incar_copy(d,args)

