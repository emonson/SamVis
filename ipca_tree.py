import struct
import numpy as N
import collections as C
import pprint
import json
import os
import io

class IPCATree(object):
	
	def __init__(self, filename = None):

		self.data_loaded = False
		self.data_file = None
		self.label_file = None
		self.labels = None
		self.lite_tree_root = None
		self.nodes_by_id = None

		# Built so it will automatically load a valid ipca file if given in constructor
		# Otherwise, call SetFileName('file.ipca') and LoadData() separately
		
		if filename:
# 			try:
# 				self.SetFileName(filename)
# 			except:
# 				print "Problem setting filename"
# 			
# 			try:
# 				self.LoadData()
# 			except:
# 				print "Problem loading data"
			self.SetFileName(filename)
			self.LoadData()

	# --------------------
	def SetFileName(self, filename):
		"""Set file name manually for IPCA file. Can also do this in constructor."""

		if filename and type(filename) == str:
			self.data_file = os.path.abspath(filename)
		else:
			raise IOError, "filename needs to be a non-empty string"

		if not os.path.isfile(self.data_file):
			raise IOError, "input file does not exist"

	# --------------------
	def SetLabelFileName(self, filename):
		"""Set file name manually for label file."""

		if filename and type(filename) == str:
			self.label_file = os.path.abspath(filename)
		else:
			raise IOError, "filename needs to be a non-empty string"

		if not os.path.isfile(self.label_file):
			raise IOError, "input file does not exist"

	# --------------------
	def LoadLabelData(self):
		
		if not self.label_file:
			raise IOError, "No label file set: Use SetLabelFileName('labelfile.data.hdr')"
		
		f = open(self.label_file, 'r')
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
		
		fb = open(os.path.splitext(self.label_file)[0], 'rb')
		self.labels = N.fromfile(fb, dtype=N.dtype('i' + str(n_bytes)), count=n_elements)
		fb.close()
		
		# If the data is already loaded, compute mean labels
		# TODO: Really need to do something more robust for data/label loading order...
		if self.data_loaded and self.nodes_by_id:
			self.post_process_mean_labels()
		
	# --------------------
	def LoadData(self):
		"""Routine that does the actual data loading and some format conversion.
		If a valid file name is given in the constructor, then this routine is called
		automatically. If you haven't given a file name in the constructor then you'll
		have to call SetFileName() before calling this."""

		if not self.data_file:
			raise IOError, "No data file: Use SetFileName('file.ipca') before LoadData()"

		print 'Trying to load data set from .ipca file... ', self.data_file

		f = io.open(self.data_file, 'rb', buffering=65536)

		# Tree header
		dt = N.dtype([('epsilon', N.dtype('d8')), 
									('d', N.dtype('I4')), 
									('m', N.dtype('I4')), 
									('minPoints', N.dtype('i4'))])
		header = N.frombuffer(f.read(8+4+4+4), dtype=dt, count=1)
		epsilon = header['epsilon']
		d = header['d']
		m = header['m']
		minPoints = header['minPoints']

		self.tree_root = None
		self.nodes_by_id = []
		nodes = C.deque()
		cur = None

		id = 0

# 		try:
		r_nPhi = f.read(4)
		while r_nPhi:
			nPhi = int(N.frombuffer(r_nPhi, N.dtype('i4'), count=1))
			
			phi = N.matrix(N.frombuffer(f.read(8*nPhi*m), N.dtype('d8'), count=nPhi*m).reshape(nPhi,m))
			sigma = N.frombuffer(f.read(8*nPhi), N.dtype('d8'), count=nPhi)
			center = N.frombuffer(f.read(8*m), N.dtype('d8'), count=m)
			mse = N.frombuffer(f.read(8*(d+1)), N.dtype('d8'), count=(d+1))
			dir = N.frombuffer(f.read(8*m), N.dtype('d8'), count=m)
			
			a = float(N.frombuffer(f.read(8), N.dtype('d8'), count=1))
			nPoints = int(N.frombuffer(f.read(4), N.dtype('i4'), count=1))
			
			pts = N.frombuffer(f.read(4*nPoints), N.dtype('i4'), count=nPoints)
			
			r = float(N.frombuffer(f.read(8), N.dtype('d8'), count=1))
			isLeaf = bool(N.frombuffer(f.read(1), N.dtype('?1'), count=1))
	
			node = {}
			node['id'] = id
			node['children'] = C.deque()
	
			if cur == None:
				self.tree_root = node

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
			self.nodes_by_id.append(node)
			
			r_nPhi = f.read(4)
			id = id + 1
		
# 		except:
# 			raise IOError, "Can't load data from file %s" % (self.data_file,)
		
# 		finally:
		f.close()
			
		self.post_process_nodes(self.tree_root)

		# Since nodes now have scale (depth) info attached, can make nice 
		# reference map (lists of lists) indexed first by scale
		self.nodes_by_scale = self.collect_nodes_by_scale(self.nodes_by_id)
		
		# Now that data is loaded, default projection basis is
		# root node first two PCA directions
		# Using Sam's notation for now on matrices / arrays
		self.V = self.nodes_by_id[0]['phi'][:2,:].T
		
		# HACK: Using node 0 center as data center...
		self.data_center = self.tree_root['center']
		
		self.data_loaded = True

	# --------------------
	def post_process_nodes(self, root_node, child_key='children', scale_key='scale'):
	
		# Clear out empty children from tree and convert deques into lists
		# and add scale (depth in tree starting with 0 at root) as we go

		MODE = 'breadth_first'
		# MODE = 'depth_first'

		# Iterative traversal
		#		Note: for Python deque, 
		#				extendleft / appendleft --> [0, 1, 2] <-- extend / append
		#											 popleft <--						 --> pop

		nodes = C.deque()
		scales = C.deque()
		nodes.appendleft(root_node)
		scales.appendleft(0)

		while len(nodes) > 0:
			# Get next node to process from deque for iterative traversal
			if MODE == 'breadth_first':
				current_node = nodes.pop()
				current_scale = scales.pop()
			elif MODE == 'depth_first':
				current_node = nodes.popleft()
				current_scale = scales.popleft()
			else:
				break
		
			# Add scale (depth) on to current node
			current_node[scale_key] = current_scale
			
			# Delete empty children deques and change rest into lists
			if child_key in current_node:
				if len(current_node[child_key]) == 0:
					del current_node[child_key]
				else:
					current_node[child_key] = list(current_node[child_key])
	
			# Add on to deque for ongoing iterative tree traveral
			if child_key in current_node:
				nodes.extendleft(current_node[child_key])
				scales.extendleft([current_scale+1]*len(current_node[child_key]))

	# --------------------
	def collect_nodes_by_scale(self, nodes_by_id, scale_key='scale'):
		"""Returns nodes_by_scale"""
		
		if len(nodes_by_id) == 0 or scale_key not in nodes_by_id[0]:
			return None
		
		# This will be a list of lists
		nodes_by_scale = []
		
		for node in nodes_by_id:
			scale = node[scale_key]
			
			if scale > (len(nodes_by_scale) - 1):
				nodes_by_scale.extend(list([[]]*((scale+1)-len(nodes_by_scale))))
			
			nodes_by_scale[scale].append(node)
		
		return nodes_by_scale
	
	# --------------------
	def post_process_mean_labels(self):
		"""Modifies self.nodes_by_id in place finding mean label value"""
		
		for node in self.nodes_by_id:
			indices = node['indices']
			node['label'] = N.mean(self.labels[indices])
	
	# --------------------
	def calculate_node_ellipse(self, node_id):
		"""Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse"""
		
		node = self.nodes_by_id[node_id]
		
		# Compute projection of this node's covariance matrix
		A = node['phi'].T
		sigma = N.matrix(N.diag(node['sigma']))
		center = node['center']
		
		A = A * N.sqrt(sigma)

		C1 = self.V.T * A
		
		C = C1 * C1.T

		# ALT METHOD for transforming the unit circle according to projected covariance
		# Compute svd in projected space to find rx, ry and rotation for ellipse in D3 vis
		U, S, V = N.linalg.svd(C)

		# Project mean
		xm = N.dot(self.V.T, center)
		xrm = N.dot(self.V.T, self.data_center)	# NOTE: using node[0] center as data center...
		xm = N.squeeze(N.asarray(xm - xrm))
		
		# Calculate scalings (not needed because it's in sigma
		# N.squeeze(N.asarray(N.sum(N.square(a),1)))
		
		# Calculate angles
		phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
		# t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))
		
		result_list = N.round((xm[0], xm[1], S[0], S[1], phi_deg), 2).tolist()
		result_list.append(node['id'])
		
		return result_list
	
	# --------------------
	def RegenerateLiteTree(self, children_key='c', parent_id_key='p', key_dict = {'id':'i', 
																					'npoints':'v',
																					'scale':'s',
																					'label':'l'}
																					):
		"""Keeping full tree as true record of data, and regenerate new lite tree
		when needed, like after labels update. Children and parent keys required,
		so they're not in the key string map (originals assumed to be 'children' and 'parent_id')"""
		
		# NOTE: Cheating a bit by relying on nodes_by_id being in breadth-first order so
		#		children's parents already exist as the array is being populated.
		#		If this becomes a problem, need to build by traversing tree.
		
		# This is only for helping fill in children. Not keeping it around.
		lite_nodes_by_id = []
		
		for node in self.nodes_by_id:
			lite_node = {}
			if 'children' in node:
				lite_node[children_key] = []
			lite_nodes_by_id.append(lite_node)
			
			if 'parent_id' in node:
				parent_id = node['parent_id']
				# NOTE: Not copying parent id to lite tree for now!
				# lite_node[parent_id_key] = parent_id
				lite_nodes_by_id[parent_id][children_key].append(lite_node)
			else:
				# This assignment of root node keeps whole lite tree
				self.lite_tree_root = lite_node
			
			for k,v in key_dict.items():
				lite_node[v] = node[k]

	# --------------------
	def SetBasisID(self, id):
	
		if (id is not None) and self.data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			self.V = self.nodes_by_id[id]['phi'][:2,:].T

	# --------------------
	def GetMaxID(self):
	
		if self.data_loaded:
			return len(self.nodes_by_id)-1

	# --------------------
	def GetScaleEllipses(self, id = None):
		"""Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
	
		if (id is not None) and self.data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			scale = self.nodes_by_id[id]['scale']
			
			ellipse_params = []
			labels = []
			# Always include node 0 for now
			if scale != 0:
				ellipse_params.append(self.calculate_node_ellipse(0))
				labels.append(self.nodes_by_id[0]['label'])
			for node in self.nodes_by_scale[scale]:
				ellipse_params.append(self.calculate_node_ellipse(node['id']))
				labels.append(node['label'])
			
			round_labels = N.round(labels, 2).tolist()
			return_obj = {'data':ellipse_params, 'labels':round_labels}
			
			return return_obj
		
	# --------------------
	def GetScaleEllipsesJSON(self, id = None):
		"""Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""
	
		return json.dumps(self.GetScaleEllipses(id))
		
	# --------------------
	def GetLiteTreeJSON(self, pretty = False):
		
				# Lite node key names are minimized to reduce transferred JSON size
				# 'i' = 'id'
				# 'c' = 'children'
				# 'v' = 'value'
				# 's' = 'scale'
				# 'l' = 'label'
		if not self.lite_tree_root:
			self.RegenerateLiteTree()
		
		if pretty:
			return json.dumps(self.lite_tree_root, indent=2)
		else:
			return json.dumps(self.lite_tree_root)
	
	# --------------------
	def WriteLiteTreeJSON(self, filename, pretty = False):
	
		out_file = None
		
		if filename and type(filename) == str:
			out_file = os.path.abspath(filename)
		else:
			raise IOError, "output filename needs to be a non-empty string"

		f = open(out_file, 'w')
		if pretty:
			f.write(self.GetLiteTreeJSON(True))
		else:
			f.write(self.GetLiteTreeJSON())
		f.close()

# --------------------
# --------------------
if __name__ == "__main__":

	# from tkFileDialog import askopenfilename
	# data_file = askopenfilename()
# 	data_file = '/Users/emonson/Programming/Sam/test/orig2-copy2.ipca'
# 	label_file = '/Users/emonson/Programming/Sam/test/labels02.data.hdr'
	data_file = '/Users/emonson/Programming/Sam/test/mnist12.ipca'
	label_file = '/Users/emonson/Programming/Sam/test/mnist12_labels.data.hdr'

	# DataSource loads .ipca file and can generate data from it for other views
	tree = IPCATree(data_file)
	tree.SetLabelFileName(label_file)
	tree.LoadLabelData()
	tree.GetScaleEllipsesJSON(900)
	
	# print tree.GetLiteTreeJSON()

		
