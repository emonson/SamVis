import io
import struct
import numpy as N
import collections as C
import json
import os

import time

# http://stackoverflow.com/questions/8889083/how-to-time-execution-time-of-a-batch-of-code-in-python
def time_this(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print 'func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts)
        return result

    return timed


def read_data_info(datapath):
	
	if os.path.isdir(datapath):
		data_info = json.loads(open(os.path.join(datapath, 'data_info.json')).read())
		
		return data_info
	
@time_this
def read_sambinary_v3_ipcadata(tree_data_filename):
	""" Read IPCA tree and data from Sam's binary file format which he dumps variables
	from his tree in C++. Return root of tree (which is just a bunch of dictionaries
	linked to each other through children and parent) and list of same node element objects
	but ordered by id rather than in a tree structure."""
	
	f = io.open(tree_data_filename, 'rb', buffering=65536)

	# Tree header
	dt = N.dtype([('epsilon', N.dtype('f8')), 
								('m', N.dtype('u4')), 
								('minPoints', N.dtype('i4'))])
	header = N.frombuffer(f.read(8+4+4), dtype=dt, count=1)
	epsilon = header['epsilon']
	m = header['m']
	minPoints = header['minPoints']

	tree_root = None
	nodes_by_id = {}
	nodes = C.deque()
	cur = None

	id = 0

# 		try:
	r_nPhi = f.read(4)
	while r_nPhi:

		nPhi = int(N.frombuffer(r_nPhi, N.dtype('i4'), count=1))
		nSplit = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
		nKids = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
		childmap = {}
		for ii in range(nKids):
			i1 = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
			i2 = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
			childmap[i1] = i2
			
		phi = N.matrix(N.frombuffer(f.read(8*nPhi*m), N.dtype('f8'), count=nPhi*m).reshape(nPhi,m))
		sigma = N.frombuffer(f.read(8*nPhi), N.dtype('f8'), count=nPhi)
		center = N.frombuffer(f.read(8*m), N.dtype('f8'), count=m)
		mse = N.frombuffer(f.read(8*(nPhi+1)), N.dtype('f8'), count=(nPhi+1))
		dir = N.matrix(N.frombuffer(f.read(8*m*nSplit), N.dtype('f8'), count=m*nSplit).reshape(nSplit,m))
		
		a = N.frombuffer(f.read(8*nSplit), N.dtype('f8'), count=nSplit)
		nPoints = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
		indices = N.frombuffer(f.read(4*nPoints), N.dtype('i4'), count=nPoints)
		l2Radius = float(N.frombuffer(f.read(8), N.dtype('f8'), count=1))

		node = {}
		node['id'] = id
		node['nSplit'] = nSplit
		node['nKids'] = nKids
		node['children'] = C.deque()

		node['l2Radius'] = l2Radius
		node['phi'] = phi
		node['sigma'] = sigma
		node['dir'] = dir
		node['a'] = a
		node['mse'] = mse
		node['center'] = center
		node['indices'] = indices
		node['npoints'] = nPoints
		node['sigma2'] = sigma*sigma

		# if previously read node is not empty. 
		# i.e. if node != root
		if cur == None:
			tree_root = node
			cur = node
		else:
			# if just-read node is not a leaf
			if node['nKids'] > 0:
				# put just-read node in the deque to be visited later
				nodes.append(node)
	
			# if children array of cur (previously read) is full
			# (I think an alternative to this if not dealing with a binary tree
			#		would be to keep track of everyone's parent node ID and check here 
			#		whether cur is the parent of node)
			if len(cur['children']) == cur['nKids']:
				cur = nodes.popleft()
	
			# fill up cur's children list
			node['parent_id'] = cur['id']
			cur['children'].append(node)
	
		# Keep a copy indexed by ID, too
		nodes_by_id[id] = node
		
		r_nPhi = f.read(4)
		
		# NOTE: I would prefer some sort of ID saved with each node...
		id = id + 1
	
# 		except:
# 			raise IOError, "Can't load data from file %s" % (tree_data_file,)
	
# 		finally:
	f.close()
	
	return tree_root, nodes_by_id
	
	
def read_sambinary_labeldata(label_data_filename, data_type):
	"""Read IPCA tree label data from Sam's binary format, which is basically an
	R datastructure, I think... data_type == 'i' or 'f'"""
	
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
	
	labels = None
	fb = open(os.path.splitext(label_data_filename)[0], 'rb')
	if data_type == 'i':
		labels = N.fromfile(fb, dtype=N.dtype('i' + str(n_bytes)), count=n_elements)
	elif data_type == 'f':
		labels = N.fromfile(fb, dtype=N.dtype('f' + str(n_bytes)), count=n_elements)
	fb.close()
	
	return labels

def checked_filename(filename):
	if filename and isinstance(filename, basestring):
		return  os.path.abspath(filename)
	else:
		raise IOError, "filename needs to be a non-empty string"

	if not os.path.isfile(self.label_file):
		raise IOError, "input file does not exist"
	
	return ""


def read_sambinary_originaldata(orig_data_file, data_type):
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
	if data_type == 'i':
		orig_data = N.fromfile(fd, dtype=N.dtype('i' + str(n_bytes)), count=m*n).reshape(m,n, order='F')
	elif data_type == 'f':
		orig_data = N.fromfile(fd, dtype=N.dtype('f' + str(n_bytes)), count=m*n).reshape(m,n, order='F')
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

def read_sambinary_originaldata_linear(orig_data_file, data_type):
	"""Read the original data used for IPCA but don't reshape it into 2d like it should be.
	   Used for data transformations using numpy where array.tofile() would save in C order,
	   but here we need to reshape in F order to get the original shape."""

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
	if data_type == 'i':
		orig_data = N.fromfile(fd, dtype=N.dtype('i' + str(n_bytes)), count=m*n)
	elif data_type == 'f':
		orig_data = N.fromfile(fd, dtype=N.dtype('f' + str(n_bytes)), count=m*n)
	fd.close()
	
	return orig_data


# --------------------
if __name__ == "__main__":

	data_path = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2'
	
	data_info = read_data_info(data_path)
	
	tree_data_file = os.path.join(data_path, data_info['full_tree']['filename'])
	tree_root, nodes_by_id = read_sambinary_v3_ipcadata(tree_data_file)
	
	labels = {}
	for name, info in data_info['original_data']['labels'].iteritems():
		label_data_file = os.path.join(data_path, info['filename'])
		labels[name] = read_sambinary_labeldata(label_data_file, info['data_type'])
	
	orig_data_path = os.path.join(data_path, data_info['original_data']['filename'])
	orig_data = read_sambinary_originaldata(orig_data_path, data_info['original_data']['data_type'])
