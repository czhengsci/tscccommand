#!/usr/bin/env python

"""
Convenient CONTCAR.relax2 file copy from TSCC to local script.
"""

__author__ = "Chen Zheng"
__version__ = "1.0"
__email__ = "chz022@ucsd.edu"
__date__ = "Dec 16, 2014"

import os
import subprocess
import argparse


CWD = os.getcwd()


def Contcar_copy(args):

    #Counter to count the number of file copied with CONTCAR.relax2.gz
    counter = 0

    #Check the existance of local copied to folder and scp CONTCAR.relax2 file to local subfolder
    if args.direrange:
        for i in range(args.direrange):

            subdir = args.directory + '%d'%i
            cpcommandtemp = 'scp chz022@tscc.sdsc.edu:{}/CONTCAR.relax2.gz .'.format(subdir)
            localfolderpath = args.localfolder + '%d'%i

            if os.path.exists(localfolderpath):
                os.chdir(localfolderpath)
                subprocess.call(cpcommandtemp,shell=True)
                subprocess.call('gunzip CONTCAR.relax2.gz',shell=True)
                os.chdir(CWD)
                counter += 1

            else:
                mkdircommandtemp = 'mkdir {}'.format(localfolderpath)
                subprocess.call(mkdircommandtemp,shell=True)
                os.chdir(localfolderpath)
                subprocess.call(cpcommandtemp,shell=True)
                subprocess.call('gunzip CONTCAR.relax2.gz',shell=True)
                os.chdir(CWD)
                counter += 1

    print 'Number of CONTCAR.relax2 files copied to local is: '+str(counter)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This is a simple script for copy cont, could provide either
    1. Parent directory name and number of sub-directory for iterating
    2. subdirectory name for iterating along""",
    epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument('-d', "--directory", metavar="dir", type=str,
                        help="directory containing file existance checking process")
    parser.add_argument("-r", "--direrange",type=int, help="Range of folder id need to iterate")
    parser.add_argument("-loc", "--localfolder",type=str, help="Local folder name")

    args = parser.parse_args()
    #call Contcar_copy function
    Contcar_copy(args)