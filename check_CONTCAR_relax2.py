__author__ = 'chenzheng'

#!/usr/bin/env python

__author__ = "Chen Zheng"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__status__ = "Personal use"
__version__ = "1.0"
__date__ = "Dec 4, 2014"

import argparse
import os

# Specific file existance checking function, function for CONTCAR.relax2.gz checking
def check_existance_of_relax2CONTCAR(args):
    filepath = args.subdirectory + '/CONTCAR.relax2.gz'
    return os.path.isfile(filepath)

#This is the function we used for file existance checking
def call_check_file_existance(args):

    #Counter to count the number of folders with CONTCAR.relax2.gz
    counter = 0

    #Check the existance of CONTCAR.relax2.gz use the working directory and sub-directory range passed in
    if args.direrange:
        for i in range(args.direrange):

            subdir = args.directory + '%d'%i

            if os.path.exists(subdir):
                args.subdirectory = subdir
                if check_existance_of_relax2CONTCAR(args):
                    counter += 1
                    print 'CONTCAR.relax2.gz exist in subdir: ' + args.subdirectory
                else:
                    print 'WARNING!!!!!!  CONTCAR.relax2.gz did not exist in subdir: ' + args.subdirectory
            else:
                print subdir + 'did not exists in the folder during iteration'

    # Check the existance of CONTCAR.relax2.gz use the subdirectory passed in, usually just check one directory
    if args.subdirectory:

        if check_existance_of_relax2CONTCAR(args):
            print 'CONTCAR.relax2.gz exist in subdir: ' + args.subdirectory
        else:
            print 'WARNING!!!!!!  CONTCAR.relax2.gz did not exist in subdir: ' + args.subdirectory

    else:
       print "No subdirectory folder index provided"

    print 'Number of folder contains CONTCAR.relax2.gz is: '+str(counter)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This is a simple script for file existance checking, could provide either
    1. Parent directory name and number of sub-directory for iterating
    2. subdirectory name for iterating along""",
    epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument('-d', "--directory", metavar="dir", type=str,
                        help="directory containing file existance checking process")
    parser.add_argument("-r", "--direrange",type=int, help="Range of folder id need to iterate")
    parser.add_argument("-s", "--subdirectory",metavar="dir",type=str,help="subdirectory to iterate for stability checking")

    args = parser.parse_args()
    #calculate_phase_stability(args)
    call_check_file_existance(args)