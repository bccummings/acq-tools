# acq-tools
Toolkit for managing and analyzing physiologic data collected via BIOPAC's AcqKnowledge software.

## Introduction

Much of the data from the clinical and pre-clinical groups at MCIRCC is acquired using the [BIOPAC](https://www.biopac.com) AcqKnowledge software package, however, many of the tools and analysis techniques developed by MCIRCC members are implemented in MATLAB and other programming languages that cannot work with the AcqKnowledge (ACQ) fiels directly. Thus, this repository is designed as an extension of the excellent [`bioread`](https://github.com/uwmadison-chm/bioread) package developed by [Nate Vack](https://github.com/njvack), which wraps ACQ files into a MATLAB structure compatible with MCIRCC's tools. As the repository grows, other transformations and operations that are common accross MCRICC projects may be added.

## Getting started

To use the tools included in this repository, open up a command line window and clone it using:

```bash
git clone https://github.com/bccummings/acq-tools
```

Then, create a Python 3 virtual environment and load in the required packages. The code below moves the user into the repository's directory, then constructs and activates a virtual environment. Lastly, it loads the required dependancies listed in the `requirements.txt`.

```bash
cd acq-tools
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Loading an ACQ file

### Converting ACQ into MATLAB

To convert an ACQ file into a MATLAB file, use the `acq2mat.py` script. It takes the ACQ filename as a positional argument.

```bash
python acq2mat /path/to/file.acq
```

In the case where the BIOPAC acquisition is stopped and started, these files can easily be concatenated together. Simply specify multiple file names in the order that they should be concatenated, and `acq2mat.py` will take care of the rest. After concatenation, the original breakpoints of the files are specified by the "Segment 1" event markers. Note that there is no adjustment for the time between stopping and resuming acquisition – they are appended directly.

```bash
python acq2mat /path/to/file_01.acq /path/to/file_02.acq
```

Optionally, an output file can be specified using the `-o` or `--outfile` flags. If no output directory is specified, the script places the new output file in the same directory as the input file, with the `.acq` extension changed to `.mat`. If the user has specified multiple files, then the first filename is used.

```bash
python acq2mat /path/to/file.acq -o /new/output/path.mat
```

### Opening the file in MATLAB

To load the MAT file from within MATLAB, use of the `loadfile.m` function is recommended. The `scipy.io.savemat()` function, around which the `acq2mat.py` script is centered, is unable to save array data into a MATLAB table. Thus, the event markers must be saved as a MATLAB `struct` object. The `loadfile.m` MATLAB function converts this struct to a more human-readable `table` object, as well as converts the various character arrays into `cellstr` objects.

From within MATLAB:

```matlab
d = loadfile('file.mat');
```
### Navigating the `d` structure

As required by many of the previously constructed analysis tools and pipelines, the data is stored in an object termed `d`. This is a 1-by-1 `struct` object which contains a field for each channel recorded by the BIOPAC. The fields are named according to how they were initialized in the ACQ file, with the exception that the channel name is altered to be lower case and follow valid MATLAB variable conventions (must start with a letter, and can only contain letters, numbers, and the `_` character).

Each of these channels contains the same three fields:  
* `wave`: the waveform data, saved as an n-by-one double.  
* `Fs`: sampling frequency, in Hz.  
* `unit`: the channel unit. Note that this is based on the manual configuration set up in the ACQ file, which historically has not been consistently updated as new channels are added and re-configured.

Additionally, there is an `event_markers` field under the `d` object, which (if opened via the `loadfile.m` function) is a table containing event marker data for the duration of the file. It has the columns:

`label`: the annotation text.
`sample_index`: the sample number associated with the marker.
`type`: how the marker was created (e.g. `User Type 9` for F9 markers)
`type_code`: an internal ACQ notation for the `type`
`channel_number`: if the marker is associated with a specific channel, it shows up here. Based on our usage thus far, this is usually empty.
`channel`: the name of the associated channel. Again, usually empty.

#### Usage example

The following MATLAB code will plot an arterial blood pressure waveform saved under the name `abp`. The x-axis will be in seconds. Additionally, it will annotate the plot with the event markers.

```matlab
t = ( 1:length(d.abp.wave) ) / d.abp.Fs; % time vector
plot(t, d.abp.wave); % plot arterial blood pressure

x = d.event_markers.sample_index / d.abp.Fs; % create x-coordinates for text annotations
y = ones(height(d.event_markers), 1) * mean(d.abp.wave); % create y-coordinates for text annotations
text(x, y, d.event_markers.label, 'Rotation', 90) % plot text annotations
```
## Contributing

In addition to providing tools to extract and analyze ACQ data files, this repository is intended to have a dual purpose in helping contributers both learn and teach git techniques. I encourage contributors to use the GitHub [Issue](https://github.com/bccummings/acq-tools/issues) and [Project](https://github.com/bccummings/acq-tools/projects/1) tools to submit and track even small proposed changes, and to use pull requests rather than committing to the master branch. Please see
[CONTRIBUTING.md](https://github.com/bccummings/acq-tools/blob/master/docs/CONTRIBUTING.md) for more information.

## Acknowledgements and Disclaimers

Many of the tools found in this repository, most saliently `acq2mat.py`, rely heavily on the expertly-constructed [`bioread`](https://github.com/uwmadison-chm/bioread) package authored primarily by [Nate Vack](https://github.com/njvack). This package is responsible for loading and parsing the ACQ file – the `acq2mat` tool in this repository simply wraps the data into a prettier format more consistent with MCIRCC analysis tools.

Additionally, neither the authors nor this repository have any affiliation with or endorsement from [BIOPAC Systems, Inc.](https://www.biopac.com), and note that both BIOPAC and AcqKnowledge are trademarks of this company.
