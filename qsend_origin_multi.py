#!/usr/bin/env python

"""
Convenient job submit script for TSCC, the template is the standard submit_script.
which automatically generates submission scripts and sends them to the queue.
"""


__author__ = 'chenzheng'
__version__ = "1.0"
__email__ = "chz022@ucsd.edu"
__date__ = "Apr 11, 2015"

import os
import subprocess
import argparse
from monty.tempfile import ScratchDir


SCRATCH_ROOT = "/oasis/tscc/scratch/"
CWD = os.getcwd()
SUBMIT_FNAME = "submit_script"


TEMPLATE = """#!/bin/bash
#PBS -q {queue}
#PBS -N {name}
#PBS -l nodes={nnodes}:ppn={nproc}:{ibswitch}
#PBS -l walltime={walltime}
#PBS -o vasp.out
#PBS -e {name}.err
#PBS -V
#PBS -M {user}@ucsd.edu
#PBS -m {verbosity}
#PBS -A {account_name}
#PBS -d {dir}

#To run vasp, load the VASP module first
#module load vasp scipy/2.7

CURR_DIR=`pwd`

#You should always run your calculations on the scratch space.
#The next three lines create a unique scratch directory.

SCRATCH={scratch}
mkdir $SCRATCH
cp * $SCRATCH
cd $SCRATCH

#This is the actual run command. VASP is run using mpirun.
mpirun -machinefile $PBS_NODEFILE -np {multinproc} /opt/vasp/5.2.12/openmpi_ib/bin/vasp

#This moves the completed calculation back to the working directory
mv * $CURR_DIR
"""


walltime_settings={
    'home':(24,240),
    'hotel':(24,168),
    'condo':(8,8),
    'glean':(24,240)
}


pjoin = os.path.join

tempscratch = pjoin(SCRATCH_ROOT, os.environ["USER"])


def proc_dir(d, queue, name, verbosity, numnodes, ibswitch, walltime):
    name = name if name else "job"
    dirname = os.path.abspath(d)
    with ScratchDir(tempscratch, create_symbolic_link=True, copy_to_current_on_exit=True, copy_from_current_on_enter=True) as temp_dir:
        scratch = temp_dir



    p = {
        "queue": queue,
        "account_name": "ong-group",
        "name": name,
        "user": os.environ["USER"],
        "nproc": 16,
        "dir": dirname,
        "scratch": scratch,
        "verbosity": verbosity,
        "nnodes":numnodes,
        "ibswitch":ibswitch
    }

    if queue == "home":
        p["group_list"] = "ong-group"
        # p["walltime"] = "240:00:00"
    elif queue == "condo":
        p["group_list"] = "condo-group"
        # p["walltime"] = "8:00:00"
    elif queue == 'hotel':
        p["group_list"] = "ong-group"
        # p["walltime"] = "168:00:00"
    else: #glean queue
        p["group_list"] = "ong-group"
        # p["walltime"] = "24:00:00"


    p['multinproc'] = 16*numnodes

    p['walltime']= '%d:00:00'% walltime

    with open(pjoin(d, SUBMIT_FNAME), "w") as f:
        f.write(TEMPLATE.format(**p))
    os.chdir(d)
    subprocess.call(["qsub", SUBMIT_FNAME])
    print "{} submitted to {}".format(d, queue)
    os.chdir(CWD)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
        qsend is a convenient script for submitting jobs using templates on
        TSCC. Currently mainly for VASP jobs.""",
        epilog="""
    Author: Shyue Ping Ong
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    parser.add_argument("directories", metavar="dir",
                        type=str, nargs="+",
                        help="directories to process")
    parser.add_argument("-q", "--queue", dest="queue", type=str,
                        nargs="?", default="glean",
                        choices=["home", "condo", "glean",'hotel'],
                        help="Queue to send jobs to. Defaults to 'glean'. "
                             "Other option is 'condo' or 'home' or 'hotel'.")
    parser.add_argument("-v", "--verbosity", dest="verbosity", type=str,
                        nargs="?", default="bae", choices=["ae", "bae"],
                        help="Verbosity of the run. Standard PBS "
                             "notification settings. Options are a (abort "
                             "only - the default), ae (abort and end) and bae ("
                             "begin, abort and end).")

    parser.add_argument("-n", "--name", dest="name", type=str,
                        nargs="?", default="",
                        help="Name for your jobs. Makes it easier to "
                             "identify which series of jobs they "
                             "belong to. Keep it short and crytic.")
    parser.add_argument('-nod','--numnodes',dest='nnodes',type=int,
                        nargs="?",default='1',help='Command to setup number of nodes.')

    parser.add_argument("-ib", "--ibswitch", dest="ibswitch", type=str,
                        choices=['ib','ib:ibswitch3','ib:ibswitch4','ib:rack1','ib:rack2'],
                        nargs="?", default="ib",
                        help="Command to setup ibswitch. Defaults to 'ib'")

    parser.add_argument("-w", "--walltime", dest="walltime", type=int,
                        nargs="?", default=None,
                        help="Provide a walltime for the job in hours. "
                             "Defaults are specified for each queue. But for "
                             "the hotel queue, you must specify a walltime.")


    args = parser.parse_args()

    VASP_INPUT = set(["INCAR", "POSCAR", "POTCAR", "POSCAR"])

    queue = args.queue

    print('%s queue selected.'% queue)

    walltime = args.walltime

    if walltime is None:
        walltime = walltime_settings[queue]
        print("Default walltime for queue used. You can "
              "use the -w option to specify any other number "
              "explicitly. The %s queue has a limit of %d hours. But be "
              "careful about running very long jobs." % (
            queue, walltime[1]))
        walltime = walltime[0]
    print("Walltime is set at %d hours." % walltime)
    print("")

    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            if set(files).issuperset(VASP_INPUT):
                proc_dir(parent, queue=args.queue,
                         name=args.name, verbosity=args.verbosity, numnodes=args.nnodes,
                         ibswitch=args.ibswitch,walltime=walltime)