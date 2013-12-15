import numpy as N
import os
import h5py

def read_hdf5_ipcadata(tree_data_filename):
	""" Read IPCA tree and data from Sam's binary file format which he dumps variables
	from his tree in C++. Return root of tree (which is just a bunch of dictionaries
	linked to each other through children and parent) and list of same node element objects
	but ordered by id rather than in a tree structure."""
	
	with h5py.File(tree_data_filename, 'r') as f:
		
		# Make a first pass through nodes_by_id and grab node data
		n_nodes = f['/full_tree/n_nodes'][()]
		nodes_by_id = [{}]*n_nodes
		nodes_g = f['/full_tree/nodes']
		
		
		for id_str, node_g in nodes_g.iteritems():
			
			# Could also just grab the ID
			id = node_g['id'][()]
			
			for d_name in node_g:
				d_class = node_g.get(d_name, getclass=True)
				if d_class == h5py.Dataset:
					dataset = node_g[d_name]
					data = N.empty(dataset.shape, dtype=dataset.dtype)
					dataset.read_direct(data)
					nodes_by_id[id][d_name] = data
	
		# Make a second pass through to put in hard links to children now that they all exist
		for id_str, node_g in nodes_g.iteritems():
			
			if 'children' in node_g:
				# Remove the group path slash to get the ID
				id = int(id_str)
				children_g = node_g['children']
				nodes_by_id[id]['children'] = []
				
				# Put reference to existing nodes in 'children' list
				for n_name, n_g in children_g.iteritems():
					cid = n_g['id'][()]
					nodes_by_id[id]['children'].append(nodes_by_id[cid])
					
		# Get the tree root by id from the hard link
		tree_root_id = f['/full_tree/tree_root']['id'][()]
		tree_root = nodes_by_id[tree_root_id]
	
	return tree_root, nodes_by_id
	

def read_hdf5_labeldata(label_data_filename):
	"""Read IPCA tree label data from Sam's binary format, which is basically an
	R datastructure, I think..."""
	
	labels = {}
	label_descriptions = {}
	
	with h5py.File(label_data_filename, 'r') as f:

		# Original data labels
		labels_g = f['/original_data/labels']
		for lname in labels_g.keys():
			ld = labels_g[lname]
			label_data = N.empty(ld.shape, dtype=ld.dtype)
			ld.read_direct(label_data)
			labels[lname] = label_data
			label_descriptions[lname] = ld.attrs['description']
			
	return labels, label_descriptions


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

	with h5py.File(orig_data_file, 'r') as f:
	
		# Original data
		original_data_g = f['/original_data']
		od = original_data_g['data']
		
		orig_data = N.empty(od.shape, dtype=od.dtype)
		od.read_direct(orig_data)
	
		dataset_type = original_data_g.attrs['dataset_type']
		if dataset_type == 'image':
			image_n_rows = original_data_g.attrs['image_n_rows']
			image_n_columns = original_data_g.attrs['image_n_columns']
	
	return orig_data


# --------------------
if __name__ == "__main__":

	hdf = '../../test/test1_mnist12.hdf5'		
	
	tree_root, nodes_by_id = read_hdf5_ipcadata(hdf)
	print tree_root.keys()
	print nodes_by_id[20].keys()
	labels, label_descriptions = read_hdf5_labeldata(hdf)
	print labels
	print label_descriptions
	
	orig_data = read_hdf5_originaldata(hdf)
	print orig_data.shape, orig_data.dtype
	print orig_data