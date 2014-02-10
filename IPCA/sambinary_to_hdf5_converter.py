import h5py
import numpy as N
import ipca_sambinary_read as IR

tdf = '../../test/mnist12.ipca'
ldf = '../../test/mnist12_labels.data.hdr'
df = '../../test/mnist12.data.hdr'		

outfile = '../../test/test1_mnist12.hdf5'

tree_root, nodes_by_id = IR.read_sambinary_ipcadata(tdf)
labels_array = IR.read_sambinary_labeldata(ldf)
original_data_array = IR.read_sambinary_originaldata(df)

print 'data read in. starting hdf5 original data writing'

with h5py.File(outfile, 'w') as f:
	
	# Original data
	original_data_g = f.create_group("original_data")
	original_data_g.create_dataset("data", data=original_data_array)
	
	original_data_g.attrs['dataset_type'] = 'image'
	original_data_g.attrs['image_n_rows'] = 28
	original_data_g.attrs['image_n_columns'] = 28
	
	# Original data labels
	original_data_labels_g = original_data_g.create_group('labels')
	digit_id = original_data_labels_g.create_dataset('digit_id', data=labels_array)
	digit_id.attrs['description'] = 'Identity of the digit depicted in each image. Label is the actual digit, here 1 and 2.'
		
	# Tree
	# Storing main copy of the tree nodes in a flat set of groups under full_tree group
	# named by ID. They'll contain hard links to children, and a hard link to the root
	# node will be included in case we want to traverse the tree in a standard way
	print 'starting full tree writing'
	full_tree_g = f.create_group("full_tree")
	full_tree_g['n_nodes'] = len(nodes_by_id)
	
	# TODO: Create the n_nodes x 5 array with the tree description in the format
	#   of the cover tree and add it in as a dataset to full_tree, too.
	
	# Make a first pass through nodes_by_id and write out node data
	nodes_g = full_tree_g.create_group("nodes")
	for id,node in nodes_by_id.iteritems():
		
		node_g = nodes_g.create_group(str(node['id']))
	
		node_g['id'] = node['id']
		if 'parent_id' in node:
			node_g['parent_id'] = node['parent_id']
		node_g['r'] = node['r']
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

