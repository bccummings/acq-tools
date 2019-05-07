'''
acq2mat.py

Convert an ACQ file collected via Biopac's AcqKnowledge software to a MATLAB structure.
'''

import sys
import argparse
import re
import bioread
import pandas as pd
from scipy import io as sio

def argument_parser(argv):
    '''Parse input from the command line'''

    parser = argparse.ArgumentParser(description='ACQ2MAT: a tool to extract ACQ files.')

    parser.add_argument('file',
        help='ACQ file to convert')

    parser.add_argument('-o', '--outfile',
        help='Filename for MATLAB file output')

    args = parser.parse_args()

    if not args.outfile:
        args.outfile = args.file.replace('.acq', '.mat')

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
    valid_events = [i for i in data.event_markers if i.type_code != 'nrto']

    event_markers = pd.DataFrame()

    c = 0
    for event in valid_events:
        event_markers[c, 'label'] = event.text
        event_markers[c, 'sample_index'] = event.sample_index
        event_markers[c, 'type_code'] = event.type_code
        event_markers[c, 'type'] = event.type
        event_markers[c, 'channel_number'] = event.channel_number
        event_markers[c, 'channel'] = event.channel

        c+=1

    d['event_markers'] = event_markers.to_dict()

    return d

if __name__ == '__main__':

    args = argument_parser(sys.argv[1:])
    data = bioread.read_file(args.file)
    d = parse_data(data)
    d = {'d': d} # wrap into one MATLAB struct rather than multiple variables

    sio.savemat(args.outfile, d)
