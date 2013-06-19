import simplejson
import os
import numpy as N
import path_json_read as PR

# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
class PrettyPrecision2SciFloat(float):
	def __repr__(self):
		return '%.2g' % self

# --------------------
class PathObj(object):
	
	def __init__(self, dirname = None):

		# Path data itself
		self.path_data_loaded = False
		self.path_data_dir = None
		self.d_info = None
		self.netpoints = None
		self.path_info = None
		self.sim_opts = None
		
		# For projection of district ellipses into a certain basis
		self.basis_id = None
		self.proj_basis = None
		self.data_center = None
		self.all_ellipse_params = None

		# Built so it will automatically load a valid ipca file if given in constructor
		# Otherwise, call SetTreeFileName('file.ipca') and LoadTreeData() separately
		
		if dirname:
			# TODO: For production code, set try/catch block on load
			self.SetDataDirName(dirname)
			self.LoadPathData()

	# --------------------
	def SetDataDirName(self, dirname):
		"""Set file name for original data file."""

		if dirname and type(dirname) == str:
			self.path_data_dir = os.path.abspath(dirname)
		else:
			raise IOError, "filename needs to be a non-empty string"

		if not os.path.isdir(self.path_data_dir):
			raise IOError, "input data directory does not exist"

	# --------------------
	def LoadPathData(self):
		"""Routine that does the actual data loading.
		If a valid directory name is given in the constructor, then this routine is called
		automatically. If you haven't given a data directory name in the constructor then you'll
		have to call SetDataDirName() before calling this."""

		if not self.path_data_dir:
			raise IOError, "No data directory: Use SetDataDirName('json_blah') before LoadPathData()"

		print 'Trying to load data set from directory ', self.path_data_dir

		self.d_info = PR.load_d_info( os.path.join(self.path_data_dir, 'd_info.json') )
		self.netpoints = PR.load_netpoints( os.path.join(self.path_data_dir, 'netpoints.json') )
		self.path_info = PR.load_trajectory( os.path.join(self.path_data_dir, 'trajectory.json') )
		self.sim_opts = PR.load_sim_opts( os.path.join(self.path_data_dir, 'sim_opts.json') )
		
		self.path_data_loaded = True
		# HACK: data_center
		self.data_center = N.zeros(self.d_info[0]['mu'].shape)
		self.ResetBasis()
		
	# --------------------
	def ResetBasis(self):
	
		if self.path_data_loaded:
			
			self.basis_id = None
			self.proj_basis = N.diag([1,1]+[0]*(len(self.d_info[0]['mu'].squeeze())-2))

	# --------------------
	def SetBasisID_ReprojectAll(self, id):
	
		if (id is not None) and self.path_data_loaded and id >= 0 and id < len(self.d_info):
			
			if id != self.basis_id:
				self.SetBasisID(id)
				
				self.all_ellipse_params = []
				for node in self.nodes_by_id:
					self.all_ellipse_params.append(self.calculate_node_ellipse(node['id']))

	# --------------------
	def SetBasisID(self, id):
	
		if (id is not None) and self.path_data_loaded and id >= 0 and id < len(self.d_info):
			
			self.basis_id = id
			self.proj_basis = self.d_info[id]['U'][:,:2]

	# --------------------
	def SetBasisID_ReprojectAll(self, id):
	
		if (id is not None) and self.path_data_loaded and id >= 0 and id < len(self.d_info):
			
			if id != self.basis_id:
				self.SetBasisID(id)
				
				self.all_ellipse_params = []
				for node in self.nodes_by_id:
					self.all_ellipse_params.append(self.calculate_node_ellipse(node['id']))

	# --------------------
	def GetMaxID(self):
	
		if self.path_data_loaded:
			return len(self.d_info)-1

	# --------------------
	def GetRawPathCoordList_JSON(self):
		
		if self.path_data_loaded:
			return simplejson.dumps(self.path_info['path'].tolist())
		
	# --------------------
	def GetNetCoordList_JSON(self):
		
		if self.path_data_loaded:
			return simplejson.dumps(self.netpoints[:,:2].tolist())
		
	# --------------------
	def GetNetPathCoordList_JSON(self):
		
		if self.path_data_loaded:
			netpts = self.netpoints[self.path_info['path_index'].squeeze(),:2]
			# adding some randomness to make the "thickness" of the connectors reflect times visited
			netpts = netpts + 0.0005*(N.max(self.netpoints)-N.min(self.netpoints))*N.random.standard_normal(netpts.shape)
			return simplejson.dumps(netpts.tolist())
		
	# --------------------
	def GetGlobalPathCoordList_JSON(self):
		
		if self.path_data_loaded:
			# NOTE: hard-coded 2d...
			g_path = []
			for ii,idx in enumerate(self.path_info['path_index']):
				d_info = self.d_info[idx]
				U = d_info['U'][:,:2]
				x = self.path_info['path'][ii].reshape((1,2))
				x = x.dot(U.T)
				x = x + d_info['mu']
				g_path.append(x.squeeze()[:2].tolist())
		
			return simplejson.dumps(g_path)
		
	# --------------------
	def calculate_node_ellipse(self, node_id):
		"""Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse"""
		
		node = self.d_info[node_id]
		
		# Compute projection of this node's covariance matrix
		A = node['phi'].T
		sigma = N.matrix(N.diag(node['E']))
		center = node['mu']
		
		A = A * N.sqrt(sigma)
		C1 = self.proj_basis.T * A
		C = C1 * C1.T
		print C
		# ALT METHOD for transforming the unit circle according to projected covariance
		# Compute svd in projected space to find rx, ry and rotation for ellipse in D3 vis
		U, S, V = N.linalg.svd(C)

		# Project mean
		xm = N.dot(self.proj_basis.T, center)
		xrm = N.dot(self.proj_basis.T, self.data_center)
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
# --------------------
if __name__ == "__main__":

	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130601'
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
