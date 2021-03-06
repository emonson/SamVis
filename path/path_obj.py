import json
import os
import numpy as N
import collections as C
import path_json_read as PR
from scipy.sparse import coo_matrix 

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
		
		# Trying out caching time from district to all others
		self.time_from_region = {}
		
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

		if dirname and isinstance(dirname, basestring):
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
		
		# Fixup path_index and time data structures so they're 1D rather than 2D
		self.path_info['path_index'] = self.path_info['path_index'].ravel()
		self.path_info['t'] = self.path_info['t'].ravel()
		
		self.path_data_loaded = True
		
		# Gather up path coordinates by district ID for faster lookup later
		self.gather_coords_by_district_id()
		

	# --------------------
	# QUERY
	
	# TODO: All path networks return all the points whether they were visited or not,
	#   which makes the DOM bigger (a bunch of zero radius nodes), but makes the code on
	#   the JS end cleaner because we don't have to use JS to wire up the network, we can
	#   use the built-in d3 methods instead (which rely on indices of nodes matching up with
	#   source/target designations), and then all the data binding works out automatically, too.
	#   What would be better is to always be filtering both networks and scalars for net nodes
	#   on this Python end by the districts that were actually visited before they're returned
	#   to d3. This would mean reducing the edge mtx before calculating node ids and edge
	#   source/target ids, and filtering any outgoing scalars. This would reduce the DOM,
	#   the amount of data being sent over HTTP, etc.
	
	# --------------------
	def GetDistrictFromPathTime_JSON(self, time=None):
		"""Get district ID for path at a given time. NOTE: time is an index, not real time
		for now. Returns {district_id:ID} JSON"""

		if time is not None:
			return json.dumps({'district_id':int(self.path_info['path_index'][time])})

	# --------------------
	def GetTimesFromDistrict_JSON(self, district_id=None):
		"""Get district ID for path at a given time. NOTE: time is an index, not real time
		for now. Returns {district_id:ID} JSON"""

		if district_id is not None:
			# At least for now going to use -1 as "not visited" average time
			avg_times = N.zeros_like(self.d_info) - 1
			# DEBUG
			# time_lists = ['']*len(self.d_info)
			
			# First test whether district is ever visited
			if district_id not in self.path_info['path_index']:
				return json.dumps({'avg_time_to_district':avg_times.tolist()})

			# This increments time after leaving the chosen district and until it returns
			if district_id in self.time_from_region:
				tfr = self.time_from_region[district_id]
			else:
				tfr = self.calculate_time_from_region(district_id)
				self.time_from_region[district_id] = tfr
							
			# What we really want to calculate here, though, is average 1st passage time
			# to any other district. So, we need to keep track of whether the path has
			# made it to a district or not, and if not, then put the time into a list,
			# then start over again each time we get back to the original district.
			# Note: the tfr (times from region) array will be filled with zeros before
			# the first encounter with the origin district.
			# TODO: Really need to filter this somehow to get rid of huge passage times
			#   which result from going far away and coming back to a district. For now
			#   solving that by taking median rather than average, but not a great solution...
			visited = {}
			times = C.defaultdict(list)
			for t,d in zip(tfr,self.path_info['path_index']):
				if d == district_id:
					visited.clear()
					continue
				if (d not in visited) and (t > 0):
					visited[d] = True
					times[d].append(t)

			for d,vals in times.iteritems():
				# MEDIAN -- to reduce the effect of outliers
				avg_time = N.median(vals)
				# MEAN
				# avg_time = N.array(vals).mean()
				avg_times[d] = avg_time
				# DEBUG passing along whole time lists
				# avg_time_str = "%.3g" % avg_time
				# time_lists[d] = str(self.pretty_sci_floats(vals)) + " median( " + avg_time_str + " )"
			avg_times_list = self.pretty_sci_floats(avg_times.tolist())
			t_max_idx = self.path_info['path'].shape[0] - 1
			return json.dumps({'avg_time_to_district':avg_times_list, 't_max_idx':t_max_idx})
			# DEBUG
			# return json.dumps({'avg_time_to_district':avg_times_list, 'time_lists':time_lists, 't_max_idx':t_max_idx})

	# --------------------
	def GetDistrictCenterData_JSON(self, district_id=None):
		"""Return data associated with the center of each district. For now it is an
		image, but it could also be molecular structure data, etc. JSON"""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			if 'center_data' in self.netpoints:
				
				datatype = self.netpoints['center_data']['datatype']
				datashape = self.netpoints['center_data']['data_info']
				
				if datatype == 'image':
					
					data = self.netpoints['center_data']['data'][district_id,:].todense().reshape(datashape, order='F').tolist()
				
				elif datatype == 'function':

					data = self.netpoints['center_data']['data'][district_id,:].reshape(datashape, order='F').tolist()

				# N.asscalar() converts from numpy to native python types so can be json serialized
				datarange = (N.asscalar(N.min(data)), N.asscalar(N.max(data)))
			
				output = {'datatype':datatype, 'data':data, 'data_range':datarange, 'data_dims':datashape.tolist()}
				return json.dumps(output)
									

	# --------------------
	def GetNetPoints_JSON(self):
		"""Get the 2D coordinates in some universal coordinate system for an overview.
		Right now it's just the 1st two dimensions of the netpoints data."""

		netpoints = self.pretty_sci_floats(self.netpoints['points'][:,:2].tolist())
		return json.dumps({'netpoints':netpoints})

	# --------------------
	def GetDataInfo_JSON(self):
		"""Get the ellipse center data type and shape."""

		datatype = self.netpoints['center_data']['datatype']
		data_info = self.netpoints['center_data']['data_info'].tolist()
		data = self.netpoints['center_data']['data']
		bounds = (N.asscalar(data.min()), N.asscalar(data.max()))
		
		return json.dumps({'datatype':datatype, 'shape':data_info, 'alldata_bounds':bounds})

	# --------------------
	def GetTransitionGraph_JSON(self):
		"""Get the graph/network corresponding to all path transitions between districts
		in a format that's easy for D3 to parse."""

		n_nodes = len(self.d_info)
		edge_start = self.path_info['path_index'][:-1]
		edge_end = self.path_info['path_index'][1:]
		edge_mtx = coo_matrix((N.ones_like(edge_start),(edge_start,edge_end)), shape=(n_nodes,n_nodes)).tocsr()
		# sum of csr almost 2x faster along rows. Changing from N.matrix to N.array and ravel()ing
		node_time = edge_mtx.sum(axis=1).A.ravel()	
		node_time_max = int(N.max(node_time))
		v_max = int(edge_mtx.max())
		edge_coo = edge_mtx.tocoo()

		graph_nodes = [{'i':int(i), 't':int(t)} for i,t in enumerate(node_time)]
		# vt is the value of the edge coming from the target back towards the source
		# which we need for some edge rendering schemes
		graph_edges = [{'source':int(r), 'target':int(c), 'v':int(v), 'vt':int(edge_mtx[c,r]), 'i':int(i)} for i,(r,c,v) in enumerate(zip(edge_coo.row, edge_coo.col, edge_coo.data)) if r != c]
		t_max_idx = self.path_info['path'].shape[0] - 1
		
		# Redundant max time info that's also sent with path, but using it here for network
		# transition time scalars
		return json.dumps({'nodes':graph_nodes, 'edges':graph_edges, 't_max_idx':t_max_idx, 'node_time_max':node_time_max, 'vmax':v_max})

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
			if (prev_district is not None) and (prev_district >= 0) and (prev_district < len(self.d_info)):
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
			if (prev_district is not None) and (prev_district >= 0) and (prev_district < len(self.d_info)) and (R_old is not None):
					
				# NOTE:  cherrypy routine parses R_old out from string to 2x2 list of lists, send that directly
				district_path_info = self.GetDistrictDeepPathLocalRotatedCoordInfo(dest_district, prev_district, depth, R_old)
			
				return json.dumps(district_path_info)
		
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
			if (previous_id is not None) and (previous_id >= 0) and (previous_id < len(self.d_info)):
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
					return_obj = {'data':ellipse_params, 'bounds':bounds, 'n_districts':len(self.d_info), 'drift':[], 'R_old':R_new_str}

			
					return return_obj
		
	# --------------------
	def GetDistrictLocalRotatedEllipses_JSON(self, district_id, previous_id, R_old):
	
		return json.dumps(self.GetDistrictLocalRotatedEllipses(district_id, previous_id, R_old))
		
	# --------------------
	def GetDistrictDiffusionRotatedEllipses(self, district_id = None, previous_id = None, R_old = None):
		"""Return list of ellipses in a district (center plus neighbors). This routine
		never goes out into the global space, but uses TM to transfer coordinate systems
		of neighbors into center local system (all low-d). Centered at zero on local center
		system."""

		if (district_id is not None) and (district_id >= 0) and (district_id < len(self.d_info)) and self.path_data_loaded:
			
			# Apply an orthogonal transformation to eliminate rotation of coordinate systems betweeen districts
			if (previous_id is not None) and (previous_id >= 0) and (previous_id < len(self.d_info)):
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
					return_obj = {'data':ellipse_params, 'bounds':bounds, 'n_districts':len(self.d_info), 'drift':drift_params, 'R_old':R_new_str}
			
					return return_obj
		
	# --------------------
	def GetDistrictDiffusionRotatedEllipses_JSON(self, district_id = None, previous_id = None, R_old = None):
	
		return json.dumps(self.GetDistrictDiffusionRotatedEllipses(district_id, previous_id, R_old))
		
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
		elif 'diff' in orig_node:
			sig = N.matrix(orig_node['diff'])
		else:
			# TODO: handle this exception someplace...
			raise NameError('No diffusion variable defined in nodes')
			
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
			# TODO: Magic numbers: 0.2 scaling!!
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
			
		# else if drift not part of original data
		else:
			
			# TODO: Handle this exception or figure out how else to deal with missing drift...
			raise NameError('No drift data')

	# --------------------
	def calculate_ellipse_bounds(self, e_params):
		"""Rough calculation of ellipse bounds by centers +/- max radius for each"""
		
		if len(e_params) > 0:
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
		
		# TODO: not sure this is the best default value, or if exception should be raised!
		else:
			return [[0.0, 0.0], [0.0, 0.0]]
	
	# --------------------
	def calculate_regions_hit_within_time_window(self, tfr, idx_from, time_thresh, idx_to):
		'''Returns mask for path of indices hit from a given idx that hit idx2 withtin 
		time threshold t_thresh'''

		# NOTE: Routine relies on path_index being 1d
		# tfr = calculate_time_from_region(idx_from, 'from')

		# Make a binary mask for parts of the path coming from idx and within
		# the time window
		within_time_window = N.logical_and(tfr < time_thresh, tfr > 0)

		# Create a copy of this mask that contains numbers starting with 1
		# for each continuous section (add a 0 on to the beginning so diff'd array is 
		# same length as original) Changing to int type so cumsum will work in next op
		wtw = N.concatenate((N.array([0],dtype='i'), within_time_window.astype('i')))
		
		# Apply time mask (default for numpy arrays is element-wise multiplication)
		# NOTE: this algorithm using cumsum will start segment numbering at 1...!!
		numbered_segments = N.cumsum( N.diff(wtw)==1 )*within_time_window

		# Now find any segments that contain the target index and get rid of
		# repeats
		segments_hit = N.unique(numbered_segments[N.logical_and(within_time_window, self.path_info['path_index']==idx_to)])

		# Expand to whole path segment that have hits in them (return logical array)
		segments_hit_indices = N.in1d(numbered_segments, segments_hit)

		return segments_hit_indices

	# --------------------
	def calculate_time_from_region(self, dist_idx, direction='from'):
		'''Fills an array the same length as p_idx (path_index) with times
		from a given district index (time in indices, not real time). This can
		then be filtered and by time and used for looking at paths that go
		between districts within a certain window, or gathered by district to
		see the stats of time to other districts. Note that the beginning of
		the array will be filled with zeros before the 1st encounter with
		the source (if 'from', target if 'to') district.'''

		# NOTE: Relies on path_index already being 1d (after ravel())

		t_from_reg = N.zeros_like(self.path_info['path_index'])
		count = 0
		past_init = False

		if direction == 'from':
			idxs = N.arange(len(self.path_info['path_index']))
		elif direction == 'to':
			idxs = N.arange(len(self.path_info['path_index']))[::-1]
		else:
			return

		for ii in idxs:
			if self.path_info['path_index'][ii] == dist_idx:
				# relying here on t_from_reg being initialized with zeros so can skip entry
				past_init = True
				count = 0
			else:
				if past_init:
					count = count + 1
					t_from_reg[ii] = count

		return t_from_reg

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
	
	# data_dir = 'data/json_20130813'
	# data_dir = 'data/json_20130913_ex3d'
	# data_dir = 'data/json_20130927_img_d02'
	data_dir = 'data/json_20140225_function'
	
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
