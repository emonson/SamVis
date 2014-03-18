# Saved from Matlab with JSONlab
# NOTE: JSONlab writes out its 1D arrays in Matlab's column-major ordering, like FORTRAN
#   which necessitates an order='F' on reshape for numpy
# NOTE: Matlab arrays have 1-based indices, and Python has 0-based!!

# load('d_info.mat')
# savejson('',d_info,'ArrayToStruct',1,'ArrayIndent',0,'FileName','d_info.json','ForceRootName',0);
# clear all
# load('netpoints.mat')
# savejson('',netpoints,'ArrayToStruct',1,'ArrayIndent',0,'FileName','netpoints.json','ForceRootName',0);
# clear all
# load('traj2.mat')
# savejson('',sim_opts,'ArrayToStruct',1,'ArrayIndent',0,'FileName','sim_opts.json','ForceRootName',0);
# trajectory = struct()
# trajectory.path = path
# trajectory.path_index = path_index
# trajectory.t = t
# trajectory.v_norm = v_norm
# savejson('',trajectory,'ArrayToStruct',1,'ArrayIndent',0,'FileName','trajectory.json','ForceRootName',0);


import json
import json
import os
import numpy as N
from scipy.sparse import coo_matrix 

def fill_dict_with_arrays(obj):
	# When ArrayToStruct is set, all arrays are saved in 1D format along with size
	c = {}
	for k,v in obj.items():
		item = parse_data_item(k,v)
		if item is not None:
			c[k] = item
	return c

def parse_data_item(k,v):
	if isinstance(v, dict):
		# NOTE: skipping sparse (and big!) lmks array for now...
		if isinstance(k, basestring) and k.startswith('lmks'):
			return
		if ("_ArrayIsSparse_" in v) and (v['_ArrayIsSparse_'] == 1):
			# Data stored as a list of triplet lists, [row, column, value]
			rcv = N.array(v['_ArrayData_'])
			# NOTE: Need to subtract 1 in rows and column indices since Matlab 1-based indices...
			c = coo_matrix((rcv[:,2],(rcv[:,0]-1,rcv[:,1]-1)), shape=tuple(v['_ArraySize_'])).tocsr()
		# NOTE: bad name-based test!!
		elif isinstance(k, basestring) and k.endswith('index'):
			# changing 1-based indices to 0-based
			c = N.array(v['_ArrayData_']).reshape(v['_ArraySize_'], order='F') - 1
		else:
			c = N.array(v['_ArrayData_']).reshape(v['_ArraySize_'], order='F')
	else:
		# Just an isolated value (usually just strings)
		c = v
	
	return c

	
def load_d_info(filename):
	
	if os.path.exists(filename):
		d = json.loads(open(filename).read())
		data = []
		# When ArrayToStruct is set, all arrays are saved in 1D format along with size
		for chart in d:
			c = fill_dict_with_arrays(chart)
			data.append(c)
			
		return data
	
def load_trajectory(filename):
	
	if os.path.exists(filename):
		d = json.loads(open(filename).read())
		data = fill_dict_with_arrays(d)
		return data
	
def load_sim_opts(filename):
	
	return load_trajectory(filename)
	
def load_netpoints(filename):

	if os.path.exists(filename):
		d = json.loads(open(filename).read())
		netpoints = {}
		
		# NOTE: Hack until I can find out from Miles what the deal is with the new format...
		if "points" in d:
			points = N.array(d['points']['_ArrayData_']).reshape(d['points']['_ArraySize_'], order='F')
		else:
			points = N.array(d['_ArrayData_']).reshape(d['_ArraySize_'], order='F')
		netpoints['points'] = points
		
		# Center data
		if "center_data" in d:
			# TODO: Need to come up with more general routine here for differnt types of data...
			center_data = {}
			
			# For sparse images these are stores as [n, r*c], which are sparse 1d arrays
			# when sliced. So, they need to be sliced, then .todense() then reshape, probably
			# with 'F' order...
			center_data['data'] = parse_data_item("center_data", d['center_data'])

			if 'datatype' in d:
				# "image", ...
				center_data['datatype'] = d['datatype']

			if 'data_info' in d:
				# image dimensions (flatten to get rid of 2d-ness)
				center_data['data_info'] = parse_data_item("data_info", d['data_info']).flatten()
			
			netpoints['center_data'] = center_data
			
		return netpoints
	
# --------------------
if __name__ == "__main__":

	# data_dir = 'data/json_20130927_img_d02'
	data_dir = 'data/json_20140225_function'
	
	d_info = load_d_info( os.path.join(data_dir, 'd_info.json') )
	netpoints = load_netpoints( os.path.join(data_dir, 'netpoints.json') )
	path = load_trajectory( os.path.join(data_dir, 'trajectory.json') )
	sim_opts = load_sim_opts( os.path.join(data_dir, 'sim_opts.json') )
