#!/usr/bin/env python

"""
#TODO: Write module doc.
"""

from __future__ import division

__author__ = 'Chen Zheng'
__copyright__ = 'Copyright 2013, The Materials Virtual Lab'
__version__ = '0.1'
__maintainer__ = 'Chen Zheng'
__email__ = 'chz022@ucsd.edu'
__date__ = '12/30/15'

import os
import argparse
import itertools
import logging
import glob
import sys
import subprocess

from bson.objectid import ObjectId
import numpy as np
import collections

from monty.os import cd
from monty.serialization import loadfn

from pymatgen.io.vaspio import Vasprun
from pymacy.md.parse import MDDBManager, update_all_analysis

from fireworks.fw_config import LAUNCHPAD_LOC, CONFIG_FILE_DIR
from fireworks.scripts.lpad_run import get_lp


FORMAT = '%(asctime)-15s %(message)s'
logger = logging.getLogger(__name__)

def validate(path):

    files = os.listdir(path)

    if ('vasprun.xml.relax1' in files) or ('vasprun.xml.relax2' in files):
        return True
    else:
        return False


def revive(args):
    lp = get_lp(args)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)


    ids = []

    if args.fw_id:
        query = {'nodes': {"$in": args.fw_id}}
        id_add = lp.get_wf_ids(query)
        ids.extend(id_add)

    elif args.states:
        for state in args.states:
            query = {'state':state}
            id_add = lp.get_wf_ids(query)
            ids.extend(id_add)

    for wfid in ids:
        d = lp.get_wf_summary_dict(wfid,'reservations')
        to_check = []
        print d


        #Add firetask with desired state to checklist
        for k, v in d["states"].items():
            if v in args.states:
                to_check.append(k)

        logging.debug('Check state task is: {}'.format(to_check))

        dead = []

        for k in to_check:
            state = 'Not found'
            for l in d["launches"][k]:
                qid = l["state_history"][0]["reservation_id"]
                try:
                    qstat = subprocess.check_output(["qstat", "-f", qid])
                    for l in qstat.split("\n"):
                        toks = l.split("=")
                        if toks[0].strip() == "job_state":
                            state = toks[1].strip()
                            break
                except subprocess.CalledProcessError:
                    pass
            name, fw_id = k.split("--")
            fw_id = int(fw_id)
            if state not in ["Q", "R"]:
                print "%s with fw_id %d is dead. qid %s not found..." % (
                    name, fw_id, qid)
                dead.append(fw_id)
            else:
                print "%s with fw_id %d is in state %s with qid %s..." % (
                    name, fw_id, state, qid)

        if len(dead) > 0:
            print("Fw ids %s are dead..." % dead)
            r = "y" if args.force else raw_input("Rerun? (y/n) " % dead)
            if r == "y":
                for i in dead:
                    lp.rerun_fw(i)


    logger.debug("State fw id is: {}".format(ids))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Tools for relaxation revive.""",
        epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))


    subparsers = parser.add_subparsers()

    parser_revive = subparsers.add_parser("revive",
                                          help="Revive killed runs.")
    fw_id_args = ["-i", "--fw_id"]
    fw_id_kwargs = {"type": int, "nargs": "+", "help": "fw_id"}


    # parser_revive.add_argument(
    #     "-ids", "--fw_id", dest="fw_id", type=int, nargs="+",
    #     help="Fw id to retrive")
    #
    # parser_revive.add_argument(
    #     "-i", "--wfids", dest="wfids", type=int, nargs="+",
    #     help="Wflow id to revive. Searches for killed fireworks in that "
    #          "workflow.")
    parser_revive.add_argument(*fw_id_args, **fw_id_kwargs)

    parser_revive.add_argument(
        '-l', '--launchpad_file',
        help='path to LaunchPad file containing central DB connection info',
        default=LAUNCHPAD_LOC)
    parser_revive.add_argument(
        '-c', '--config_dir',
        help='path to a directory containing the LaunchPad file (used if -l unspecified)',
        default=CONFIG_FILE_DIR)
    parser_revive.add_argument(
        '-f', '--force', action='store_true',
        help='Skip validation and immediately perform revive.')
    parser_revive.add_argument(
        '-s', '--states', dest="states", type=str.upper, nargs="+", default=[
            "RUNNING", "FIZZLED"],
        help='States to revive. Defaults only to running.')
    parser_revive.add_argument("-db", "--debug", dest="debug", action="store_true",
                             help="Debug mode")

    parser_revive.set_defaults(func=revive)

    args = parser.parse_args()
    args.func(args)