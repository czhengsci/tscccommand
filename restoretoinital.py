#!/usr/bin/env python

"""
Convenient job submit script for TSCC, which automatically generates
submission scripts and sends them to the queue.
"""

__author__ = "Chen Zheng"
__version__ = "1.0"
__email__ = "chz022@ucsd.edu"
__date__ = "Dec 5, 2014"

import os
import subprocess
import argparse


CWD = os.getcwd()


def proc_dir(d):

    dirname = os.path.abspath(d)
    restorepath = dirname +'/restore'

    os.chdir(d)
    subprocess.call('mkdir restore/',shell=True)
    subprocess.call('mv * restore/',shell=True)

    os.chdir(restorepath)
    subprocess.call('mv KPOINTS INCAR POSCAR POTCAR *.cif ../',shell=True)

    os.chdir(dirname)
    subprocess.call('rm -r restore',shell=True)
    #subprocess.call('cd ../',shell=True)
    #subprocess.call('rm -r restore',shell=True)

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

    args = parser.parse_args()


    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            #print 'parent is:'+ parent
            #print 'subdir is:'+ str(subdir)
            #print 'files is:' + str(files)
            proc_dir(d)
