#!/usr/bin/env python

__author__ = 'chenzheng'
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__status__ = "Personal use"
__version__ = "1.0"
__date__ = "Apr 23, 2015"
"""
A convenience script for user usage .
"""

import os,fnmatch,csv,re
from monty.os import cd
import logging
import argparse

def analysis(filepath,debug):

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    file = open(filepath,'r')
    matchdata=[]
    time = []
    for line in file:
        if re.search('chz022',line):
            logging.debug('Found line with chz022 {}'.format(line))

            for element in line.split(' '):
                m = re.match("-*",m)
                time.append(m)
            matchline=line.rstrip()
            matchdata.append(matchline)

    logging.debug('The use time is: {}'.format(time))
    return time

if __name__=='__main__':

    parser = argparse.ArgumentParser(description="""
    This is a simple script for chen's CPU usage checking""",
    epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument('-db', "--debug", action="store_true",
                        help="set for debug info ")

    args = parser.parse_args()

    os.mkdir('CPU_Time_Analysis')
    with cd('CPU_Time_Analysis'):
        os.system('gstatement -p ong-group -s 2015-04-16 > report_analysis')
        analysis('report_analysis',args.debug)



