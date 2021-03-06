#!/usr/bin/env python

__author__ = "Chen Zheng"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__status__ = "Personal use"
__version__ = "2.0"
__date__ = "Jan 18, 2015"

import argparse
import os
import subprocess

# Specific file existance checking function, function for CONTCAR.relax2.gz checking
def check_existance_of_relax2CONTCAR(args):
    filepath = args.subdirectory + '/CONTCAR.relax2.gz'
    return os.path.isfile(filepath)

def folder_move(dict,dest):

    command = 'mv ' + dict + ' ' + dest
    subprocess.call(command,shell=True)

#Function we used to check existance of CONTCAR.relax2.gz file and move the folder to
#Desired folder if we specified move option in argument
#Two arguments could be specified to set moving option different condition
def existance_check_call(directory,files,args):

    if 'CONTCAR.relax2.gz' in files:
        print 'CONTCAR.relax2.gz exist in subdir: ' + directory
        if args.store == 'Yes':
            folder_move(directory,args.storedirectory)
    else:
        print 'WARNING!!!!!!  CONTCAR.relax2.gz did not exist in subdir: ' + directory
        if args.move == 'Yes':
            if os.path.exists(args.movedirectory):
                folder_move(directory,args.movedirectory)
            else:
                command = 'mkdir ' + args.movedirectory
                subprocess.call(command,shell=True)
                folder_move(directory,args.movedirectory)


#This is the function we used for file existance checking
def call_check_file_existance(args):

    #Counter to count number of folder contains CONTCAR.relax2.gz
    counter = 0
    if args.direrange:
        for i in range(args.direrange):

            subdir = args.directory + '%d'%i

            if os.path.exists(subdir):
                args.subdirectory = subdir

                if check_existance_of_relax2CONTCAR(args):
                    #print 'CONTCAR.relax2.gz exist in subdir: ' + args.subdirectory
                    counter += 1
                    #if args.move == 'Yes': folder_move(subdir,args.movedirectory)
                else:
                    print 'WARNING!!!!!!  CONTCAR.relax2.gz did not exist in subdir: ' + args.subdirectory
                    if args.move == 'Yes': folder_move(subdir,args.movedirectory)

            else:
                print subdir + ' dose not exist in the folder during iteration'

    elif args.subdirectory:

        if check_existance_of_relax2CONTCAR(args):
            print 'CONTCAR.relax2.gz exist in subdir: ' + args.subdirectory
            #if args.move == 'Yes': folder_move(args.subdirectory,args.movedirectory)
        else:
            print 'WARNING!!!!!!  CONTCAR.relax2.gz did not exist in subdir: ' + args.subdirectory
            if args.move == 'Yes': folder_move(args.subdirectory,args.movedirectory)

    else:
       print "No subdirectory folder index provided"

    print 'Number of sub-folders contain CONTCAR.relax2.gz is {}.'.format(counter)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""
    This is a simple script for file existance checking, could provide either
    1. Parent directory name and number of sub-directory for iterating
    2. subdirectory name for iterating along""",
    epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("directories", metavar="dir",type=str, nargs="+",help="directories to process")

    parser.add_argument('-d', "--directory", metavar="dir", type=str,
                        help="directory containing file existance checking process")
    parser.add_argument("-r", "--direrange",type=int, help="Range of folder id need to iterate")
    parser.add_argument("-s", "--subdirectory",metavar="dir",type=str,help="subdirectory to iterate for stability checking")
    parser.add_argument("-me", "--move",type=str,choices=["No", "Yes"],default='No',help="Option to move folder that does not \
                        contain CONTCAR.Relax2.gz to other directory specified in argument movedirectory ")
    parser.add_argument("-st", "--store",type=str,choices=["No", "Yes"],default='No',help="Option to move folder that does \
                        contain CONTCAR.Relax2.gz to other directory specified in argument storedirectory")
    parser.add_argument("-mvdic", "--movedirectory",metavar="dir",type=str,help="subdirectory to move folder that does not contain\
                                                                                CONTCAR.relax2 file")
    parser.add_argument("-stdic", "--storedirectory",metavar="dir",type=str,help="directory to move folder that does contain\
                        CONTCAR.relax2 file to")



    args = parser.parse_args()
    #calculate_phase_stability(args)
    # call_check_file_existance(args)
    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            existance_check_call(d,files,args)
            print 'The subdirectory is: {}'.format(d)
            print 'The files in subdirectory are: {}'.format(d)
