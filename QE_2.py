#!/usr/bin/env python

"""
Convenient job submit script for TSCC, which automatically generates
submission scripts and sends them to the queue.
"""

__author__ = "Shyue Ping Ong", 'Chen Zheng'
__version__ = "1.0"
__email__ = "ongsp@ucsd.edu"
__date__ = "Jan 24, 2015"

import os
import subprocess
import argparse
import fnmatch


SCRATCH_ROOT = "/oasis/tscc/scratch/"
CWD = os.getcwd()
SUBMIT_FNAME = "submit_script"
TEMPLATE = """#!/bin/bash
#PBS -q {queue}
#PBS -N {name}
#PBS -l nodes={nnodes}:ppn={nproc}:{ibswitch}
#PBS -l walltime={walltime}
#PBS -o {command}.out
#PBS -e {name}.err
#PBS -V
#PBS -M {user}@ucsd.edu
#PBS -m {verbosity}
#PBS -A {account_name}
#PBS -d {dir}

module load vasp scipy/2.7
{master_command}
"""

commands = {
    "run_vasp": 'run_vasp -c "mpirun -machinefile $PBS_NODEFILE -np {multinproc} /opt/vasp/5.2.12/openmpi_ib/bin/vasp" -z -s {scratch} relax relax',

}

walltime_settings={
    'home':(24,240),
    'hotel':(24,168),
    'condo':(8,8),
    'glean':(24,240)
}


pjoin = os.path.join


def proc_dir(d, queue, command, name, verbosity, numnodes, ibswitch,walltime,fileset):
    name = name if name else "job"
    dirname = os.path.abspath(d)

    for files in fnmatch.filter(fileset, '*.pw.in'):
        inputfilename = files

    p = {
        "queue": queue,
        "account_name": "ong-group",
        "command": command,
        "name": name,
        "user": os.environ["USER"],
        "nproc": 16,
        "dir": dirname,
        "scratch": pjoin(SCRATCH_ROOT, os.environ["USER"]),
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

    # p["master_command"] = commands[command].format(**p) if queue != 'glean'\
    #     else commands['run_vasp_glean']
    p["master_command"] = commands[command].format(**p)

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
    parser.add_argument("-c", "--command", dest="command", type=str,
                        nargs="?", default="run_vasp",
                        choices=["run_vasp", "run_vasp_md","run_vasp_glean",'run_vasp_single'],
                        help="Command to run. Defaults to 'vasp'.")

    parser.add_argument("-n", "--name", dest="name", type=str,
                        nargs="?", default="jobs",
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

    HPC_Input = set(['Fe.pbe-spn-kjpaw_psl.0.2.1.UPF'])

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
    print("Selected command is " + commands[args.command])
    print("")

    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            if set(files).issuperset(HPC_Input):
                proc_dir(parent, queue=args.queue, command=args.command,
                         name=args.name, verbosity=args.verbosity, numnodes=args.nnodes,
                         ibswitch=args.ibswitch,walltime=walltime,fileset = files)
