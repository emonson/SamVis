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

		# Built so it will automatically load a valid matlab file if given in constructor
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

	def SetFileName(self, filename):
		"""Set file name manually for Matlab file. Can also do this in constructor."""

		if filename and type(filename) == str:
			self.data_file = os.path.abspath(filename)
		else:
			raise IOError, "filename needs to be a non-empty string"

		if not os.path.isfile(self.data_file):
			raise IOError, "input file does not exist"

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
		
		
				node = {}
				node['id'] = id
				node['children'] = C.deque()
				lite_node = {}
				lite_node['id'] = id
				lite_node['children'] = C.deque()
				if isLeaf:
					lite_node['value'] = nPoints
		
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
					cur['children'].append(node)
					lite_cur['children'].append(lite_node)
			
				else:
					cur = node
					lite_cur = lite_node
		
				r_nPhi = f.read(4)
				id = id + 1
		
		except:
			raise IOError, "Can't load data from file %s" % (self.data_file,)
		
		finally:
			f.close()
			
		self.CleanUpChildNodes(self.tree_root)
		self.CleanUpChildNodes(self.lite_tree_root)

	def CleanUpChildNodes(self, root_node):
	
		# Clear out empty children from tree and convert deques into lists

		MODE = 'breadth_first'
		# MODE = 'depth_first'

		# Iterative traversal
		#   Note: for Python deque, 
		#	      extendleft / appendleft --> [0, 1, 2] <-- extend / append
		#				               popleft <--             --> pop

		nodes = C.deque()
		nodes.appendleft(root_node)

		while len(nodes) > 0:
			if MODE == 'breadth_first':
				current_node = nodes.pop()
			elif MODE == 'depth_first':
				current_node = nodes.popleft()
			else:
				break
		
			# Calculate something on the current node
			if 'children' in current_node:
				if len(current_node['children']) == 0:
					del current_node['children']
				else:
					current_node['children'] = list(current_node['children'])
	
			if 'children' in current_node:
				nodes.extendleft(current_node['children'])
				# for child in current_node['children']:
				# 	nodes.appendleft(child)

	def GetLiteTreeJSON(self, pretty = False):
		
		if pretty:
			return json.dumps(self.lite_tree_root, indent=2)
		else:
			return json.dumps(self.lite_tree_root)
	
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

if __name__ == "__main__":

	# from tkFileDialog import askopenfilename
	# data_file = askopenfilename()
	data_file = '/Users/emonson/Programming/Sam/test/mnist12.ipca'

	# DataSource loads .ipca file and can generate data from it for other views
	tree = IPCATree(data_file)
	
	print tree.GetLiteTreeJSON()

		
