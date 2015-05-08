__author__ = 'chenzheng'


import argparse
import os
import re
import logging
import csv
import glob
import multiprocessing
from pymatgen.apps.borg.hive import SimpleVaspToComputedEntryDrone, \
    VaspToComputedEntryDrone
from pymatgen.apps.borg.queen import BorgQueen
from pymatgen.io.vaspio import Outcar, Vasprun, Chgcar
import numpy as np
from prettytable import PrettyTable

def group_directories(root_dir, group_depth):

    rootpath = root_dir[0].rstrip('/')
    pathdepth = glob.glob(rootpath+'/*'*int(group_depth))
    dirlistdepth = filter(lambda f: os.path.isdir(f),pathdepth)

    logging.debug('The directory contained in the path directory is: {}'.format(dirlistdepth))
    # logging.debug('The type of dirlistdepth parameter is:{}'.format(type(dirlistdepth)))

    return dirlistdepth


def assimilate(path):
    files = os.listdir(path)

    try:
        files_to_parse={}
        for filename in ("INCAR", "POTCAR", "POSCAR","KPOINTS"):
            files = glob.glob(os.path.join(path,filename))
            if len(files) !=4: continue







