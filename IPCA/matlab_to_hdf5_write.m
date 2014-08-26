function matlab_to_hdf5_write(GMRA, imgOpts, filename)

% Use the high-level interface to write Matlab GMRA data out to an HDF5 
% file for import into web-based IPCA visualization. Low-level interface
% used for file reset and hard link construction

fprintf('(re)Creating HDF5 file, %s\n', filename);

% Recreate file each time
fcpl = H5P.create('H5P_FILE_CREATE');
fapl = H5P.create('H5P_FILE_ACCESS');
fid = H5F.create(filename, 'H5F_ACC_TRUNC', fcpl, fapl);
H5F.close(fid);

%% Original data

fprintf('Writing original data\n');

% Original data : want [D x N]
h5create(filename, '/original_data/data', size(GMRA.X'));
h5write(filename, '/original_data/data', GMRA.X');

% Data type and attributes
% TODO: Need to figure out a good way to specify options
if imgOpts.imageData,
    h5writeatt(filename, '/original_data', 'dataset_type', 'image');
    h5writeatt(filename, '/original_data', 'image_n_rows', int64(imgOpts.imR));
    h5writeatt(filename, '/original_data', 'image_n_columns', int64(imgOpts.imC));
end

%% Labels

fprintf('Writing original data labels\n');

for ii = 1:size(imgOpts.Labels, 2)
    label_data = imgOpts.Labels(:,ii);
    % TODO: need to have labels names stored in metadata...
    h5create(filename, '/original_data/labels/digit_id', length(label_data), 'Datatype', 'int32');
    h5write(filename, '/original_data/labels/digit_id', int32(label_data));
    h5writeatt(filename, '/original_data/labels/digit_id', 'description', 'digit ids');
    h5writeatt(filename, '/original_data/labels/digit_id', 'variable_type', 'categorical');
    % h5writeatt(filename, '/original_data/labels/digit_id', 'key', {{'1', 'digit1'}, {'2', 'digit2'}});
end

%% Full tree by ID

fprintf('Writing nodes by ID\n');

% First pass, store nodes by ID
n_nodes = length(GMRA.cp);
nodes_root = '/full_tree/nodes/';
for ii = 1:n_nodes,
    % IDs for vis need to be zero-based
    node_id = int64(ii-1);      % zero-based!
    node_group_name = [nodes_root int2str(node_id)];      % zero-based!

    % node_g['id'] = node['id']
    h5create(filename, [node_group_name '/id'], 1, 'Datatype', 'int64');
    h5write(filename, [node_group_name '/id'], node_id);      % zero-based!
    
    % if 'parent_id' in node:
    %     node_g['parent_id'] = node['parent_id']
    % cp is a list of the parent ID of each node. Root has parent ID == 0 (in Matlab's ones-based indices)
    parent_id = int64(GMRA.cp(ii)-1);      % zero-based!
    % Adopting convention (for now) that root doesn't have parent_id field
    if parent_id > -1,
        h5create(filename, [node_group_name '/parent_id'], 1, 'Datatype', 'int64');
        h5write(filename, [node_group_name '/parent_id'], parent_id);      % zero-based!
    end
    
    % node_g['l2Radius'] = node['l2Radius']
    h5create(filename, [node_group_name '/l2Radius'], 1, 'Datatype', 'double');
    h5write(filename, [node_group_name '/l2Radius'], GMRA.Radii(ii));
   
    % node_g['a'] = node['a']
    
    % node_g['npoints'] = node['npoints']
    h5create(filename, [node_group_name '/npoints'], 1, 'Datatype', 'int64');
    h5write(filename, [node_group_name '/npoints'], int64(GMRA.Sizes(ii)));
    
    % node_g.create_dataset('phi', data=node['phi'])
    h5create(filename, [node_group_name '/phi'], size(GMRA.ScalFuns{ii}), 'Datatype', 'double');
    h5write(filename, [node_group_name '/phi'], GMRA.ScalFuns{ii});
    
    % node_g.create_dataset('sigma', data=node['sigma'])
    % NOTE: Careful, this Sigmas is normalized to 1/sqrt(n_points)...
    h5create(filename, [node_group_name '/sigma'], length(GMRA.Sigmas{ii}), 'Datatype', 'double');
    h5write(filename, [node_group_name '/sigma'], GMRA.Sigmas{ii});

    % node_g.create_dataset('dir', data=node['dir'])
    % node_g.create_dataset('mse', data=node['mse'])
    
    % node_g.create_dataset('center', data=node['center'])
    h5create(filename, [node_group_name '/center'], length(GMRA.Centers{ii}), 'Datatype', 'double');
    h5write(filename, [node_group_name '/center'], GMRA.Centers{ii});
    
    % node_g.create_dataset('indices', data=node['indices'])
    h5create(filename, [node_group_name '/indices'], length(GMRA.PointsInNet{ii}), 'Datatype', 'int64');
    h5write(filename, [node_group_name '/indices'], int64(GMRA.PointsInNet{ii}));

    % node_g.create_dataset('sigma2', data=node['sigma2'])
    % NOTE: Careful, this Sigmas is normalized to 1/sqrt(n_points)...
    h5create(filename, [node_group_name '/sigma2'], length(GMRA.Sigmas{ii}), 'Datatype', 'double');
    h5write(filename, [node_group_name '/sigma2'], GMRA.Sigmas{ii}.^2);
end

% In high-level interface, group must exist before you can attach
% attributes to it.
h5writeatt(filename, '/full_tree', 'n_nodes', int64(n_nodes));

%% Tree links for structure

% Second pass to put in hard links to root node and children
fid = H5F.open(filename,'H5F_ACC_RDWR','H5P_DEFAULT');
lcpl = 'H5P_DEFAULT';
lapl = 'H5P_DEFAULT';

fprintf('Creating hard links for tree\n');
for ii = 1:length(GMRA.cp),
    node_id = int64(ii-1);     % zero-based
    node_group_name = [nodes_root int2str(node_id)];      % zero-based!
    gid_node = H5G.open(fid, node_group_name);
    
    children_ids = (find(GMRA.cp == ii) - 1);
    if ~isempty(children_ids),
        % Create the new children group to put the links in
        gid_children = H5G.create(gid_node, 'children', 'H5P_DEFAULT');
        for cc = 1:length(children_ids),
            % Find the child node group
            child_node_name = [nodes_root int2str(int64(children_ids(cc)))];
            gid_child = H5G.open(fid, child_node_name);
            % Create the hard link
            H5L.create_hard(gid_child, child_node_name, gid_children, int2str(int64(children_ids(cc))), lcpl, lapl);
            H5G.close(gid_child);
        end
        H5G.close(gid_children);
    end
    H5G.close(gid_node);
end

% Root node -- better be just one!
gid_fulltree = H5G.open(fid, '/full_tree');
root_id = (find(GMRA.cp == 0) - 1);
child_node_name = [nodes_root int2str(int64(root_id))];
gid_child = H5G.open(fid, child_node_name);
% Create the hard link
H5L.create_hard(gid_child, child_node_name, gid_fulltree, 'tree_root', lcpl, lapl);
H5G.close(gid_child);
H5G.close(gid_fulltree);

H5F.close(fid);

end
