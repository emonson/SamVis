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


import simplejson
import os
import numpy as N

def fill_dict_with_arrays(obj):
	
	# When ArrayToStruct is set, all arrays are saved in 1D format along with size
	c = {}
	for k,v in obj.items():
		if isinstance(v, dict):
			# NOTE: bad name-based test!!
			if isinstance(k,str) and k.endswith('index'):
				# changing 1-based indices to 0-based
				c[k] = N.array(v['_ArrayData_']).reshape(v['_ArraySize_'], order='F') - 1
			else:
				c[k] = N.array(v['_ArrayData_']).reshape(v['_ArraySize_'], order='F')
		else:
			c[k] = v
	return c
	
def load_d_info(filename):
	
	if os.path.exists(filename):
		d = simplejson.loads(open(filename).read())
		data = []
		# When ArrayToStruct is set, all arrays are saved in 1D format along with size
		for chart in d:
			c = fill_dict_with_arrays(chart)
			data.append(c)
			
		return data
	
def load_trajectory(filename):
	
	if os.path.exists(filename):
		d = simplejson.loads(open(filename).read())
		data = fill_dict_with_arrays(d)
		return data
	
def load_sim_opts(filename):
	
	return load_trajectory(filename)
	
def load_netpoints(filename):

	if os.path.exists(filename):
		d = simplejson.loads(open(filename).read())
		data = N.array(d['_ArrayData_']).reshape(d['_ArraySize_'], order='F')
		return data
	
# --------------------
if __name__ == "__main__":

	d_info = load_d_info('data/d_info.json')
	netpoints = load_netpoints('data/netpoints.json')
	path = load_trajectory('data/trajectory.json')
	sim_opts = load_sim_opts('data/sim_opts.json')
