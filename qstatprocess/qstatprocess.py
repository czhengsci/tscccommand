#!/usr/bin/env python

"""
Convenient qstat checking and information process
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
import numpy as np

pjoin = os.path.join
STATUSFILENAME = 'status'
RESULTFILE = 'status_result.txt'
DELIMITER = '\n---------------------------***********************--------------------------------\n'

def node_status_check(args):

    k = False
    b = []

    if not args.directories:

        CWD = os.getcwd()
        statusfilepath = CWD + '/qstatus'

        if not os.path.exists(statusfilepath):
            mkdircommand = 'mkdir ' + statusfilepath
            subprocess.call(mkdircommand,shell=True)

        os.chdir(statusfilepath)
        subprocess.call('qstat -u chz022 > status',shell=True)

    else:
        statusfilepath = os.path.abspath(args.directories)

    file = open(pjoin(statusfilepath,STATUSFILENAME),'r')
    resultfile = open(pjoin(statusfilepath,RESULTFILE),'w')
    lines = file.readlines()

    #Create job info array for further data extraction
    for i in range(0,len(lines)):
        line = lines[i]

        if k and not re.match('(.*)-----(.*)',line):
            b.append(line.split())

        if 'Job ID' in line:
            list1 = lines[i].split()
            b.append(list1)
            k = True
            #print DELIMITER

    a=np.array(b)

    #get Job ID part from array with status = 'Q'
    for j in range(0,len(a)):
        if a[j][9] == 'Q' and a[j][3] =='N0.75_GGA':
            jobid = a[j][0].split('.')[0]
            resultfile.write('Job ID of status Q and N0.75_GGA is {}'.format(jobid))
            command = 'qdel '+ str(jobid)
            subprocess.call(command,shell=True)
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