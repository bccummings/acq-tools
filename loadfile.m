function d = loadfile(filename)

load(filename, 'd');

fields = fieldnames(d.event_markers);

for i = 1:numel(fields)
    if size(d.event_markers.(fields{i}), 1) == 1
        d.event_markers.(fields{i}) = d.event_markers.(fields{i})';
    end
    
    if isa(d.event_markers.(fields{i}), 'char')
        d.event_markers.(fields{i}) = cellstr(d.event_markers.(fields{i}));
    end
end

d.event_markers = struct2table(d.event_markers);

end
