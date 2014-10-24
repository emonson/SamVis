import h5py
import os
import numpy as np
import ipca_sambinary_read as IR

data_root_path = '/Users/emonson/Data/GMRA_data'
data_folder_name = 'mnist12_v5_d8c2'

data_path = os.path.join(data_root_path, data_folder_name)
outfile = data_path + '_test1.hdf5'

# Read data from binary file
data_info = IR.read_data_info(data_path)

tree_data_file = os.path.join(data_path, data_info['full_tree']['filename'])
print 'Trying to load data from .ipca file... ', tree_data_file
tree_root, nodes_by_id = IR.read_sambinary_v3_ipcadata(tree_data_file)

original_data_file = os.path.join(data_path, data_info['original_data']['filename'])
print 'Trying to load original data from .data file... ', original_data_file
original_data_array = IR.read_sambinary_originaldata(original_data_file, data_info['original_data']['data_type'])

print 'data read in. starting hdf5 original data writing'

with h5py.File(outfile, 'w') as f:
    
    # Original data
    original_data_g = f.create_group("original_data")
    original_data_g.create_dataset("data", data=original_data_array)
    
    # Original data attributes
    original_data_g.attrs['dataset_type'] = data_info['original_data']['dataset_type']
    if data_info['original_data']['dataset_type'] == 'image':
        original_data_g.attrs['image_n_rows'] = data_info['original_data']['image_n_rows']
        original_data_g.attrs['image_n_columns'] = data_info['original_data']['image_n_columns']
    
    # Original data labels
    if 'labels' in data_info['original_data']:
        original_data_labels_g = original_data_g.create_group('labels')
    
        for label_name, label_info in data_info['original_data']['labels'].items():
            # Read labels data
            labels_data_file = os.path.join(data_path, label_info['filename'])
            labels_array = IR.read_sambinary_labeldata(labels_data_file, label_info['data_type'])
            # Store labels in HDF5
            label = original_data_labels_g.create_dataset(label_name, data=labels_array)
            # Transfer label attributes
            for attr_name, attr_value in label_info.items():
                print attr_name
                # Dataset attributes must be scalars, strings or arrays
                if isinstance(attr_value, dict):
                    val_array = np.array([(k,v) for k,v in attr_value.items()])
                    # HDF5 can't handle numpy unicode types...
                    if val_array.dtype.char == 'U':
                        label.attrs[attr_name] = val_array.astype('|S1')
                    else:
                        label.attrs[attr_name] = val_array
                else:
                    label.attrs[attr_name] = attr_value
        
    # Tree
    # Storing main copy of the tree nodes in a flat set of groups under full_tree group
    # named by ID. They'll contain hard links to children, and a hard link to the root
    # node will be included in case we want to traverse the tree in a standard way
    print 'starting full tree writing'
    full_tree_g = f.create_group("full_tree")
    full_tree_g.attrs['n_nodes'] = len(nodes_by_id)
    
    # TODO: Create the n_nodes x 5 array with the tree description in the format
    #   of the cover tree and add it in as a dataset to full_tree, too.
    
    # Make a first pass through nodes_by_id and write out node data
    nodes_g = full_tree_g.create_group("nodes")
    for id,node in nodes_by_id.iteritems():
        
        node_g = nodes_g.create_group(str(node['id']))
        
        # TODO: get these all straight...
        # ['a', 'phi', 'center', 'parent_id', 'nSplit', 'children', 'l2Radius', 'npoints', 'nKids', 'indices', 'mse', 'sigma', 'id', 'dir', 'sigma2']
        node_g['id'] = node['id']
        if 'parent_id' in node:
            node_g['parent_id'] = node['parent_id']
        node_g['l2Radius'] = node['l2Radius']
        node_g['a'] = node['a']
        node_g['npoints'] = node['npoints']
        node_g.create_dataset('phi', data=node['phi'])
        node_g.create_dataset('sigma', data=node['sigma'])
        node_g.create_dataset('dir', data=node['dir'])
        node_g.create_dataset('mse', data=node['mse'])
        node_g.create_dataset('center', data=node['center'])
        node_g.create_dataset('indices', data=node['indices'])
        node_g.create_dataset('sigma2', data=node['sigma2'])
        
        node_children_g = node_g.create_group('children')
    
    # Make a second pass through to put in hard links to children now that they all exist
    print 'starting full tree children writing'
    for id,node in nodes_by_id.iteritems():
        id = node['id']
        if 'children' in node:
            for child in node['children']:
                child_id = child['id']
                # Create hard link
                nodes_g[str(id) + '/children/' + str(child_id)] = nodes_g[str(child_id)]

    # And write hard link to tree root
    full_tree_g['tree_root'] = nodes_g[str(tree_root['id'])]

