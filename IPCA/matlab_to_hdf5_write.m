function matlab_to_hdf5_write(GMRA, imgOpts, filename)
% Use the high-level interface to write Matlab GMRA data out
% to and HDF5 file for import into web-based IPCA visualization

% Original data type and attributes
% TODO: Need to figure out a good way to specify options
if imgOpts.imageData,
    h5writeatt(filename, '/original_data', 'dataset_type', 'image');
    h5writeatt(filename, '/original_data', 'image_n_rows', imgOpts.imR);
    h5writeatt(filename, '/original_data', 'image_n_cols', imgOpts.imC);
end

% Original data
h5create(filename, '/original_data/data', size(GMRA.X));
h5write(filename, '/original_data/data', GMRA.X);

% Labels
for ii = 1:size(imgOpts.Labels, 2)
    label_data = imgOpts.Labels(:,ii);
    % TODO: need to have labels names stored in metadata...
    h5create(filename, '/original_data/labels/digit_id', size(label_data));
    h5write(filename, '/original_data/labels/digit_id', label_data);
end

% Full tree
% First pass, store nodes by ID
n_nodes = length(GMRA.cp);
h5writeatt(filename, '/full_tree', 'n_nodes', n_nodes);
for ii = 1:n_nodes,
    % IDs for vis need to be zero-based
    node_group_name = ['/full_tree/nodes/' int2str(ii-1)];
    
end

end
