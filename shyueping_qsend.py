#!/usr/bin/env python

"""
Convenient job submit script for TSCC, which automatically generates
submission scripts and sends them to the queue.
"""

__author__ = "Shyue Ping Ong"
__version__ = "1.0"
__email__ = "ongsp@ucsd.edu"
__date__ = "Oct 6, 2013"

import os
import subprocess
import argparse


SCRATCH_ROOT = "/oasis/tscc/scratch/"
CWD = os.getcwd()
SUBMIT_FNAME = "submit_script"
TEMPLATE = """#!/bin/bash
#PBS -q {queue}
#PBS -N {name}
#PBS -l nodes=1:ppn={nproc}:ib
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
    "run_vasp": 'run_vasp -c "mpirun -machinefile $PBS_NODEFILE -np {nproc} vasp" -z -s {scratch} relax relax',
    "run_vasp_md": 'run_vasp_md -c "mpirun -machinefile $PBS_NODEFILE -np {nproc} vasp" -z -s {scratch}',
}

pjoin = os.path.join


def proc_dir(d, queue, command, name, verbosity):
    name = name if name else "job"
    dirname = os.path.abspath(d)

    p = {
        "queue": queue,
        "account_name": "ong-group",
        "command": command,
        "name": name,
        "user": os.environ["USER"],
        "nproc": 16,
        "dir": dirname,
        "scratch": pjoin(SCRATCH_ROOT, os.environ["USER"]),
        "verbosity": verbosity
    }

    if queue == "home":
        p["group_list"] = "ong-group"
        p["walltime"] = "240:00:00"
    elif queue == "condo":
        p["group_list"] = "condo-group"
        p["walltime"] = "8:00:00"
    else: #glean queue
        p["group_list"] = "ong-group"
        p["walltime"] = "24:00:00"

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
                        choices=["home", "condo", "glean"],
                        help="Queue to send jobs to. Defaults to 'glean'. "
                             "Other option is 'condo' or 'home'.")
    parser.add_argument("-v", "--verbosity", dest="verbosity", type=str,
                        nargs="?", default="a", choices=["ae", "bae"],
                        help="Verbosity of the run. Standard PBS "
                             "notification settings. Options are a (abort "
                             "only - the default), ae (abort and end) and bae ("
                             "begin, abort and end).")
    parser.add_argument("-c", "--command", dest="command", type=str,
                        nargs="?", default="run_vasp",
                        choices=["run_vasp", "run_vasp_md"],
                        help="Command to run. Defaults to 'vasp'.")
    parser.add_argument("-n", "--name", dest="name", type=str,
                        nargs="?", default="",
                        help="Name for your jobs. Makes it easier to "
                             "identify which series of jobs they "
                             "belong to. Keep it short and crytic.")
    args = parser.parse_args()

    VASP_INPUT = set(["INCAR", "POSCAR", "POTCAR", "POSCAR"])

    for d in args.directories:
        for parent, subdir, files in os.walk(d):
            if set(files).issuperset(VASP_INPUT):
                proc_dir(parent, queue=args.queue, command=args.command,
                         name=args.name, verbosity=args.verbosity)