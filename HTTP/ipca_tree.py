import ipca_sambinary_read as IR
import ipca_hdf5_read as IH
import numpy as N
from scipy import stats
import collections as C
import pprint
import simplejson
import os

# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
class PrettyPrecision2SciFloat(float):
	def __repr__(self):
		return '%.2g' % self

# --------------------
class IPCATree(object):
	
	def __init__(self, filename = None):

		self.tree_data_loaded = False
		self.tree_data_file = None
		self.label_file = None
		self.label_data_loaded = False	# not used...
		self.labels = None
		self.orig_data_file = None
		self.orig_data_loaded = False
		self.orig_data = None
		self.orig_data_min = None
		self.orig_data_max = None
		self.lite_tree_root = None
		self.nodes_by_id = None
		self.all_ellipse_params = None
		self.basis_id = None

		# Built so it will automatically load a valid ipca file if given in constructor
		# Otherwise, call SetTreeFileName('file.ipca') and LoadTreeData() separately
		
		if filename:
# 			try:
# 				self.SetTreeFileName(filename)
# 			except:
# 				print "Problem setting filename"
# 			
# 			try:
# 				self.LoadTreeData()
# 			except:
# 				print "Problem loading data"
			self.SetTreeFileName(filename)
			self.LoadTreeData()

	# --------------------
	def SetLabelFileName(self, filename):
		"""Set file name manually for label file."""

		self.label_file = IH.checked_filename(filename)

	# --------------------
	def LoadLabelData(self):
		
		if not self.label_file:
			raise IOError, "No label file set: Use SetLabelFileName('labelfile.data.hdr')"
		
		# Read labels from binary file
		self.labels = IR.read_sambinary_labeldata(self.label_file)
		# self.labels = IH.read_hdf5_labeldata(self.label_file)
		
		# If the data is already loaded, compute mean labels
		# TODO: Really need to do something more robust for data/label loading order...
		if self.tree_data_loaded and self.nodes_by_id:
			self.post_process_mean_labels()
		
	# --------------------
	def SetTreeFileName(self, filename):
		"""Set file name manually for IPCA file. Can also do this in constructor."""

		self.tree_data_file = IR.checked_filename(filename)
		# self.tree_data_file = IH.checked_filename(filename)

	# --------------------
	def LoadTreeData(self):
		"""Routine that does the actual data loading and some format conversion.
		If a valid file name is given in the constructor, then this routine is called
		automatically. If you haven't given a file name in the constructor then you'll
		have to call SetTreeFileName() before calling this."""

		if not self.tree_data_file:
			raise IOError, "No data file: Use SetTreeFileName('file.ipca') before LoadTreeData()"

		print 'Trying to load data set from .ipca file... ', self.tree_data_file

		# Read data from binary file
		# self.tree_root, self.nodes_by_id = IR.read_sambinary_ipcadata(self.tree_data_file)
		self.tree_root, self.nodes_by_id = IR.read_sambinary_v3_ipcadata(self.tree_data_file)
		# self.tree_root, self.nodes_by_id = IH.read_hdf5_ipcadata(self.tree_data_file)
			
		self.post_process_nodes(self.tree_root)

		# Since nodes now have scale (depth) info attached, can make nice 
		# reference map (lists of lists) indexed first by scale
		self.nodes_by_scale = self.collect_nodes_by_scale(self.nodes_by_id)
		
		# Using node 0 center as data center
		self.data_center = self.tree_root['center']
		
		self.tree_data_loaded = True

		# Now that data is loaded, default projection basis is
		# root node first two PCA directions
		# Using Sam's notation for now on matrices / arrays
		# self.V = self.nodes_by_id[0]['phi'][:2,:].T
		self.SetBasisID_ReprojectAll(0)
		
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
		
		# TODO: since nodes_by_id is now a dictionary rather than a list, need
		#  to make sure this doesn't need to be traversed in any particular order...
		for id, node in nodes_by_id.iteritems():
			scale = node[scale_key]
			
			if scale > (len(nodes_by_scale) - 1):
				nodes_by_scale.extend(list([[]]*((scale+1)-len(nodes_by_scale))))
			
			nodes_by_scale[scale].append(node)
		
		return nodes_by_scale
	
	# --------------------
	def post_process_mean_labels(self):
		"""Modifies self.nodes_by_id in place finding mean label value"""
		
		for id, node in self.nodes_by_id.iteritems():
			indices = node['indices']
			node['labels'] = {}
			for lname,larray in self.labels.iteritems():
				node['labels'][lname] = N.mean(larray[indices])
	
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
		xrm = N.dot(self.V.T, self.data_center)
		xm = N.squeeze(N.asarray(xm - xrm))
		
		# Calculate scalings (not needed because it's in sigma
		# N.squeeze(N.asarray(N.sum(N.square(a),1)))
		
		# Calculate angles
		phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
		# t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))
		
		# How many sigma ellipses cover
		s_mult = 2.0
		result_list = N.round((xm[0], xm[1], s_mult*S[0], s_mult*S[1], phi_deg), 2).tolist()
		result_list.append(node['id'])
		
		return result_list
	
	# --------------------
	def calculate_ellipse_bounds(self, e_params):
		"""Rough calculation of ellipse bounds by centers +/- max radius for each"""
		
		# Ellipse params is a list of tuples (X, Y, RX, RY, Phi, i)
		params_array = N.array(e_params)
		X = params_array[:,0]
		Y = params_array[:,1]
		
		maxR = N.max(params_array[:,2:4], axis=1)
		minX = N.min(X-maxR)
		maxX = N.max(X+maxR)
		minY = N.min(Y-maxR)
		maxY = N.max(Y+maxR)
		
		return [(minX, maxX), (minY, maxY)]
	
	# --------------------
	def RegenerateLiteTree(self, children_key='c', parent_id_key='p', key_dict = {'id':'i', 
																					'npoints':'v',
																					'scale':'s'}
																					):
		"""Keeping full tree as true record of data, and regenerate new lite tree
		when needed, like after labels update. Children and parent keys required,
		so they're not in the key string map (originals assumed to be 'children' and 'parent_id')"""
		
		# Doing a two-pass strategy for constructing the tree. Fill in basic lite_nodes_by_id
		# first, with all object-local fields, then take another pass through, filling in the
		# children after being assured all nodes exist.
		
		# This is only for helping fill in children. Not keeping it around.
		lite_nodes_by_id = {}
		
		# First pass with object-local fields
		for id,node in self.nodes_by_id.iteritems():
			lite_node = {}
			# NOTE: Not copying parent id to lite tree for now!
			# if 'parent_id' in node:
				# lite_node[parent_id_key] = parent_id
			# All other values copied over
			for k,v in key_dict.items():
				lite_node[v] = node[k]
			
			lite_nodes_by_id[id] = lite_node
		
		# Second pass for children list
		for id,node in self.nodes_by_id.iteritems():
			if 'children' in node:
				lite_nodes_by_id[id][children_key] = []
				for child in node['children']:
					cid = child['id']
					lite_nodes_by_id[id][children_key].append(lite_nodes_by_id[cid])
		
		# This assignment of root node keeps whole lite tree
		self.lite_tree_root = lite_nodes_by_id[self.tree_root['id']]

	# --------------------
	def SetBasisID(self, id):
	
		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			self.V = self.nodes_by_id[id]['phi'][:2,:].T

	# --------------------
	def SetBasisID_ReprojectAll(self, id):
	
		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			if id != self.basis_id:
				self.basis_id = id
				self.V = self.nodes_by_id[id]['phi'][:2,:].T
				
				self.all_ellipse_params = []
				for id,node in self.nodes_by_id.iteritems():
					self.all_ellipse_params.append(self.calculate_node_ellipse(node['id']))

	# --------------------
	def GetMaxID(self):
	
		if self.tree_data_loaded:
			return len(self.nodes_by_id)-1

	# --------------------
	def GetScaleEllipses(self, id = None):
		"""Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
	
		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			scale = self.nodes_by_id[id]['scale']
			
			ellipse_params = []
			# Always include node 0 for now
			if scale != 0:
				ellipse_params.append(self.calculate_node_ellipse(0))
			for node in self.nodes_by_scale[scale]:
				ellipse_params.append(self.calculate_node_ellipse(node['id']))
			
			bounds = self.calculate_ellipse_bounds(ellipse_params)
			return_obj = {'data':ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetScaleEllipsesJSON(self, id = None):
	
		return simplejson.dumps(self.GetScaleEllipses(id))
		
	# --------------------
	def GetContextEllipses(self, id = None, bkgd_scale = None):
		"""Take in node_id and scale for background ellipses for vis context.
		   Project into parent scale basis, and return ellipses for parent, self, sibling and
		   self and sibling's children, as well as background scale ellipses."""

		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			if (bkgd_scale is not None) and (bkgd_scale < len(self.nodes_by_scale)):
			
				ellipse_params = []
				bkgd_ellipse_params = []
				
				selected_node = self.nodes_by_id[id]
				
				# If this is not the root node
				if 'parent_id' in selected_node:
					# Project into parent space
					parent_id = selected_node['parent_id']
				else:
					parent_id = 0
				
				# NOTE: In principle, might not want to go down two scales if choosing root node...
				self.SetBasisID(parent_id)
				ellipse_params.append(self.calculate_node_ellipse(parent_id))

				parent_node = self.nodes_by_id[parent_id]
				# also get children
				for node in parent_node['children']:
					ellipse_params.append(self.calculate_node_ellipse(node['id']))
					# and children of children
					if 'children' in node:
						for child_node in node['children']:
							ellipse_params.append(self.calculate_node_ellipse(child_node['id']))
				
				for node in self.nodes_by_scale[bkgd_scale]:
					bkgd_ellipse_params.append(self.calculate_node_ellipse(node['id']))
				bounds = self.calculate_ellipse_bounds(ellipse_params + bkgd_ellipse_params)
				return_obj = {'foreground':ellipse_params, 'background':bkgd_ellipse_params, 'bounds':bounds}

				return return_obj
		
	# --------------------
	def GetContextEllipsesJSON(self, id = None, bkgd_scale = None):
	
		return simplejson.dumps(self.GetContextEllipses(id, bkgd_scale))
		
	# --------------------
	def GetScaleEllipses_NoProjection(self, id = None):
		"""Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
	
		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			scale = self.nodes_by_id[id]['scale']
			
			ellipse_params = []
			# Always include node 0 for now
			if scale != 0:
				ellipse_params.append(self.all_ellipse_params[0])
			for node in self.nodes_by_scale[scale]:
				ellipse_params.append(self.all_ellipse_params[node['id']])
			
			bounds = self.calculate_ellipse_bounds(ellipse_params)
			return_obj = {'data':ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetAllEllipses_NoProjection(self):
		"""Return dict of all ellipses in tree"""
	
		if self.tree_data_loaded:
			
			bounds = self.calculate_ellipse_bounds(self.all_ellipse_params)
			return_obj = {'data':self.all_ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
	def pretty_sci_floats(self, obj):
	
		if isinstance(obj, float):
			return PrettyPrecision2SciFloat(obj)
		elif isinstance(obj, dict):
			return dict((k, self.pretty_sci_floats(v)) for k, v in obj.items())
		elif isinstance(obj, (list, tuple)):
			return map(self.pretty_sci_floats, obj)             
		return obj

	# --------------------
	def GetEllipseCenterAndFirstTwoBases(self, id = None):
		"""Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
	
		if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
			
			# WARNING: TODO: REMOVE MAGIC NUMBERS!!
			c1 = 28
			c2 = 28
						
			center = self.nodes_by_id[id]['center'].reshape(c1,c2).tolist()
			basis1 = self.nodes_by_id[id]['phi'][0,:].reshape(c1,c2).tolist()
			basis2 = self.nodes_by_id[id]['phi'][1,:].reshape(c1,c2).tolist()
			return_obj = {'center':center, 'center_range':(N.min(center), N.max(center)),
			              'basis1':basis1, 'basis1_range':(N.min(basis1), N.max(basis1)),
			              'basis2':basis2, 'basis2_range':(N.min(basis2), N.max(basis2))}

			return return_obj
		
	# --------------------
	def GetScaleEllipses_NoProjectionJSON(self, id = None):
		"""Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""
	
		return simplejson.dumps(self.GetScaleEllipses_NoProjection(id))
		
	# --------------------
	def GetAllEllipses_NoProjectionJSON(self):
		"""Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""
	
		return simplejson.dumps(self.GetAllEllipses_NoProjection())
		
	# --------------------
	def GetEllipseCenterAndFirstTwoBasesJSON(self, id = None):
		"""Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""

		return simplejson.dumps(self.pretty_sci_floats(self.GetEllipseCenterAndFirstTwoBases(id)))
		
	# --------------------
	# --------------------
	def GetScalarsByNameJSON(self, name = None):
		"""Take in scalar "name" and get out JSON of scalars for all nodes by id"""
		
		if name:
			if name in self.labels:
				labels = N.zeros((len(self.nodes_by_id),))
				for id,node in self.nodes_by_id.iteritems():
					labels[id] = node['labels'][name]
				return simplejson.dumps(N.round(labels, 2).tolist())
		

	# --------------------
	def GetAggregatedScalarsByNameJSON(self, name = None, aggregation = 'mean'):
		"""Take in scalar "name" and aggregation method
		and get out JSON of scalars for all nodes by id, calculated 'on the fly'.
		aggregation = 'mean', 'mode', 'hist'...
		NOTE: only works with non-negative integer labels!!"""
		
		if name:
			if name in self.labels:
				labels_array = self.labels[name]
				
				# Average of only requested scalar
				if aggregation == 'mean':
					labels = N.zeros((len(self.nodes_by_id),))
					for id,node in self.nodes_by_id.iteritems():
						indices = node['indices']
						labels[id] = N.mean(labels_array[indices])
					output = N.round(labels,2).tolist()
					print output
						
				# Winner is most highly represented label
				# TODO: decide on better determiner for ties...
				elif aggregation == 'mode':
					labels = N.zeros((len(self.nodes_by_id),), dtype='int')
					for id,node in self.nodes_by_id.iteritems():
						indices = node['indices']
						counts = N.bincount(labels_array[indices])
						labels[id] = N.argmax(counts)
					output = labels.tolist()
				
				# 'hist'
				elif aggregation == 'hist':
					unique_labels = N.unique(labels_array)
					# want to be able to look up the indices of each of the labels
					# for cases in which they're not sequential and individual nodes where
					# not all labels are present
					reverse_lookup = N.zeros(N.max(unique_labels)+1, dtype='int')-1
					for ii,ul in enumerate(unique_labels):
						reverse_lookup[ul] = ii
					n_bins = len(unique_labels)
					labels = N.zeros((len(self.nodes_by_id),n_bins),dtype='int')
					for id,node in self.nodes_by_id.iteritems():
						indices = node['indices']
						bincount = N.bincount(labels_array[indices])
						node_unique_labels = N.nonzero(bincount)
						label_indices = reverse_lookup[node_unique_labels]
						labels[id,label_indices] = bincount[node_unique_labels]
					output = labels.tolist()
								
				# default to old average code
				else:
					labels = N.zeros((len(self.nodes_by_id),))
					for id,node in self.nodes_by_id.iteritems():
						labels[id] = node['labels'][name]
					output = N.round(labels,2).tolist()

				return simplejson.dumps(output)


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
			return simplejson.dumps(self.lite_tree_root, indent=2)
		else:
			return simplejson.dumps(self.lite_tree_root)
	
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
	
	# v2 sambinary
	# tree_file = '/Users/emonson/Programming/Sam/test/mnist12.ipca'
	# label_file = '/Users/emonson/Programming/Sam/test/mnist12_labels.data.hdr'
	# data_file = '/Users/emonson/Programming/Sam/test/mnist12.data.hdr'

	# v3 sambinary
	tree_file = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2/tree.ipca'
	label_file = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2/labels.data.hdr'

	# HDF5
	# tree_file = '/Users/emonson/Programming/Sam/test/test1_mnist12.hdf5'
	# label_file = '/Users/emonson/Programming/Sam/test/test1_mnist12.hdf5'

	# DataSource loads .ipca file and can generate data from it for other views
	tree = IPCATree(tree_file)
	tree.SetLabelFileName(label_file)
	tree.LoadLabelData()
	# tree.SetOriginalDataFileName(data_file)
	# tree.LoadOriginalData()
	# tree.GetScaleEllipsesJSON(900)
	
	# print tree.GetLiteTreeJSON()

		
