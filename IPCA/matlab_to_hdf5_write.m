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
n_pts = size(imgOpts.Labels, 1);
for ii = 1:size(imgOpts.Labels, 2)
    h5create(filename, 'original_data/
end

end
