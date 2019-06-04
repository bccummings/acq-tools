function d = loadfile(filename)
%LOADFILE A function to load MAT files created by acq2mat.py.
%
% USAGE: d = loadfile(filename);
%
% Brandon Cummings
% MCIRCC, University of Michigan, Ann Arbor
% June 4, 2019
%
% The loadfile() function reads a MAT file constructed by acq2mat.py and
% reconfigures the event_markers field into a MATLAB table. This is
% necessary because the scipy.io.savemat() function only supports
% structural data, not tabular. 
%
% The output is an object, 'd', is a MATLAB structure with fields
% corresponding to the Biopac channel names. Each of the channels is a
% structure in its own right, with subfields "wave", "Fs", and "unit". The
% "wave" object contains the waveform data in an column vector with double
% precision. The "Fs" object represents the sampling frequency in Hz, and
% the "unit" is a character object describing the unit of measure. Note
% that this is reflective of what is entered manually in Biopac, and has
% historically not been kept up-to-date through template changes.
%
% EXAMPLES
%
% 1. Plot arterial pressure waveform saved under the channel name "abp"
% 
% d = loadfile(filename);
% plot( (1:length(d.abp.wave))/d.abp.Fs, d.abp.wave)
%
% 2. Annotate with event markers
% 
% text(d.event_markers.sample_index, zeros(height(d.event_markers), 1), d.event_markers.label, 'Rotation', 90)
%

load(filename, 'd');

fields = fieldnames(d.event_markers);

for i = 1:numel(fields)
    
    % Convert character arrays to cellstr
    if isa(d.event_markers.(fields{i}), 'char')
        d.event_markers.(fields{i}) = cellstr(d.event_markers.(fields{i}));
    
    % Convert in64 to doubles
    elseif isa(d.event_markers.(fields{i}), 'int64')
        d.event_markers.(fields{i}) = double(d.event_markers.(fields{i}));
        
    end
    
end

d.event_markers = struct2table(d.event_markers);

end
