import io
import struct
import numpy as N
import collections as C
import os

def read_sambinary_ipcadata(tree_data_filename):
	""" Read IPCA tree and data from Sam's binary file format which he dumps variables
	from his tree in C++. Return root of tree (which is just a bunch of dictionaries
	linked to each other through children and parent) and list of same node element objects
	but ordered by id rather than in a tree structure."""
	
	f = io.open(tree_data_filename, 'rb', buffering=65536)

	# Tree header
	dt = N.dtype([('epsilon', N.dtype('f8')), 
								('d', N.dtype('u4')), 
								('m', N.dtype('u4')), 
								('minPoints', N.dtype('i4'))])
	header = N.frombuffer(f.read(8+4+4+4), dtype=dt, count=1)
	epsilon = header['epsilon']
	d = header['d']
	m = header['m']
	minPoints = header['minPoints']

	tree_root = None
	nodes_by_id = []
	nodes = C.deque()
	cur = None

	id = 0

# 		try:
	r_nPhi = f.read(4)
	while r_nPhi:
		nPhi = int(N.frombuffer(r_nPhi, N.dtype('i4'), count=1))
		
		phi = N.matrix(N.frombuffer(f.read(8*nPhi*m), N.dtype('f8'), count=nPhi*m).reshape(nPhi,m))
		sigma = N.frombuffer(f.read(8*nPhi), N.dtype('f8'), count=nPhi)
		center = N.frombuffer(f.read(8*m), N.dtype('f8'), count=m)
		mse = N.frombuffer(f.read(8*(d+1)), N.dtype('f8'), count=(d+1))
		dir = N.frombuffer(f.read(8*m), N.dtype('f8'), count=m)
		
		a = float(N.frombuffer(f.read(8), N.dtype('f8'), count=1))
		nPoints = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
		
		pts = N.frombuffer(f.read(4*nPoints), N.dtype('i4'), count=nPoints)
		
		r = float(N.frombuffer(f.read(8), N.dtype('f8'), count=1))
		isLeaf = bool(N.frombuffer(f.read(1), N.dtype('b1'), count=1))

		node = {}
		node['id'] = id
		node['children'] = C.deque()

		if cur == None:
			tree_root = node

		node['r'] = r
		node['phi'] = phi
		node['sigma'] = sigma
		node['dir'] = dir
		node['a'] = a
		node['mse'] = mse
		node['center'] = center
		node['indices'] = pts
		node['npoints'] = nPoints
		node['sigma2'] = sigma*sigma

		# if previously read node is not empty. 
		# i.e. if node != root
		if cur != None:

			# if just-read node is not a leaf
			if not isLeaf:
				# put just-read node in the deque to be visited later
				nodes.append(node)
	
			# if children array of cur (previously read) is full
			# (I think an alternative to this if not dealing with a binary tree
			#		would be to keep track of everyone's parent node ID and check here 
			#		whether cur is the parent of node)
			if len(cur['children']) == 2:
				cur = nodes.popleft()
	
			# fill up cur's children list
			node['parent_id'] = cur['id']
			cur['children'].append(node)
	
		else:
			cur = node

		# Keep a copy arranged by ID, too (relying on sequential IDs)
		nodes_by_id.append(node)
		
		r_nPhi = f.read(4)
		id = id + 1
	
# 		except:
# 			raise IOError, "Can't load data from file %s" % (tree_data_file,)
	
# 		finally:
	f.close()
	
	return tree_root, nodes_by_id
	

def read_sambinary_labeldata(label_data_filename):
	"""Read IPCA tree label data from Sam's binary format, which is basically an
	R datastructure, I think..."""
	
	f = open(label_data_filename, 'r')
	vectype = f.readline().strip()
	if vectype != 'DenseVector':
		raise IOError, "Label file needs to be a DenseVector"
	
	size = f.readline().strip().split()
	if size[0] != 'Size:':
		raise IOError, "Problem reading label vector size"
	n_elements = int(size[1])
	
	elsize = f.readline().strip().split()
	if elsize[0] != 'ElementSize:':
		raise IOError, "Problem reading label vector element size"
	n_bytes = int(elsize[1])
	
	f.close()
	
	fb = open(os.path.splitext(label_data_filename)[0], 'rb')
	labels = N.fromfile(fb, dtype=N.dtype('i' + str(n_bytes)), count=n_elements)
	fb.close()
	
	return labels

def checked_filename(filename):
	if filename and type(filename) == str:
		return  os.path.abspath(filename)
	else:
		raise IOError, "filename needs to be a non-empty string"

	if not os.path.isfile(self.label_file):
		raise IOError, "input file does not exist"
	
	return ""


def read_sambinary_originaldata(orig_data_file):
	"""Read the original data used for IPCA. Basically an R binary format, I think..."""

	f = open(orig_data_file, 'r')

	vectype = f.readline().strip()
	if vectype != 'DenseMatrix':
		raise IOError, "Data file needs to be a DenseMatrix"

	size = f.readline().strip().split()
	if size[0] != 'Size:' or size[2] != 'x':
		raise IOError, "Problem reading data matrix size"
	m = int(size[1])
	n = int(size[3])

	elsize = f.readline().strip().split()
	if elsize[0] != 'ElementSize:':
		raise IOError, "Problem reading data matrix element size"
	n_bytes = int(elsize[1])

	rowmaj = f.readline().strip().split()
	if rowmaj[0] != 'RowMajor:':
		raise IOError, "Problem reading data matrix row major order"
	row_major = int(rowmaj[1])

	datafile = f.readline().strip().split()
	if datafile[0] != 'DataFile:':
		raise IOError, "Problem reading data matrix file name"
	data_file = os.path.abspath(os.path.join(os.path.dirname(orig_data_file),datafile[1]))

	f.close()

	fd = open(data_file, 'rb')
	# orig_data = N.fromstring(fd.read(8*m*n), dtype=N.dtype('d8'), count=m*n).reshape(m,n)
	orig_data = N.fromfile(fd, dtype=N.dtype('d8'), count=m*n).reshape(m,n)
	fd.close()
	
	# Real data center
	# data_center = orig_data.mean(axis=1)

	# For now just calculate min and max here after centering data
	# m = orig_data.shape[0]
	# orig_data = orig_data - data_center.reshape(m,1)
	
	# orig_min = N.matrix(orig_data.min(axis=1))
	# orig_max = N.matrix(orig_data.max(axis=1))
	# Results in m x 2 matrix
	# orig_data_bounds = N.concatenate((orig_min, orig_max), axis=0).T
	
	return orig_data


# --------------------
if __name__ == "__main__":

	tdf = '../../test/mnist12.ipca'
	ldf = '../../test/mnist12_labels.data.hdr'
	df = '../../test/mnist12.data.hdr'		
	
	tree_root, nodes_by_id = read_sambinary_ipcadata(tdf)
	labels = read_sambinary_labeldata(ldf)
	orig_data = read_sambinary_originaldata(df)