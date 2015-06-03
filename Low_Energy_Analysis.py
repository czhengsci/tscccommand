#!/usr/bin/env python

"""
A master script Chen used for generating vasp output analysis to CSV
"""


__author__ = "Chen Zheng"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Chen Zheng"
__email__ = "chz022@ucsd.edu"
__date__ = "May 3rd, 2015"


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


SAVE_FILE = "vasp_data.gz"


def get_energies(rootdir, reanalyze, verbose, detailed,
                 sort, formulaunit, debug, hull, threshold, args):

    ion_list = 'Novalue'
    ave_key_list = 'Novalue'
    threscount = 0

    """
    Doc string.
    """
    if (verbose and not debug):
        FORMAT = "%(relativeCreated)d msecs : %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)

    elif debug:
        logging.basicConfig(level=logging.DEBUG)

    if not detailed:
        drone = SimpleVaspToComputedEntryDrone(inc_structure=True)
    else:
        drone = VaspToComputedEntryDrone(inc_structure=True,
                                         data=["filename",
                                               "initial_structure"])

    ncpus = multiprocessing.cpu_count()
    logging.info("Detected {} cpus".format(ncpus))
    queen = BorgQueen(drone, number_of_drones=ncpus)
    if os.path.exists(SAVE_FILE) and not reanalyze:
        msg = "Using previously assimilated data from {}.".format(SAVE_FILE) \
            + " Use -f to force re-analysis."
        queen.load_data(SAVE_FILE)
    else:
        if ncpus > 1:
            queen.parallel_assimilate(rootdir)
        else:
            queen.serial_assimilate(rootdir)
        msg = "Analysis results saved to {} for faster ".format(SAVE_FILE) + \
              "subsequent loading."
        queen.save_data(SAVE_FILE)

    entries = queen.get_data()
    if sort == "energy_per_atom":
        entries = sorted(entries, key=lambda x: x.energy_per_atom)
    elif sort == "filename":
        entries = sorted(entries, key=lambda x: x.data["filename"])

    # logging.debug('First Energy entry is {}'.format(entries[0]))

    base_energy = entries[0].energy



    all_data = []
    energy_diff = []

    threshold=float(threshold)

    for e in entries:

        if not detailed:
            delta_vol = "{:.2f}".format(e.data["delta_volume"] * 100)
        else:
            delta_vol = e.structure.volume / \
                e.data["initial_structure"].volume - 1
            delta_vol = "{:.2f}".format(delta_vol * 100)


        entry_path = e.data['filename'].rsplit('/',1)[0]

        if args.nupdown:
            entry_data= [rootdir,e.data["filename"].replace("./", ""),
                             re.sub("\s+", "", e.composition.formula),
                             "{:.5f}".format(e.energy),
                             "{:.5f}".format(1000*(e.energy-base_energy)/int(formulaunit)),
                             "{:.5f}".format(e.energy_per_atom),
                             delta_vol,e.parameters['run_type'],
                             e.data['NUPDOWN']]
        else:
            entry_data= [rootdir,e.data["filename"].replace("./", ""),
                             re.sub("\s+", "", e.composition.formula),
                             "{:.5f}".format(e.energy),
                             "{:.5f}".format(1000*(e.energy-base_energy)/int(formulaunit)),
                             "{:.5f}".format(e.energy_per_atom),
                             delta_vol,e.parameters['run_type']]

        if args.ion_list:
            if args.ion_list[0] == "All":
                ion_list = None
            else:
                (start, end) = [int(i) for i in re.split("-", args.ion_list[0])]
                ion_list = list(range(start, end + 1))
            for d in entry_path:
                magdata = get_magnetization(d, ion_list)
                entry_data.extend(magdata)

        if args.ion_avg_list:
            ave_mag_data, ave_key_list = get_ave_magnetization(entry_path,args.ion_avg_list)
            entry_data.extend(ave_mag_data)

        if threshold != 0:
            all_data.append(entry_data)
            if float(entry_data[4])<threshold:
                threscount +=1

        elif threshold == 0:
            all_data.append(entry_data)

        energy_diff.append("{:.5f}".format(1000*(e.energy-base_energy)/int(formulaunit)))


    # if len(all_data) > 0:
    #     headers = ("Directory", "Formula", "Energy", "Energy Diff (meV)/F.U.","E/Atom", "% vol chg")
    #     t = PrettyTable(headers)
    #     t.align["Directory"] = "l"
    #     for d in all_data:
    #         logging.debug('data row in all data is: \n {}'.format(d))
    #         t.add_row(d)
    #     print(t)
    #     print(msg)
    # else:
    #     print("No valid vasp run found.")

    if hull:
        print 'Analyzing group: {}\n'.format(rootdir)
        print 'Energy above hull is: \n'
        print map(lambda x: x.encode('ascii'), energy_diff)

    logging.info('In group: {}, number of entries fall in threshold is {}'.format(rootdir,threscount))
    all_data.append([])

    return all_data


def get_magnetization(entry_path,ion_list):

    data = []

    for (parent, subdirs, files) in os.walk(entry_path):
        for f in files:
            if re.match("OUTCAR*", f):
                try:
                    row = []
                    outcar = Outcar(f)
                    mags = outcar.magnetization
                    mags = [m["tot"] for m in mags]
                    all_ions = list(range(len(mags)))
                    if ion_list:
                        all_ions = ion_list
                    for ion in all_ions:
                        row.append(str(mags[ion]))
                    data.append(row)
                except:
                    pass

    return data


def mag_list_process(option,list_to_process):

    processed_list = []

    if option == 'mag_list':
        if list_to_process[0] == "All":
            processed_list = None
        else:
            (start, end) = [int(i) for i in re.split("-", list_to_process[0])]
            processed_list = list(range(start, end + 1))


    if option == 'ave_mag':
        for ele in list_to_process:
            processed_list.append(ele)


    return processed_list




def get_ave_magnetization(entry_path, ave_list):

    ave_list_dic = {}
    data = []
    keylist = []
    row_stat = {}

    if ave_list:
        for key in ave_list:
            (start, end) = [int(i) for i in re.split("-", key)]
            value = list(range(start, end + 1))
            ave_list_dic[key] = value
            row_stat[key] = []
            keylist.append(key)
    else:
        keylist.append('Average All')
        row_stat['Average All']=[]



    for (parent, subdirs, files) in os.walk(entry_path):
        for f in files:
            if re.match("OUTCAR*", f):
                try:
                    row = []
                    fullpath = os.path.join(parent, f)
                    outcar = Outcar(fullpath)
                    mags = outcar.magnetization
                    mags = [m["tot"] for m in mags]
                    all_ions = list(range(len(mags)))

                    if ave_list:
                        for ele in keylist:
                            all_ions = ave_list_dic[ele]
                            magdata = []
                            logging.debug('ion list is {}\n'.format(all_ions))
                            for ion in all_ions:
                                magdata.append(mags[ion])
                            avg_mag = sum(magdata)/len(magdata)
                            row.append(avg_mag)
                            row_stat[ele].append(avg_mag)
                            logging.debug('The intermediat row_stat key value is: {}'.format(row_stat[key]))
                        data.append(row)

                    else:
                        magdata = []
                        for ion in all_ions:
                            magdata.append(mags[ion])
                        logging.debug('The magdata list is: {}'.format(magdata))
                        logging.debug('The magdata list length is: {}'.format(len(magdata)))
                        avg_mag = sum(magdata)/len(magdata)
                        row.append(avg_mag)
                        row_stat['Average All'].append(avg_mag)
                        data.append(row)
                except:
                    pass

    logging.debug('The row state value is: {}'.format(row_stat))


    static_row = ['The average and standard deviation data of all above value is: ']
    for ele in keylist:
        ele_avg = sum(row_stat[ele])/len(row_stat[ele])
        std_dev = np.std(np.array(row_stat[ele]))
        static_row.append(str(ele_avg)+'_'+str(std_dev))


    return data, keylist


def get_incar_para():
    pass



def parse_vasp(groupdireclist, args):

    data_to_csv = []

    default_energies = not (args.get_energies or args.ion_list or args.ion_avg_list)


    if args.get_energies or default_energies:
        for d in groupdireclist:
            groupdata= get_energies(d, args.reanalyze, args.verbose,
                         args.detailed, args.sort[0],args.formulaunit,args.debug,args.hull,args.threshold, args)
            data_to_csv.extend(groupdata)


    output_CSV(data_to_csv,args)


def group_directories(root_dir, group_depth):

    rootpath = root_dir[0]
    pathdepth = glob.glob(rootpath+'/*'*int(group_depth))
    dirlistdepth = filter(lambda f: os.path.isdir(f),pathdepth)

    logging.debug('The directory contained in the path directory is: {}'.format(dirlistdepth))
    # logging.debug('The type of dirlistdepth parameter is:{}'.format(type(dirlistdepth)))

    return dirlistdepth



def output_CSV(data_entry,args):

    if args.nupdown:
        fieldnames = ["Directory Group", "Directory", "Formula", "Energy",
                      "Energy Diff (meV)/F.U.","E/Atom", "% vol chg", 'Run_Type','NUPDOWN']
    else:
        fieldnames = ["Directory Group", "Directory", "Formula", "Energy",
                      "Energy Diff (meV)/F.U.","E/Atom", "% vol chg", 'Run_Type']

    if args.ion_list:
        fieldnames.extend(mag_list_process('mag_list',args.ion_list))

    if args.ion_avg_list:
        fieldnames.extend(mag_list_process('ave_mag',args.ion_avg_list))

    with open('results.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for f in data_entry:
            r = dict(zip(fieldnames,f))
            writer.writerow(r)
    print("Results written to results.csv!")


def file_process(args):

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    groupdirlist = group_directories(args.directories, args.depth)

    parse_vasp(groupdirlist,args)

    pass


def main():
    parser = argparse.ArgumentParser(description="""
    This is a master script for generating csv file.""",
                                     epilog="""
    Author: Chen Zheng
    Version: {}
    Last updated: {}""".format(__version__, __date__))

    subparsers = parser.add_subparsers()

    parser_vasp = subparsers.add_parser("analyze", help="Vasp run analysis.")
    parser_vasp.add_argument("directories", metavar="dir", default=".",
                             type=str, nargs="*",
                             help="directory to process (default to .)")
    parser_vasp.add_argument("-dep",  "--depth", dest='depth', default="1",
                             type=str, nargs="?",
                             help="Depth level of children directory that will be group together")

    parser_vasp.add_argument("-db", "--debug", dest="debug", action="store_true",
                             help="Debug mode, provides information used for debug")
    parser_vasp.add_argument("-thr", "--threshold", dest="threshold", type=str, nargs="?", default='0',
                             help="The threshold of energy difference failed to distinguish with DFT accuracy")


    parser_vasp.add_argument("-e", "--energies", dest="get_energies",
                             action="store_true", help="Print energies")
    parser_vasp.add_argument("-hu", "--hull", dest="hull",
                             action="store_true", help="Print energies above lowest structure list")
    parser_vasp.add_argument("-m", "--mag", dest="ion_list", type=str, nargs=1,
                             help="Print magmoms. ION LIST can be a range "
                             "(e.g., 1-2) or the string 'All' for all ions.")
    parser_vasp.add_argument("-f", "--force", dest="reanalyze",
                             action="store_true",
                             help="Force reanalysis. Typically, vasp_analyzer"
                             " will just reuse a vasp_analyzer_data.gz if "
                             "present. This forces the analyzer to reanalyze "
                             "the data.")
    parser_vasp.add_argument("-v", "--verbose", dest="verbose",
                             action="store_true",
                             help="verbose mode. Provides detailed output on "
                             "progress.")
    parser_vasp.add_argument("-d", "--detailed", dest="detailed",
                             action="store_true",
                             help="Detailed mode. Parses vasprun.xml instead "
                             "of separate vasp input. Slower.")
    parser_vasp.add_argument("-s", "--sort", dest="sort", type=str, nargs=1,
                             default=["energy_per_atom"],
                             help="Sort criteria. Defaults to energy / atom.")

    parser_vasp.add_argument("-fu", "--formulaunit", dest="formulaunit", type=str,
                             default=1,
                             help="Formula unit defined by user")

    parser_vasp.add_argument("-avl", "--averlist", dest="ion_avg_list", type=str, nargs='*',
                             help="Return average magmons value of ions. ION LIST can be a range "
                             "(e.g., 1-2, 3-4) or the string 'All' for all ions.")

    parser_vasp.add_argument("-nu", "--nupdown", dest="nupdown",
                             action="store_true",
                             help="set and determine whether fetch NUPDOWN value, no pass if NUPDOWN not setting"
                             )


    parser_vasp.set_defaults(func=file_process)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()








