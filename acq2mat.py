'''
acq2mat.py

Convert an ACQ file collected via Biopac's AcqKnowledge software to a MATLAB structure.
'''

import sys
import argparse
import re
import bioread
import numpy as np
import pandas as pd
from scipy import io as sio
import pdb

def argument_parser(argv):
    '''Parse input from the command line'''

    parser = argparse.ArgumentParser(description='ACQ2MAT: a tool to extract ACQ files.')

    parser.add_argument('file',
        help='ACQ file to convert',
        nargs='+')

    parser.add_argument('-o', '--outfile',
        help='Filename for MATLAB file output',
        required=False)

    args = parser.parse_args()

    if not args.outfile:
        args.outfile = args.file[0].replace('.acq', '.mat')

    return args

def clean(s):
    '''Take a string and construct a valid variable name.
    Used to ensure that channel names are able to be used in MATLAB.
    Adapted from https://stackoverflow.com/questions/3303312/how-do-i-convert-a-string-to-a-valid-variable-name-in-python'''

    s = s.lower().strip() # preliminary cleaning
    s = re.sub('[^0-9a-zA-Z_]', '', s) # include only valid characters
    s = re.sub('^[^a-zA-Z]+', '', s) # first character must be a letter

    return s

def parse_data(data):
    '''Read in ACQ file using njvack's bioread package (https://github.com/uwmadison-chm/bioread)'''
    d = {} # new dictionary to be saved with scipy.io

    # Add channel data
    for channel in data.channels:
        chan_name = channel.name.lower().strip().replace(' ', '_')
        d[clean(channel.name)] = {
            'wave':channel.data,
            'Fs': channel.samples_per_second,
            'unit': channel.units,
        }

    # Add event markers
    event_markers = {}
    event_markers['label'] = []
    event_markers['sample_index'] = []
    event_markers['type_code'] = []
    event_markers['type'] = []
    event_markers['channel_number'] = []
    event_markers['channel'] = []

    valid_events = [i for i in data.event_markers if i.type_code != 'nrto']
    for event in valid_events:

        [setattr(event, key, np.nan) for key in event.__dict__.keys() if getattr(event, key) == None]

        event_markers['label'].append(event.text)
        event_markers['sample_index'].append(event.sample_index+1) # +1 since MATLAB is indexed from 1, not 0
        event_markers['type_code'].append(event.type_code)
        event_markers['type'].append(event.type)
        event_markers['channel_number'].append(event.channel_number)
        event_markers['channel'].append(event.channel)

    d['event_markers'] = event_markers

    return d

def cat_multiple_files(d_list):

    d = d_list[0]

    for d_new in d_list[1:]:

        offset = max([len(d[i]['wave']) for i in d.keys() if i != 'event_markers'])

        for key in d.keys():

            if key == 'event_markers':
                for key2 in d['event_markers'].keys():
                    if key2 == 'sample_index':
                        d['event_markers']['sample_index'] = d['event_markers']['sample_index'] + [i+offset for i in d_new['event_markers']['sample_index']] # increment sample number
                    else:
                        d['event_markers'][key2] = d['event_markers'][key2] + d_new['event_markers'][key2]

            else:
                d[key]['wave'] = np.append(d[key]['wave'], d_new[key]['wave'])

    return d


if __name__ == '__main__':

    args = argument_parser(sys.argv[1:])
    data = [bioread.read_file(i) for i in args.file] # read each file specified in command line
    d_list = [parse_data(i) for i in data] # parse the data and return in a list of dictionaries

    if len(d_list) >= 2: # concatenate files if there are more than one
        d = cat_multiple_files(d_list)
    else:
        d = d_list[0];

    d = {'d': d} # wrap into one MATLAB struct rather than multiple variables

    sio.savemat(args.outfile, d, oned_as='column', do_compression=True)
