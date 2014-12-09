#!/usr/bin/env python

"""
Convenient node checking and information process
"""

__author__ = "Chen Zheng"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__status__ = "Personal use"
__version__ = "1.0"
__date__ = "Dec 8, 2014"


import os
import subprocess
import re
import argparse

pjoin = os.path.join
NODEFILENAME = 'node'
RESULTFILE = 'node_result.txt'
DELIMITER = '---------------------------***********************--------------------------------\n'

def node_status_check(args):

    nodedir = {}

    if not args.directories:

        CWD = os.getcwd()
        nodefilepath = CWD + '/nodes'

        if not os.path.exists(nodefilepath):
            mkdircommand = 'mkdir ' + nodefilepath
            subprocess.call(mkdircommand,shell=True)

        os.chdir(nodefilepath)
        subprocess.call('pbsnodes > node',shell=True)

    else:
        nodefilepath = os.path.abspath(args.directories)

    #print nodefilepath

    file = open(pjoin(nodefilepath,NODEFILENAME),'r')
    resultfile = open(pjoin(nodefilepath,RESULTFILE),'w')
    lines = file.readlines()

    for i in range(0,len(lines)):
        line = lines[i]
        if 'state = free' in line:
            k = i - 1
            i += 2
            stateline = line
            if re.match('(.*)glean-node(.*)',lines[i]) and not re.match('(.*)gpu(.*)',lines[i])\
                    and not re.match('(.*)noglean(.*)',lines[i]):
                resultfile.write('\n')
                resultfile.write(lines[k])
                resultfile.write(lines[i])
                resultfile.write(DELIMITER)

    resultfile.close()
    file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        restore is a convenient script for vasp input file restore.""",
        epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("-dir","--directories", metavar="dir",
                        type=str, nargs="?",
                        help="directories path that have node in it to process")

    args = parser.parse_args()

    #print(args.directories)
    node_status_check(args)






