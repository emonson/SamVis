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

		self.path_data_loaded = False
		self.path_data_dir = None
		self.d_info = None
		self.netpoints = None
		self.path_info = None
		self.sim_opts = None

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
		
	# --------------------
	def GetRawPathCoordList_JSON(self):
		
		return simplejson.dumps(self.path_info['path'].tolist())
		
	# --------------------
	def GetNetCoordList_JSON(self):
		
		return simplejson.dumps(self.netpoints[:,:2].tolist())
		
	# --------------------
	def GetNetPathCoordList_JSON(self):
		
		netpts = self.netpoints[self.path_info['path_index'].squeeze(),:2]
		netpts = netpts + 0.0005*(N.max(self.netpoints)-N.min(self.netpoints))*N.random.standard_normal(netpts.shape)
		return simplejson.dumps(netpts.tolist())
		
	# --------------------
	def GetGlobalPathCoordList_JSON(self):
		
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
# --------------------
if __name__ == "__main__":

	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130601'
	path = PathObj(data_dir)
	# print path.GetWholePathCoordList_JSON()

		
