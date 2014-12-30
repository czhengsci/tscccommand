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
NODEFILENAME = 'qlist'
RESULTFILE = 'qlist_sublist'
DELIMITER = '---------------------------***********************--------------------------------\n'

def qkill_multi(args):

    nodedir = {}

    if not args.directories:

        CWD = os.getcwd()
        qkillfilepath = CWD + '/qkill_multi'

        if not os.path.exists(qkillfilepath):
            mkdircommand = 'mkdir ' + qkillfilepath
            subprocess.call(mkdircommand,shell=True)

        os.chdir(qkillfilepath)
        subprocess.call('qstat -u chz022 > qlist',shell=True)

    else:
        qkillfilepath = os.path.abspath(args.directories)

    #print qkillfilepath

    file = open(pjoin(qkillfilepath,NODEFILENAME),'r')
    resultfile = open(pjoin(qkillfilepath,RESULTFILE),'w')
    lines = file.readlines()

    for startline in range(5,len(lines)):
        line = lines[startline]
        linetowrite = line.split()
        jobid = linetowrite[0][:7]
        killcommand = 'qdel ' + jobid
        #print linetowrite
        resultfile.write('\n')
        if linetowrite[9] != 'R':
            resultfile.write(jobid)
            subprocess.call(killcommand,shell=True)
            resultfile.write(DELIMITER)
        else:
            print linetowrite

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

    parser.add_argument("-r","--range",
                        type=int, nargs="?",
                        help="qid start to kill")

    parser.add_argument("-dir","--directories", metavar="dir",
                        type=str, nargs="?",
                        help="directories path that to keep qid result")

    args = parser.parse_args()

    #print(args.directories)
    qkill_multi(args)
