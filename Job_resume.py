#!/usr/bin/env python

__author__ = "Chen Zheng"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__status__ = "Personal use"
__version__ = "2.0"
__date__ = "Jan 18, 2015"

import argparse
import os,glob
import subprocess
import monty
import logging

#This is a funciton we used for check, restore and resub job using PBS system
#Integrate with check_CONTCARRElax command
def check_resub_relax2(args):

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    dir_entry = parse_entry(args)
    for ele in dir_entry:

        with monty.os.cd(ele):

            logging.debug('Current dir path is: {}'.format(os.getcwd()))

            if not os.path.exists('Complete'):
                os.makedirs('Complete')

            exclude = set(['Complete'])

            result_dir_entry = [f for f in os.listdir('.') if f not in exclude]

            for subdir in result_dir_entry:
                check_command = 'check_CONTCARRELAX2 {} -st Yes -stdic Complete/'.format(subdir)
                subprocess.call(check_command,shell=True)

            no_relax2_file = [f for f in os.listdir('.') if f not in exclude]
            logging.debug('Folder with no_relax2_file is: {}'.format(no_relax2_file))

    pass


#Function for parsing directories and return with target directories entry to be analysis
def parse_entry(args):

    rootpath = args.dir[0].rstrip('/')
    pathdepth = glob.glob(rootpath+'/*'*int(args.depth))
    dirlistdepth = filter(lambda f: os.path.isdir(f),pathdepth)

    logging.debug('The directory contained in the path directory is: {}'.format(dirlistdepth))
    # logging.debug('The type of dirlistdepth parameter is:{}'.format(type(dirlistdepth)))

    return dirlistdepth


def main():
    parser = argparse.ArgumentParser(description="""
    pmg is a convenient script that uses pymatgen to perform many
    analyses, plotting and format conversions. This script works based on
    several sub-commands with their own options. To see the options for the
    sub-commands, type "pmg sub-command -h".""",
                                     epilog="""
    Author: Shyue Ping Ong
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    subparsers = parser.add_subparsers()

    parser_resub = subparsers.add_parser("relax_resub", help="Resub job based on existing of relax2 file")
    parser_resub.add_argument("directories", metavar="dir", default=".",
                             type=str, nargs="*",
                             help="directory to process (default to .)")
    parser_resub.add_argument("-dep",  "--depth", dest='depth', default="1",
                             type=str, nargs="?",
                             help="Depth level of children directory that will be group together")

    parser_resub.add_argument("-db", "--debug", dest="debug", action="store_true",
                             help="Debug mode, provides information used for debug")

    parser_resub.add_argument("-stdic", "--storedirectory",metavar="dir",type=str,
                              help="directory to move folder that does contain CONTCAR.relax2 file to")
    parser_resub.add_argument("-st", "--store",type=str,choices=["No", "Yes"],
                              default='No',help="Option to move folder that does contain CONTCAR.Relax2.gz to \
                              other directory specified in argument storedirectory")

    parser_resub.set_defaults(func=check_resub_relax2)






    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

