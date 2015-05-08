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
from monty.os import cd
import logging


def submit_command(args,entry):
    var_dic = vars(args)

    logging.debug(var_dic)
    logging.debug('Wall time is none is: {}'.format(var_dic['walltime']==None))

    subcommand = 'qsend_multi {} -q {} -v {} -c {} -n {} -nod {} -ib {} -w {}'.format(entry,var_dic['queue'],
                                                                                        var_dic['verbosity'], var_dic['command'],
                                                                                        var_dic['name'], var_dic['nnodes'],
                                                                                        var_dic['ibswitch'],var_dic['walltime'])
    logging.debug('Resub command is: \n {}'.format(subcommand))

    return subcommand



#This is a funciton we used for check, restore and resub job using PBS system
#Integrate with check_CONTCARRElax command

def check_resub_relax2(args):



    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


    dir_entry = parse_entry(args)
    for ele in dir_entry:

        with cd(ele):

            logging.debug('Current dir path is: {}'.format(os.getcwd()))

            if not os.path.exists('Complete'):
                os.makedirs('Complete')

            exclude = set(['Complete'])

            result_dir_entry = [f for f in os.listdir('.') if f not in exclude]

            for subdir in result_dir_entry:
                check_command = 'check_CONTCARRELAX2 {} -st Yes -stdic Complete/'.format(subdir)
                subprocess.call(check_command,shell=True)

            no_relax2_file = [f for f in os.listdir('.') if f not in exclude]

            for dir_ele in no_relax2_file:
                resub_command = submit_command(args,dir_ele)
                restore_command = 'restoretoinital {}'.format(dir_ele)
                subprocess.call(restore_command,shell=)
                subprocess.call(resub_command,shell=True)


            logging.debug('Folder with no_relax2_file is: {}'.format(no_relax2_file))




#Function for parsing directories and return with target directories entry to be analysis
def parse_entry(args):

    rootpath = args.directories[0].rstrip('/')
    pathdepth = glob.glob(rootpath+'/*'*int(args.depth))
    subdir_list = filter(lambda f: os.path.isdir(f),pathdepth)

    logging.debug('The directory contained in the path directory is: {}'.format(subdir_list))
    # logging.debug('The type of subdir_list parameter is:{}'.format(type(subdir_list)))

    return subdir_list


def main():
    parser = argparse.ArgumentParser(description="""
    pmg is a convenient script that uses pymatgen to perform many
    analyses, plotting and format conversions. This script works based on
    several sub-commands with their own options. To see the options for the
    sub-commands, type "pmg sub-command -h".""",
                                     epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    subparsers = parser.add_subparsers()

    parser_resub = subparsers.add_parser("relaxresub", help="Resub job based on existing of relax2 file.")

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

    parser_resub.add_argument("-q", "--queue", dest="queue", type=str,
                                nargs="?", default="glean",
                                choices=["home", "condo", "glean",'hotel'],
                                help="Queue to send jobs to. Defaults to 'glean'. "
                                     "Other option is 'condo' or 'home' or 'hotel'.")
    parser_resub.add_argument("-v", "--verbosity", dest="verbosity", type=str,
                                nargs="?", default="bae", choices=["ae", "bae"],
                                help="Verbosity of the run. Standard PBS "
                                     "notification settings. Options are a (abort "
                                     "only - the default), ae (abort and end) and bae ("
                                     "begin, abort and end).")
    parser_resub.add_argument("-c", "--command", dest="command", type=str,
                                nargs="?", default="run_vasp",
                                choices=["run_vasp", "run_vasp_md","run_vasp_glean",'run_vasp_single'],
                                help="Command to run. Defaults to 'vasp'.")

    parser_resub.add_argument("-n", "--name", dest="name", type=str,
                                nargs="?", default="jobs",
                                help="Name for your jobs. Makes it easier to "
                                     "identify which series of jobs they "
                                     "belong to. Keep it short and crytic.")
    parser_resub.add_argument('-nod','--numnodes',dest='nnodes',type=int,
                                nargs="?",default='1',help='Command to setup number of nodes.')

    parser_resub.add_argument("-ib", "--ibswitch", dest="ibswitch", type=str,
                                choices=['ib','ib:ibswitch3','ib:ibswitch4','ib:rack1','ib:rack2'],
                                nargs="?", default="ib",
                                help="Command to setup ibswitch. Defaults to 'ib'")

    parser_resub.add_argument("-w", "--walltime", dest="walltime", type=int,
                                nargs="?", default=None,
                                help="Provide a walltime for the job in hours. "
                                     "Defaults are specified for each queue. But for "
                                     "the hotel queue, you must specify a walltime.")


    parser_resub.set_defaults(func=check_resub_relax2)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

