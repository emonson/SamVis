import simplejson
import os
import numpy as N
import collections as C
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
		
		# Path coordinates gathered by district ID for faster search
		self.coords_by_id = None
		
		# For projection of district ellipses into a certain basis
		self.basis_district_id = None
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
		
		# Gather up path coordinates by district ID for faster lookup later
		self.gather_coords_by_district_id()
		
		# HACK: data_center
		self.data_center = N.zeros(self.d_info[0]['mu'].shape).T
		self.ResetBasis()
		
	# --------------------
	# BASIS

	# --------------------
	def ResetBasis(self):
	
		if self.path_data_loaded:
			
			self.basis_district_id = None
			# TODO: Needs to be generalized to D dimensions...
			# Want projection basis to be D x 2
			tmp_basis = N.array([[1,0,0],[0,1,0]], dtype='f').T
			# Normalize (but not orthogonalize...)
			# self.proj_basis = tmp_basis/N.sqrt((tmp_basis ** 2).sum(axis=0))[N.newaxis,...]
			# Normalize and orthoganalize with QR decomposition
			self.proj_basis, r = N.linalg.qr(tmp_basis)

	# --------------------
	def ResetBasis_ReprojectAll(self):
	
		if self.path_data_loaded:
			self.ResetBasis()
			
			self.all_ellipse_params = []
			for ii in range(len(self.d_info)):
				self.all_ellipse_params.append(self.calculate_node_ellipse(ii))

	# --------------------
	def SetBasisDistrict(self, district_id = None):
	
		if self.basis_district_id == district_id:
			return
		elif (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			self.all_ellipse_params = None
			self.path_ellipse_params = None
			self.basis_district_id = district_id
			n,d = self.path_info['path'].shape
			self.proj_basis = self.d_info[district_id]['U'][:,:d]

	# --------------------
	def ResetBasis_ReprojectPathEllipses(self):
	
		if self.path_data_loaded:
			self.ResetBasis()
			
			self.path_ellipse_params = []
			for ii in set(self.path_info['path_index'].squeeze().tolist()):
				self.path_ellipse_params.append(self.calculate_node_ellipse(ii))

	# --------------------
	# NET POINTS

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
	# PATHS

	# --------------------
	def GetRawPathCoordList_JSON(self):
		
		if self.path_data_loaded:
			return simplejson.dumps(self.path_info['path'].tolist())
		
	# --------------------
	def GetGlobalPathCoordList(self):
		"""Transfer all path coordinates from local district coordinates into the global
		space, and then project onto projection basis plane. This could be used for all
		visualizations of the path, but the disadvantage of this method is that if the
		ambient dimension is very high, points need to be transferred into this high-d
		space before they're projected back down to 2d..."""
		
		# TODO: Need to set projection basis first...
		
		if self.path_data_loaded:
			n,d = self.path_info['path'].shape
			g_path = []
			for ii in range(n):
				x = self.index_to_global_path_coord(ii)
				x = x.dot(self.proj_basis)
				g_path.append(x.squeeze().tolist())
		
			return g_path
		
	# --------------------
	def GetGlobalPathCoordList_JSON(self):
		
		if self.path_data_loaded:
			g_path = self.GetGlobalPathCoordList()
			return simplejson.dumps(g_path)
		
	# --------------------
	def GetGlobalPathCoordPairs_JSON(self):
		
		if self.path_data_loaded:
			g_path = self.GetGlobalPathCoordList()
			g_pairs = []
			for ii in range(len(g_path)-1):
				gg = g_path[ii]
				gg.extend(g_path[ii+1])
				gg.append(ii)
				gg.append(int(self.path_info['path_index'][ii,0]))
				g_pairs.append(gg)
			
			g_pairs = self.pretty_sci_floats(g_pairs)
			return simplejson.dumps(g_pairs)
		
	# --------------------
	def GetDistrictPathCoordPairs_JSON(self, dest_district=None):
		"""Get back district path coordinate pairs [[x0, y0, x1, y1, time_idx, district_id], ...]
		Index is based on starting coordinate index of pair"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			# indexes is the array of "time" indexes which correspond to the coordinates
			# and district path_index values for the path that intersects this district and its
			# neighbors
			district_path_info = self.GetDistrictPathCoordInfo(dest_district)
			path = district_path_info['path']
			time_indexes = district_path_info['time_idx']
			district_ids = district_path_info['district_id']
			g_pairs = []
			for ii in range(len(time_indexes)-1):
				if (time_indexes[ii+1]-time_indexes[ii] > 1):
					continue
				idx = int(time_indexes[ii])		# numpy.int64 not json serializable...
				gg = path[ii]
				gg.extend(path[ii+1])
				gg.append(idx)
				gg.append(int(district_ids[ii]))
				g_pairs.append(gg)
			return simplejson.dumps(g_pairs)
		
	# --------------------
	def GetDistrictPathCoordInfo(self, dest_district=None):
		"""Select out path coordinates that exist within a given district and transfer them
		to the coordinates of the central node. Returns {path:[[x,y],...], time_idx:[i,...], district_id:[i,...]}"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			# Set basis to requested district
			self.SetBasisDistrict(dest_district)
			
			# Searches for which indices in path match district and NN indexes
			idx_matches = N.nonzero( N.in1d( self.path_info['path_index'], self.d_info[dest_district]['index'] ) )
			indexes = idx_matches[0].squeeze().tolist()
			path = []
			district_ids = self.path_info['path_index'][idx_matches].squeeze().tolist()
			
			for idx in indexes:
				x = self.transfer_coord_to_neighbor_district(idx, dest_district).squeeze().tolist()
				xp = self.pretty_sci_floats(x)
				path.append(xp)

			return {'path':path, 'time_idx':indexes, 'district_id':district_ids}
		
	# --------------------
	def GetDistrictPathCoordInfo_JSON(self, dest_district=None):
		"""Select out path coordinates that exist within a given district and transfer them
		to the coordinates of the central node. NOTE: As of now this will connect segments
		that actually go out of the district -- just for testing!!"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			district_path_info = self.GetDistrictPathCoordInfo(dest_district)
			
			return simplejson.dumps(district_path_info)
		
	# --------------------
	def GetDistrictDeepPathCoordInfo(self, dest_district=None, depth=2):
		"""Get paths in neighborhood of a district through NN transfer (not projection
		to global space). Not limited to 1st NN, can set depth.
		Returns {path:[[x,y],...], time_idx:[i,...], district_id:[i,...]}"""
	
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			# Set basis to requested district
			self.SetBasisDistrict(dest_district)
			
			# Get "node tree" representations around root district
			nodes_by_id, nodes_by_depth = self.generate_nn_tree(dest_district, depth)
			
			# Go from deepest up to root, layer by layer, transferring coordinates inward
			# NOTE: None of these will have the district global offset yet
			depths = nodes_by_depth.keys()
			depths.sort(reverse=True)
			for dd in depths:
				for node in nodes_by_depth[dd]:
					parent_district = node['parent_id']
					# If not root node
					if parent_district is not None:
						child_district = node['id']
						coords = node['coords']
						time_idxs = node['time_idxs']
						district_ids = node['district_ids']
						depth_list = node['depths']
						# Transfer coordinate between districts
						if len(time_idxs) > 0:
							new_coords = self.transfer_coord_between_districts(child_district, parent_district, coords)
							# Add coords onto parent
							if nodes_by_id[parent_district]['coords'].size != 0:
								nodes_by_id[parent_district]['coords'] = N.concatenate((nodes_by_id[parent_district]['coords'], new_coords), axis=0)
								nodes_by_id[parent_district]['time_idxs'] = N.concatenate((nodes_by_id[parent_district]['time_idxs'], time_idxs))
								nodes_by_id[parent_district]['district_ids'] = N.concatenate((nodes_by_id[parent_district]['district_ids'], district_ids))
								nodes_by_id[parent_district]['depths'] = N.concatenate((nodes_by_id[parent_district]['depths'], depth_list))
							else:
								nodes_by_id[parent_district]['coords'] = new_coords
								nodes_by_id[parent_district]['time_idxs'] = time_idxs
								nodes_by_id[parent_district]['district_ids'] = district_ids
								nodes_by_id[parent_district]['depths'] = depth_list
								
			# Now that all of the coordinates are transferred to the dest_district,
			# need to add the dest_district (projected) center
			d, = nodes_by_id[dest_district]['coords'][0,:].shape
			center = self.d_info[dest_district]['mu'].T
			# Project mean
			xm = N.dot(self.proj_basis.T, center)
			xrm = N.dot(self.proj_basis.T, self.data_center)
			xm = N.squeeze(N.asarray(xm - xrm))
			# Adding offset
			nodes_by_id[dest_district]['coords'] = nodes_by_id[dest_district]['coords'] + xm[:d]
			
			time_order = N.argsort(nodes_by_id[dest_district]['time_idxs'])
			return_obj = {}
			return_obj['path'] = self.pretty_sci_floats(nodes_by_id[dest_district]['coords'][time_order].tolist())
			return_obj['time_idx'] = nodes_by_id[dest_district]['time_idxs'][time_order].squeeze().tolist()
			return_obj['district_id'] = nodes_by_id[dest_district]['district_ids'][time_order].squeeze().tolist()
			return_obj['depths'] = nodes_by_id[dest_district]['depths'][time_order].squeeze().tolist()
			
			return return_obj
			
	# --------------------
	def GetDistrictDeepPathCoordInfo_JSON(self, dest_district=None, depth=2):
		"""Select out path coordinates that exist within a given district and transfer them
		to the coordinates of the central node. NOTE: As of now this will connect segments
		that actually go out of the district -- just for testing!!"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			district_path_info = self.GetDistrictDeepPathCoordInfo(dest_district, depth)
			
			return simplejson.dumps(district_path_info)
		
	# --------------------
	def GetDistrictDeepPathLocalCoordInfo(self, dest_district=None, depth=2):
		"""Get paths in neighborhood of a district through NN transfer (not projection
		to global space). Not limited to 1st NN, can set depth.
		Returns {path:[[x,y],...], time_idx:[i,...], district_id:[i,...]}"""
	
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			# Get "node tree" representations around root district
			print 'getting ready to make tree'
			nodes_by_id, nodes_by_depth = self.generate_nn_tree(dest_district, depth)
			print 'made tree, starting transfer'
			
			# Go from deepest up to root, layer by layer, transferring coordinates inward
			# NOTE: None of these will have the district global offset yet
			depths = nodes_by_depth.keys()
			depths.sort(reverse=True)
			print 'sorted'
			for dd in depths:
				for node in nodes_by_depth[dd]:
					parent_district = node['parent_id']
					# If not root node
					if parent_district is not None:
						child_district = node['id']
						coords = node['coords']
						time_idxs = node['time_idxs']
						district_ids = node['district_ids']
						depth_list = node['depths']
						# Transfer coordinate between districts
						if len(time_idxs) > 0:
							new_coords = self.transfer_coord_between_districts(child_district, parent_district, coords)
							# Add coords onto parent
							if nodes_by_id[parent_district]['coords'].size != 0:
								nodes_by_id[parent_district]['coords'] = N.concatenate((nodes_by_id[parent_district]['coords'], new_coords), axis=0)
								nodes_by_id[parent_district]['time_idxs'] = N.concatenate((nodes_by_id[parent_district]['time_idxs'], time_idxs))
								nodes_by_id[parent_district]['district_ids'] = N.concatenate((nodes_by_id[parent_district]['district_ids'], district_ids))
								nodes_by_id[parent_district]['depths'] = N.concatenate((nodes_by_id[parent_district]['depths'], depth_list))
							else:
								nodes_by_id[parent_district]['coords'] = new_coords
								nodes_by_id[parent_district]['time_idxs'] = time_idxs
								nodes_by_id[parent_district]['district_ids'] = district_ids
								nodes_by_id[parent_district]['depths'] = depth_list
			
			print 'done with transfer up tree'

			# When we never go into global coordinates for the ellipses, we don't have to 
			# add any offset onto the paths
			
			time_order = N.argsort(nodes_by_id[dest_district]['time_idxs'])
			return_obj = {}
			return_obj['path'] = self.pretty_sci_floats(nodes_by_id[dest_district]['coords'][time_order].tolist())
			return_obj['time_idx'] = nodes_by_id[dest_district]['time_idxs'][time_order].squeeze().tolist()
			return_obj['district_id'] = nodes_by_id[dest_district]['district_ids'][time_order].squeeze().tolist()
			return_obj['depths'] = nodes_by_id[dest_district]['depths'][time_order].squeeze().tolist()
			
			print 'returning obj'
			return return_obj
			
	# --------------------
	def GetDistrictDeepPathLocalCoordInfo_JSON(self, dest_district=None, depth=2):
		"""Select out path coordinates that exist within a given district and transfer them
		to the coordinates of the central node. NOTE: As of now this will connect segments
		that actually go out of the district -- just for testing!!"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			district_path_info = self.GetDistrictDeepPathLocalCoordInfo(dest_district, depth)
			
			return simplejson.dumps(district_path_info)
		
	# --------------------
	# ELLIPSES

	# --------------------
	def GetAllEllipses(self):
		"""Return dict of all ellipses in tree"""
	
		if self.path_data_loaded:
			
			self.ResetBasis_ReprojectAll()
			
			bounds = self.calculate_ellipse_bounds(self.all_ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			return_obj = {'data':self.all_ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetAllEllipses_JSON(self):
		"""Get JSON of all ellipses without reprojecting"""
	
		return simplejson.dumps(self.GetAllEllipses())
		
	# --------------------
	def GetPathEllipses(self):
		"""Return dict of all ellipses in tree"""
	
		if self.path_data_loaded:
			
			# Even though specified NoProjection, if no ellipse params, generate default
			self.ResetBasis_ReprojectPathEllipses()
			
			bounds = self.calculate_ellipse_bounds(self.path_ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			return_obj = {'data':self.path_ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetPathEllipses_JSON(self):
		"""Get JSON of all ellipses without reprojecting"""
	
		return simplejson.dumps(self.GetPathEllipses())
		
	# --------------------
	def GetDistrictEllipses(self, district_id = None):
		"""Return list of ellipses in a district (center plus neighbors). Takes ellipses
		out to global coordinate system (potentially high-d) and uses offset in global system
		rather than centered at zero in local center system."""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			# Set basis to requested district
			self.SetBasisDistrict(district_id)
			
			indexes = self.d_info[district_id]['index'].squeeze().tolist()
			ellipse_params = []
			
			for idx in indexes:
				ellipse_params.append(self.calculate_node_ellipse(idx))
			
			bounds = self.calculate_ellipse_bounds(ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			#DEBUG
			print
			print 'Global ellipses bounds:', bounds
			print
			return_obj = {'data':ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetDistrictEllipses_JSON(self, district_id):
	
		return simplejson.dumps(self.GetDistrictEllipses(district_id))
		
	# --------------------
	def GetDistrictLocalEllipses(self, district_id = None):
		"""Return list of ellipses in a district (center plus neighbors). This routine
		never goes out into the global space, but uses TM to transfer coordinate systems
		of neighbors into center local system (all low-d). Centered at zero on local center
		system."""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			indexes = self.d_info[district_id]['index'].squeeze().tolist()
			ellipse_params = []
			
			for idx in indexes:
				result_list = self.calculate_local_node_ellipse(idx, district_id)
				ellipse_params.append(self.pretty_sci_floats(result_list))
			
			bounds = self.calculate_ellipse_bounds(ellipse_params)
			bounds = self.pretty_sci_floats(bounds)
			#DEBUG
			print
			print 'Local ellipses bounds:', bounds
			print
			return_obj = {'data':ellipse_params, 'bounds':bounds}

			return return_obj
		
	# --------------------
	def GetDistrictLocalEllipses_JSON(self, district_id):
	
		return simplejson.dumps(self.GetDistrictLocalEllipses(district_id))
		
	# --------------------
	# UTILITY CLASSES
	
	# --------------------
	def calculate_node_ellipse(self, node_id):
		"""Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse.
		Returns pretty_sci_floats() version of parameters."""
		
		# TODO: Move pretty_sci_floats() out to routines that use returned params
		
		node = self.d_info[node_id]
		
		# Compute projection of this node's covariance matrix
		A = node['U']
		sigma = N.diag(node['E'].squeeze())
		center = node['mu'].T
		
		A = N.dot(A, N.sqrt(sigma))
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
		# Casting to int() here because json serializer has trouble with numpy ints
		result_list.append(int(node_id))
		
		return result_list
	
	# --------------------
	def calculate_local_node_ellipse(self, orig_id, dest_id):
		"""Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse.
		Returns pretty_sci_floats() version of parameters."""
				
		orig_node = self.d_info[orig_id]
		dest_nnidx = N.nonzero(orig_node['index'].squeeze() == dest_id)[0][0]
		
		dest_node = self.d_info[dest_id]
		orig_nnidx = N.nonzero(dest_node['index'].squeeze() == orig_id)[0][0]

		# NOTE: Taking d from district centers dimensionality. Always reliable...?
		nn,d = orig_node['A'].shape
		
		# Method for transforming the unit circle according to projected covariance
		# Compute svd in projected space to find rx, ry and rotation for ellipse in D3 vis
		
		# Sometimes self-TM not identity (as it should be), so safer to just set explicitly
		if orig_id == dest_id:
			T = N.matrix(N.eye(d))
		else:
			T = N.matrix(orig_node['TM'][:d,:d, dest_nnidx])
		
		I = N.matrix(N.eye(d))
		S2 = N.matrix(N.diag(orig_node['E'][:d].squeeze()))
	
		covXT = T.T * I * S2 * I.T * T
	
		U, S, V = N.linalg.svd(covXT)
		R = N.sqrt(S)
	
		# Calculate angles
		phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
		# t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))
	
		center = dest_node['A'][orig_nnidx, :d]
		
		# How many sigma ellipses cover
		r_mult = 1.0
		
		# Will to rounding to specific precision in receiving routine
		result_list = [center[0], center[1], r_mult*R[0], r_mult*R[1], phi_deg]
		# Casting to int() here because json serializer has trouble with numpy ints
		result_list.append(int(orig_id))
		
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
		
		return self.pretty_sci_floats([[minX, maxX], [minY, maxY]])
	
	# --------------------
	def index_to_global_path_coord(self, index):
		
		n,d = self.path_info['path'].shape
		district_id = self.path_info['path_index'][index]
		d_info = self.d_info[district_id]
		U = d_info['U'][:,:d]
		x = self.path_info['path'][index][N.newaxis,:]	# makes (1,d) instead of (d,)
		x = x.dot(U.T)
		x = x + d_info['mu']
		
		return x

	# --------------------
	def gather_coords_by_district_id(self):
		
		if not self.path_data_loaded:
			raise Exception('DataNotLoaded')

		n,d = self.path_info['path'].shape
		self.coords_by_id = {}
		
		path_district_ids = N.unique(self.path_info['path_index'])
		
		for id in path_district_ids:
			self.coords_by_id[id] = {}
			idx_matches = N.nonzero( N.in1d( self.path_info['path_index'], N.array([id]) ) )
			self.coords_by_id[id]['coords'] = self.path_info['path'][idx_matches]
			self.coords_by_id[id]['time_idxs'] = idx_matches[0]
		
	# --------------------
	def transfer_coord_to_neighbor_district(self, pos_idx, dest_district):
		
		n,d = self.path_info['path'].shape
		# start district of position -- original coordinate system in which it's defined
		idx = self.path_info['path_index'][pos_idx, 0]
		nnidx = N.nonzero(self.d_info[idx]['index'].squeeze() == dest_district)[0][0]
		
		x = self.path_info['path'][pos_idx, :]
		x = x - self.d_info[idx]['lmk_mean'][nnidx, :d]
		# NOTE: For some reason Miles stored all zeros TM for self-transfer...
		if idx != dest_district:
			x = x.dot(self.d_info[idx]['TM'][:d, :d, nnidx])

		oldidx = N.nonzero(self.d_info[dest_district]['index'].squeeze() == idx)[0][0]
		
		x = x + self.d_info[dest_district]['lmk_mean'][oldidx, :d]
		
		# TODO: shouldn't have to recompute this for each point, do it on district level...
		center = self.d_info[dest_district]['mu'].T
		# Project mean
		xm = N.dot(self.proj_basis.T, center)
		xrm = N.dot(self.proj_basis.T, self.data_center)
		xm = N.squeeze(N.asarray(xm - xrm))

		# print idx, x
		
		# return x
		return x + xm[:d]

	# --------------------
	def transfer_coord_between_districts(self, orig_district, dest_district, coords):
		
		# NOTE: Not quite sure how to make this generic... coord comes in as shape (d,)
		# NOTE: This routine doesn't add the district global offset (center)
		
		n,d = coords.shape
		# start district of position -- original coordinate system in which it's defined
		idx = orig_district
		nnidx = N.nonzero(self.d_info[idx]['index'].squeeze() == dest_district)[0][0]
		
		x = coords
		x = x - self.d_info[idx]['lmk_mean'][nnidx, :d]
		# NOTE: For some reason Miles stored all zeros TM for self-transfer...
		if idx != dest_district:
			x = x.dot(self.d_info[idx]['TM'][:d, :d, nnidx])

		oldidx = N.nonzero(self.d_info[dest_district]['index'].squeeze() == idx)[0][0]
		
		x = x + self.d_info[dest_district]['lmk_mean'][oldidx, :d]
		
		# print idx, x
		
		return x

	# --------------------
	def generate_nn_tree(self, root_district_id, depth_limit=2):
		"""Generate dictionaries of (nodes_by_id, nodes_by_depth) from NN information
		on districts, storing 'district_id', 'parent_id', 'child_ids', 'coords', 'time_idxs'
		in each node. Root node considered depth=0, will continue including depth limit value."""
	
		if (root_district_id is not None) and (root_district_id >= 0) and (root_district_id < len(self.d_info)) and self.path_data_loaded:

			# NOTE: Have to go breadth-first with the way I'm figuring out which are children
			#   from the nearest-neighbor indices. If you go depth-first, some of the level 2
			#   children get counted as children of other level 2s rather than as children
			#   of level 1s since you visit some level 2s before the level 1s are done...
			
			# MODE = 'breadth_first'

			# Iterative traversal
			#		Note: for Python deque, 
			#				extendleft / appendleft --> [0, 1, 2] <-- extend / append
			#											 popleft <--						 --> pop

			node_ids= C.deque()
			node_ids.appendleft(root_district_id)
		
			parent_ids = {}
			nodes_by_id = {}
			nodes_by_depth = {}

			while len(node_ids) > 0:
				# Get next node to process from deque for iterative traversal
				# MODE == 'breadth_first':
				curr_id = node_ids.pop()
		
				# Calculate something on the current node
				node = {}
			
				if curr_id == root_district_id:
					depth = 0
					parent_id = None
					# Initialize accounted-for ids with root id since it won't get added as a child
					accounted_node_ids = N.array([root_district_id], dtype='int')
				else:
					parent_id = parent_ids[curr_id]
					depth = nodes_by_id[parent_id]['depth'] + 1
			
				node['id'] = curr_id
				node['parent_id'] = parent_id
				node['depth'] = depth
			
				# Some nearest neighbors will be siblings and parent
				potential_child_ids = self.d_info[curr_id]['index']
				# Take out current node
				non_self_child_ids = N.setdiff1d(potential_child_ids, [curr_id])
				child_ids = N.setdiff1d(potential_child_ids, accounted_node_ids)

				# NOTE: Some nodes won't end up with children at this point
				node['child_ids'] = child_ids
				
				# NOTE: The way it's being done right now some districts will be returned that
				#   don't have coordinates, so record None (for now) if nothing
				if curr_id in self.coords_by_id:
					node['coords'] = self.coords_by_id[curr_id]['coords']
					node['time_idxs'] = self.coords_by_id[curr_id]['time_idxs']
					node['depths'] = N.array([depth]*len(node['time_idxs']))
				else:
					node['coords'] = N.array([])
					node['time_idxs'] = N.array([])
					node['depths'] = N.array([])
				
				# keep track of these for later when coords are transferred between districts
				node['district_ids'] = N.array([curr_id]*len(node['time_idxs']))
			
				# Record parents for later reverse lookup
				for id in child_ids:
					parent_ids[id] = int(curr_id)
			
				# Add current children into array of accounted-for ids
				accounted_node_ids = N.union1d(accounted_node_ids, child_ids)
				nodes_by_id[curr_id] = node
				if depth not in nodes_by_depth:
					nodes_by_depth[depth] = []
				nodes_by_depth[depth].append(node)
	
				# Check if should proceed, add on to deque for ongoing iterative tree traveral
				if depth < depth_limit and len(child_ids) > 0:
					node_ids.extendleft(child_ids.tolist())
			
			return (nodes_by_id, nodes_by_depth)

	# --------------------
	def traverse_tree(self, root_node, child_key='children'):
		"""A general routine for traversing a tree iteratively"""
	
		# MODE = 'breadth_first'
		MODE = 'depth_first'

		# Iterative traversal
		#		Note: for Python deque, 
		#				extendleft / appendleft --> [0, 1, 2] <-- extend / append
		#											 popleft <--						 --> pop

		nodes = C.deque()
		nodes.appendleft(root_node)

		while len(nodes) > 0:
			# Get next node to process from deque for iterative traversal
			if MODE == 'breadth_first':
				current_node = nodes.pop()
			elif MODE == 'depth_first':
				current_node = nodes.popleft()
			else:
				break
		
			# Calculate something on the current node
			if child_key in current_node:
				if len(current_node[child_key]) == 0:
					del current_node[child_key]
				else:
					current_node[child_key] = list(current_node[child_key])
	
			# Check if should proceed, add on to deque for ongoing iterative tree traveral
			if child_key in current_node:
				nodes.extendleft(current_node[child_key])

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

	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130813'
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
