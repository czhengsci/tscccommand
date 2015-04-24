#!/usr/bin/env python

__author__ = 'chenzheng'
"""
A convenience script for user usage .
"""

import os,fnmatch,csv,re
from monty.os import cd

def analysis(filepath):
    file = open(filepath,'r')
    matchdata=[]
    time = []
    for line in file:
        if re.search('chz022',line):
            matchline=line.rstrip()
            matchdata.append(matchline)
    for element in matchdata[0].split(' '):
        if re.search('-',element):
            time.append(element)

    return time

if __name__=='__main__':

    os.mkdir('CPU_Time_Analysis')
    with cd('CPU_Time_Analysis'):
        os.system('gstatement -p ong-group -s 2015-04-16 > report_analysis')
        analysis('report_analysis')



