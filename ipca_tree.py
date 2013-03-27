import struct
import numpy as N
import collections as C
import pprint
import json
import os

class IPCATree(object):
	
	def __init__(self, filename = None):

		self.data_loaded = False
		self.data_file = None

		# Built so it will automatically load a valid ipca file if given in constructor
		# Otherwise, call SetFileName('file.ipca') and LoadData() separately
		
		if filename:
			try:
				self.SetFileName(filename)
			except:
				print "Problem setting filename"
			
			try:
				self.LoadData()
			except:
				print "Problem loading data"

	# --------------------
	def SetFileName(self, filename):
		"""Set file name manually for Matlab file. Can also do this in constructor."""

		if filename and type(filename) == str:
			self.data_file = os.path.abspath(filename)
		else:
			raise IOError, "filename needs to be a non-empty string"

		if not os.path.isfile(self.data_file):
			raise IOError, "input file does not exist"

	# --------------------
	def LoadData(self):
		"""Routine that does the actual data loading and some format conversion.
		If a valid file name is given in the constructor, then this routine is called
		automatically. If you haven't given a file name in the constructor then you'll
		have to call SetFileName() before calling this."""

		if not self.data_file:
			raise IOError, "No data file: Use SetFileName('file.ipca') before LoadData()"

		print 'Trying to load data set from .ipca file... ', self.data_file

		f = open(self.data_file, 'rb')

		# Tree header
		r_header = f.read(8 + 4 + 4 + 4)
		(epsilon, d, m, minPoints) = struct.unpack("dIIi", r_header)

		self.tree_root = None
		self.nodes_by_id = []
		nodes = C.deque()
		cur = None
		self.lite_tree_root = None
		lite_nodes = C.deque()
		lite_cur = None

		id = 0

		try:
			r_nPhi = f.read(4)
			while r_nPhi:
				(nPhi,) = struct.unpack("i", r_nPhi)
				phi = N.matrix(N.array(struct.unpack("d"*nPhi*m, f.read(8*nPhi*m))).reshape((nPhi,m)))
				sigma = N.array(struct.unpack("d"*nPhi, f.read(8*nPhi)))
				center = N.array(struct.unpack("d"*m, f.read(8*m)))
				mse = N.array(struct.unpack("d"*(d+1), f.read(8*(d+1))))
				dir = N.array(struct.unpack("d"*m, f.read(8*m)))
				(a,) = struct.unpack("d", f.read(8))
				(nPoints,) = struct.unpack("i", f.read(4))
				pts = N.array(struct.unpack("i"*nPoints, f.read(4*nPoints)))
				(r,) = struct.unpack("d", f.read(8))
				(isLeaf,) = struct.unpack("?", f.read(1))
		
		
				# Lite node key names are minimized to reduce transferred JSON size
				# 'i' = 'id'
				# 'c' = 'children'
				# 'v' = 'value'
				
				node = {}
				node['id'] = id
				node['children'] = C.deque()
				lite_node = {}
				lite_node['i'] = id
				lite_node['c'] = C.deque()
				if isLeaf:
					lite_node['v'] = nPoints
		
				if cur == None:
					self.tree_root = node
					self.lite_tree_root = lite_node

				node['r'] = r
				node['phi'] = phi
				node['sigma'] = sigma
				node['dir'] = dir
				node['a'] = a
				node['mse'] = mse
				node['center'] = center
				node['indices'] = pts
				node['sigma2'] = sigma*sigma

				# if previously read node is not empty. 
				# i.e. if node != root
				if cur != None:
		
					# if just-read node is not a leaf
					if not isLeaf:
						# put just-read node in the deque to be visited later
						nodes.append(node)
						lite_nodes.append(lite_node)
			
					# if children array of cur (previously read) is full
					# (I think an alternative to this if not dealing with a binary tree
					#   would be to keep track of everyone's parent node ID and check here 
					#   whether cur is the parent of node)
					if len(cur['children']) == 2:
						cur = nodes.popleft()
						lite_cur = lite_nodes.popleft()
			
					# fill up cur's children list
					node['parent_id'] = cur['id']
					cur['children'].append(node)
					# lite_node['p'] = lite_cur['i']
					lite_cur['c'].append(lite_node)
			
				else:
					cur = node
					lite_cur = lite_node
		
				# Keep a copy arranged by ID, too (relying on sequential IDs)
				self.nodes_by_id.append(node)
				
				r_nPhi = f.read(4)
				id = id + 1
		
		except:
			raise IOError, "Can't load data from file %s" % (self.data_file,)
		
		finally:
			f.close()
			
		self.post_process_nodes(self.tree_root)
		self.post_process_nodes(self.lite_tree_root, 'c', 's')

		# Since nodes now have scale (depth) info attached, can make nice 
		# reference map (lists of lists) indexed first by scale
		self.nodes_by_scale = self.collect_nodes_by_scale(self.nodes_by_id)
		
		# Now that data is loaded, default projection basis is
		# root node first two PCA directions
		# Using Sam's notation for now on matrices / arrays
		self.V = self.nodes_by_id[0]['phi'][:2,:]

	# --------------------
	def post_process_nodes(self, root_node, child_key='children', scale_key='scale'):
	
		# Clear out empty children from tree and convert deques into lists
		# and add scale (depth in tree starting with 0 at root) as we go

		MODE = 'breadth_first'
		# MODE = 'depth_first'

		# Iterative traversal
		#   Note: for Python deque, 
		#	      extendleft / appendleft --> [0, 1, 2] <-- extend / append
		#				               popleft <--             --> pop

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
	def GetLiteTreeJSON(self, pretty = False):
		
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
	data_file = '/Users/emonson/Programming/Sam/test/mnist12.ipca'

	# DataSource loads .ipca file and can generate data from it for other views
	tree = IPCATree(data_file)
	
	# print tree.GetLiteTreeJSON()

		
