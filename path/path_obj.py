import simplejson
import os
import numpy as N
import path_json_read as PR

# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
class PrettyPrecision2SciFloat(float):
	def __repr__(self):
		return '%.2g' % self

class PrettyPrecision3SciFloat(float):
	def __repr__(self):
		return '%.3g' % self

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
		self.path_ellipse_params = None

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
		self.data_center = N.zeros(self.d_info[0]['mu'].shape).T
		self.ResetBasis()
		
	# --------------------
	def ResetBasis(self):
	
		if self.path_data_loaded:
			
			self.basis_id = None
			# TODO: Needs to be generalized to D dimensions...
			# Want projection basis to be D x 2
			self.proj_basis = N.array([[1,0,0],[0,1,0]]).T 

	# --------------------
	def ResetBasis_ReprojectAll(self):
	
		if self.path_data_loaded:
			self.ResetBasis()
			
			self.all_ellipse_params = []
			for ii in range(len(self.d_info)):
				self.all_ellipse_params.append(self.calculate_node_ellipse(ii))

	# --------------------
	def ResetBasis_ReprojectPathEllipses(self):
	
		if self.path_data_loaded:
			self.ResetBasis()
			
			self.path_ellipse_params = []
			for ii in set(self.path_info['path_index'].squeeze().tolist()):
				self.path_ellipse_params.append(self.calculate_node_ellipse(ii))

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
			n,d = self.path_info['path'].shape
			g_path = []
			for ii,idx in enumerate(self.path_info['path_index']):
				d_info = self.d_info[idx]
				U = d_info['U'][:,:d]
				x = self.path_info['path'][ii][N.newaxis,:]	# makes (1,d) instead of (d,)
				x = x.dot(U.T)
				x = x + d_info['mu']
				x = x.dot(self.proj_basis)
				g_path.append(x.squeeze().tolist())
		
			return simplejson.dumps(g_path)
		
	# --------------------
	def GetAllEllipses_NoProjection(self):
		"""Return dict of all ellipses in tree"""
	
		if self.path_data_loaded:
			
			# Even though specified NoProjection, if no ellipse params, generate default
			if self.all_ellipse_params is None:
				self.ResetBasis_ReprojectAll()
			
			bounds = self.calculate_ellipse_bounds(self.all_ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			return_obj = {'data':self.all_ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetPathEllipses_NoProjection(self):
		"""Return dict of all ellipses in tree"""
	
		if self.path_data_loaded:
			
			# Even though specified NoProjection, if no ellipse params, generate default
			self.ResetBasis_ReprojectPathEllipses()
			
			bounds = self.calculate_ellipse_bounds(self.path_ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			return_obj = {'data':self.path_ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetAllEllipses_NoProjection_JSON(self):
		"""Get JSON of all ellipses without reprojecting"""
	
		return simplejson.dumps(self.GetAllEllipses_NoProjection())
		
	# --------------------
	def GetPathEllipses_NoProjection_JSON(self):
		"""Get JSON of all ellipses without reprojecting"""
	
		return simplejson.dumps(self.GetPathEllipses_NoProjection())
		
	# --------------------
	# UTILITY CLASSES
	
	# --------------------
	def calculate_node_ellipse(self, node_id):
		"""Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse"""
		
		node = self.d_info[node_id]
		
		# Compute projection of this node's covariance matrix
		A = node['U'].T
		sigma = N.diag(node['E'].squeeze())
		center = node['mu'].T
		
		A = A.dot(N.sqrt(sigma))
		C1 = N.dot(self.proj_basis.T, A)
		C = N.dot(C1, C1.T)

		# ALT METHOD for transforming the unit circle according to projected covariance
		# Compute svd in projected space to find rx, ry and rotation for ellipse in D3 vis
		U, S, V = N.linalg.svd(C)
		S2 = N.sqrt(S)

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
		s_mult = 1.0
		result_list = [xm[0], xm[1], s_mult*S2[0], s_mult*S2[1], phi_deg]
		result_list = self.pretty_sci_floats(result_list)
		result_list.append(node_id)
		
		return result_list
	
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
		
		return self.pretty_sci_floats([[minX, maxX], [minY, maxY]])

	# --------------------
	# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
	def pretty_sci_floats(self, obj):
	
		if isinstance(obj, float):
			return PrettyPrecision3SciFloat(obj)
		elif isinstance(obj, dict):
			return dict((k, self.pretty_sci_floats(v)) for k, v in obj.items())
		elif isinstance(obj, (list, tuple)):
			return map(self.pretty_sci_floats, obj)             
		return obj

# --------------------
# --------------------
if __name__ == "__main__":

	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130601'
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
