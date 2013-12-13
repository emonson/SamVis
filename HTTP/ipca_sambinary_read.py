import io
import struct
import numpy as N
import collections as C
import os

def read_hdf5_ipcadata(tree_data_filename):
	""" Read IPCA tree and data from Sam's binary file format which he dumps variables
	from his tree in C++. Return root of tree (which is just a bunch of dictionaries
	linked to each other through children and parent) and list of same node element objects
	but ordered by id rather than in a tree structure."""
	
	print 'data read in. starting hdf5 original data writing'

	with h5py.File(outfile, 'r') as f:
	
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
		for node in nodes_by_id:
		
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
		for node in nodes_by_id:
			id = node['id']
			if 'children' in node:
				for child in node['children']:
					child_id = child['id']
					# Create hard link
					nodes_g[str(id) + '/children/' + str(child_id)] = nodes_g[str(child_id)]

		# And write hard link to tree root
		full_tree_g['tree_root'] = nodes_g[str(tree_root['id'])]

	return tree_root, nodes_by_id
	

def read_hdf5_labeldata(label_data_filename):
	"""Read IPCA tree label data from Sam's binary format, which is basically an
	R datastructure, I think..."""
	

	return labels

def checked_filename(filename):
	if filename and type(filename) == str:
		return  os.path.abspath(filename)
	else:
		raise IOError, "filename needs to be a non-empty string"

	if not os.path.isfile(self.label_file):
		raise IOError, "input file does not exist"
	
	return ""


def read_hdf5_originaldata(orig_data_file):
	"""Read the original data used for IPCA. Basically an R binary format, I think..."""


	return orig_data


# --------------------
if __name__ == "__main__":

	hdf = '../../test/test1_mnist12.hdf5'		
	
	tree_root, nodes_by_id = read_hdf5_ipcadata(tdf)
	labels = read_hdf5_labeldata(ldf)
	orig_data = read_hdf5_originaldata(df)