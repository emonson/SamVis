import simplejson
import os
import numpy as N
import collections as C
import path_json_read as PR

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
		

	# --------------------
	# QUERY
		
	# --------------------
	def GetDistrictFromPathTime_JSON(self, time=None):
		"""Get district ID for path at a given time. NOTE: time is an index, not real time
		for now. Returns {district_id:ID} JSON"""

		if time is not None:
			return simplejson.dumps({'district_id':int(self.path_info['path_index'][time,0])})

	# --------------------
	# PATHS
		
	# --------------------
	def GetDistrictDeepPathLocalRotatedCoordInfo(self, dest_district=None, prev_district=None, depth=1, R_old=None):
		"""Get paths in neighborhood of a district through NN transfer (not projection
		to global space). Not limited to 1st NN, can set depth.
		Returns {path:[[x,y],...], time_idx:[i,...], district_id:[i,...]}"""
	
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

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
			
			# When we never go into global coordinates for the ellipses, we don't have to 
			# add any offset onto the paths
			return_obj = {}
			
			# Apply an orthogonal transformation to eliminate rotation of coordinate systems betweeen districts
			if (prev_district is not None) and (prev_district > 0) and (prev_district < len(self.d_info)):
				if R_old is not None:
					
					# TODO: should put nice out if Rold doesn't form well...
					# NOTE: calling cherrypy routine parses R_old out from string to 2x2 list of lists
					R_prev = N.matrix(R_old)
					R_new = self.calculate_local_rotation_matrix(prev_district, dest_district, R_prev)
					
					# transform, taking only 1st 2d of coordinates
					nodes_by_id[dest_district]['coords'] = nodes_by_id[dest_district]['coords'][:,:2] * R_new
					
					# return R_new as string because it will just be passed back unchanged on next transition
					# with square brackets stripped off
					R_new_str = str(N.asarray(R_new).ravel().tolist())[1:-1]
					return_obj['R_old'] = R_new_str
			
			time_order = N.argsort(nodes_by_id[dest_district]['time_idxs'])
			return_obj['path'] = self.pretty_sci_floats(nodes_by_id[dest_district]['coords'][time_order].tolist())
			return_obj['time_idx'] = nodes_by_id[dest_district]['time_idxs'][time_order].squeeze().tolist()
			return_obj['district_id'] = nodes_by_id[dest_district]['district_ids'][time_order].squeeze().tolist()
			return_obj['depths'] = nodes_by_id[dest_district]['depths'][time_order].squeeze().tolist()
			return_obj['t_max_idx'] = self.path_info['path'].shape[0] - 1
			
			# print return_obj['path']
			
			return return_obj
			
	# --------------------
	def GetDistrictDeepPathLocalRotatedCoordInfo_JSON(self, dest_district=None, prev_district=None, depth=1, R_old=None):
		"""Select out path coordinates that exist within a given district and transfer them
		to the coordinates of the central node. NOTE: As of now this will connect segments
		that actually go out of the district -- just for testing!!"""
		
		if (dest_district is not None) and (dest_district >= 0) and (dest_district < len(self.d_info)) and self.path_data_loaded:

			# Apply an orthogonal transformation to eliminate rotation of coordinate systems betweeen districts
			if (prev_district is not None) and (prev_district > 0) and (prev_district < len(self.d_info)) and (R_old is not None):
					
				# NOTE:  cherrypy routine parses R_old out from string to 2x2 list of lists, send that directly
				district_path_info = self.GetDistrictDeepPathLocalRotatedCoordInfo(dest_district, prev_district, depth, R_old)
			
				return simplejson.dumps(district_path_info)
		
	# --------------------
	# ELLIPSES
		
	# --------------------
	def GetDistrictLocalRotatedEllipses(self, district_id = None, previous_id = None, R_old = None):
		"""Return list of ellipses in a district (center plus neighbors). This routine
		never goes out into the global space, but uses TM to transfer coordinate systems
		of neighbors into center local system (all low-d). Centered at zero on local center
		system."""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			# Apply an orthogonal transformation to eliminate rotation of coordinate systems betweeen districts
			if (previous_id is not None) and (previous_id > 0) and (previous_id < len(self.d_info)):
				if R_old is not None:
					
					# TODO: should put nice out if Rold doesn't form well...
					# NOTE: calling cherrypy routine parses R_old out from string to 2x2 list of lists
					R_prev = N.matrix(R_old)
					R_new = self.calculate_local_rotation_matrix(previous_id, district_id, R_prev)
					phi_deg = 360 * ( N.arctan(-R_new[0,1]/R_new[0,0] )/(2*N.pi))
					
					# return R_new as string because it will just be passed back unchanged on next transition
					# with square brackets stripped off
					R_new_str = str(N.asarray(R_new).ravel().tolist())[1:-1]

					indexes = self.d_info[district_id]['index'].squeeze().tolist()
					ellipse_params = []
			
					for idx in indexes:
						result_list = self.calculate_local_node_ellipse(idx, district_id)
						# Transform to eliminate rotations
						# TODO: need to switch to doing the transforms for all ellipses at once...
						center = N.matrix(result_list[:2])
						center = center * R_new
						result_list[0] = center[0,0]
						result_list[1] = center[0,1]
						# print idx, result_list[4], phi_deg
						result_list[4] = result_list[4] + phi_deg
						# Avoid "spinning ellipses" caused by addition of phi_deg taking it out of range
						if result_list[4] < -90:
							result_list[4] = result_list[4] + 180
						if result_list[4] > 90:
							result_list[4] = result_list[4] - 180
						ellipse_params.append(self.pretty_sci_floats(result_list))
			
					bounds = self.calculate_ellipse_bounds(ellipse_params)
					bounds = self.pretty_sci_floats(bounds)
					return_obj = {'data':ellipse_params, 'bounds':bounds, 'drift':[], 'R_old':R_new_str}

			
					return return_obj
		
	# --------------------
	def GetDistrictLocalRotatedEllipses_JSON(self, district_id, previous_id, R_old):
	
		return simplejson.dumps(self.GetDistrictLocalRotatedEllipses(district_id, previous_id, R_old))
		
	# --------------------
	def GetDistrictDiffusionRotatedEllipses(self, district_id = None, previous_id = None, R_old = None):
		"""Return list of ellipses in a district (center plus neighbors). This routine
		never goes out into the global space, but uses TM to transfer coordinate systems
		of neighbors into center local system (all low-d). Centered at zero on local center
		system."""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			# Apply an orthogonal transformation to eliminate rotation of coordinate systems betweeen districts
			if (previous_id is not None) and (previous_id > 0) and (previous_id < len(self.d_info)):
				if R_old is not None:
					
					# TODO: should put nice out if Rold doesn't form well...
					# NOTE: calling cherrypy routine parses R_old out from string to 2x2 list of lists
					R_prev = N.matrix(R_old)
					R_new = self.calculate_local_rotation_matrix(previous_id, district_id, R_prev)
					phi_deg = 360 * ( N.arctan(-R_new[0,1]/R_new[0,0] )/(2*N.pi))
					
					# return R_new as string because it will just be passed back unchanged on next transition
					# with square brackets stripped off
					R_new_str = str(N.asarray(R_new).ravel().tolist())[1:-1]

					indexes = self.d_info[district_id]['index'].squeeze().tolist()
					ellipse_params = []
					drift_params = []
			
					for idx in indexes:
						result_list = self.calculate_local_diffusion_ellipse(idx, district_id)
						# Transform to eliminate rotations
						# TODO: need to switch to doing the transforms for all ellipses at once...
						center = N.matrix(result_list[:2])
						center = center * R_new
						result_list[0] = center[0,0]
						result_list[1] = center[0,1]
						# print idx, result_list[4], phi_deg
						result_list[4] = result_list[4] + phi_deg
						# Avoid "spinning ellipses" caused by addition of phi_deg taking it out of range
						if result_list[4] < -90:
							result_list[4] = result_list[4] + 180
						if result_list[4] > 90:
							result_list[4] = result_list[4] - 180
						ellipse_params.append(self.pretty_sci_floats(result_list))
						drift_list = self.calculate_local_drift_vector(idx, district_id)
						ends = N.matrix(drift_list[:4]).reshape((2,2))
						ends = ends * R_new
						drift_list[:4] = N.asarray(ends).ravel().tolist()
						drift_params.append(self.pretty_sci_floats(drift_list))
			
					bounds = self.calculate_ellipse_bounds(ellipse_params)
					bounds = self.pretty_sci_floats(bounds)
					return_obj = {'data':ellipse_params, 'bounds':bounds, 'drift':drift_params, 'R_old':R_new_str}
			
					return return_obj
		
	# --------------------
	def GetDistrictDiffusionRotatedEllipses_JSON(self, district_id = None, previous_id = None, R_old = None):
	
		return simplejson.dumps(self.GetDistrictDiffusionRotatedEllipses(district_id, previous_id, R_old))
		
	# --------------------
	# UTILITY CLASSES
	
	# --------------------
	def calculate_local_rotation_matrix(self, orig_id, dest_id, Rold):
		"""Calculate new orthogonal matrix to transform all coordinates to eliminate rotation."""
		
		# old center node is where we want to get the old->new TransferMatrix
		orig_node = self.d_info[orig_id]
		dest_idx_ar = N.nonzero(orig_node['index'].squeeze() == dest_id)[0]
		# NOTE: for now just using old rotation matrix if not a nearest neighbor...
		if len(dest_idx_ar) == 0:
			return Rold
		else:
			dest_nnidx = dest_idx_ar[0]
				
		# NOTE: Taking d from district centers dimensionality. Always reliable...?
		nn,d = orig_node['A'].shape
		
		# Sometimes self-TM not identity (as it should be), so safer to just set explicitly
		if orig_id == dest_id:
			T = N.matrix(N.eye(d))
		else:
			T = N.matrix(orig_node['TM'][:d, :d, dest_nnidx])

		# Calculate the new matrix to transform the translated points
		# NOTE: numpy SVD returned V is what in Matlab you'd call V.T
		#   so, reconstructing T = U * N.matrix(N.diag(S)) * V (rather than V.T as typical)
		U, S, V = N.linalg.svd(T)
		u = U[:2,:]
		v = V[:,:2]
		tmp = v.T * u.T
		Rnew1 = tmp * Rold
		
		# Since we only took the first 2-d of U and V, have to make sure Rnew is really
		# orthogonal or else we'll squish some dimensions
		U2, S2, V2 = N.linalg.svd(Rnew1)
		Rnew = U2 * V2
		
		return Rnew
	
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
		S2 = N.matrix(N.diag(N.square(orig_node['E'][:d].squeeze())))
	
		covXT = T.T * I * S2 * I.T * T
	
		U, S, V = N.linalg.svd(covXT)
		R = N.sqrt(S)
	
		# Calculate angles
		phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
		# t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))
		
		center = dest_node['A'][orig_nnidx, :d]
		
		# How many sigma ellipses cover
		r_mult = 1.0
		
		# Here taking only first 2d of centers
		# Will to rounding to specific precision in receiving routine
		result_list = [center[0], center[1], r_mult*R[0], r_mult*R[1], phi_deg]
		# Casting to int() here because json serializer has trouble with numpy ints
		result_list.append(int(orig_id))
		
		return result_list
	
	# --------------------
	def calculate_local_diffusion_ellipse(self, orig_id, dest_id):
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
		
		# Two types of data right now
		if 'sig' in orig_node:
			sig = N.matrix(orig_node['sig'])
		else:
			sig = N.matrix(orig_node['diff'])
			
		# TODO: Should probably sanity check size of sig...

		covXT = T.T * sig * sig.T * T

		U, S, V = N.linalg.svd(covXT)
		R = N.sqrt(S)

		# Calculate angles
		phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
		# t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))

		center = dest_node['A'][orig_nnidx, :d]

		# Scale diffusion ellipses by simulation radius value
		# Sometimes 'r' is a vector and sometimes a single scalar...
		if orig_node['r'].shape == (1,1):
			r_mult = N.sqrt(dest_node['t'][0, 0])
		else:
			r_mult = N.sqrt(dest_node['t'][orig_nnidx, 0])

		# Will to rounding to specific precision in receiving routine
		result_list = [center[0], center[1], r_mult*R[0], r_mult*R[1], phi_deg]
		# Casting to int() here because json serializer has trouble with numpy ints
		result_list.append(int(orig_id))

		return result_list

	# --------------------
	def calculate_local_drift_vector(self, orig_id, dest_id):
		"""Transfers the drift vector from its own district to a NN destination district
		using transfer matrix TM directly. [X1 Y1 X2 Y2 i]"""

		orig_node = self.d_info[orig_id]
		dest_nnidx = N.nonzero(orig_node['index'].squeeze() == dest_id)[0][0]

		dest_node = self.d_info[dest_id]
		orig_nnidx = N.nonzero(dest_node['index'].squeeze() == orig_id)[0][0]

		if 'drift' in orig_node:
			drift = orig_node['drift']
			_,d = drift.shape

			# Sometimes self-TM not identity (as it should be), so safer to just set explicitly
			if orig_id == dest_id:
				T = N.matrix(N.eye(d))
			else:
				T = N.matrix(orig_node['TM'][:d,:d, dest_nnidx])
		
			drift = drift*T
			# Sometimes 'r' is a vector and sometimes a single scalar...
			if orig_node['r'].shape == (1,1):
				r_mult = 0.2*N.sqrt(dest_node['t'][0, 0])
			else:
				r_mult = 0.2*N.sqrt(dest_node['t'][orig_nnidx, 0])
			drift_scaled = N.asarray(r_mult*drift).squeeze()
				
			center = dest_node['A'][orig_nnidx, :d]
			
			# Will to rounding to specific precision in receiving routine
			result_list = [center[0], center[1], center[0]+drift_scaled[0], center[1]+drift_scaled[1]]
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
	def gather_coords_by_district_id(self):
		
		if not self.path_data_loaded:
			raise Exception('DataNotLoaded')

		n,d = self.path_info['path'].shape
		self.coords_by_id = {}
		
		path_district_ids = N.unique(self.path_info['path_index'])
		
		for id in path_district_ids:
			self.coords_by_id[id] = {}
			idx_matches = N.nonzero( N.in1d( self.path_info['path_index'].ravel(), N.array([id]) ) )
			self.coords_by_id[id]['coords'] = self.path_info['path'][idx_matches]
			self.coords_by_id[id]['time_idxs'] = idx_matches[0]

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
	# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
	def pretty_sci_floats(self, obj):
	
		if isinstance(obj, float):
			return PrettyPrecision3SciFloat(obj)
		elif isinstance(obj, dict):
			return dict((k, self.pretty_sci_floats(v)) for k, v in obj.items())
		elif isinstance(obj, (list, tuple)):
			return map(self.pretty_sci_floats, obj)							
		return obj

# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
class PrettyPrecision2SciFloat(float):
	def __repr__(self):
		return '%.2g' % self

class PrettyPrecision3SciFloat(float):
	def __repr__(self):
		return '%.3g' % self

# --------------------
# --------------------
if __name__ == "__main__":

	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130601'
	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130813'
	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130913_ex3d'
	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130926_imgex'
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
