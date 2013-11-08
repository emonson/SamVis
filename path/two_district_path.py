import numpy as N
from path_obj import PathObj

def regions_hit_within_time_window(path_index, idx_from, time_thresh, idx_to):
	'''Returns mask for path of indices hit from a given idx that hit idx2 withtin 
	time threshold t_thresh'''

	# Both routines rely on path_index being 1d
	if len(path_index.shape) == 1:
		path_idx = path_index
	else:
		path_idx = path_index.ravel()

	tfr = time_from_region(path_idx, idx_from, 'from')

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
	segments_hit = N.unique(numbered_segments[N.logical_and(within_time_window, path_idx==idx_to)])

	# Expand to whole path segment that have hits in them (return logical array)
	segments_hit_indices = N.in1d(numbered_segments, segments_hit)

	return segments_hit_indices

def time_from_region(p_idx, dist_idx, direction):
	'''Fills an array the same length as p_idx (path_index) with times
	from a given district index (time in indices, not real time). This can
	then be filtered and by time and used for looking at paths that go
	between districts within a certain window, or gathered by district to
	see the stats of time to other districts'''

	# NOTE: Relies on p_idx already being 1d (after ravel())
	if len(p_idx.shape) != 1:
		raise ValueError('p_idx needs to be 1d')
		
	t_from_reg = N.zeros_like(p_idx)
	count = 0
	past_init = False

	if direction == 'from':
		idxs = N.arange(len(p_idx))
	elif direction == 'to':
		idxs = N.arange(len(p_idx))[::-1]
	else:
		return

	for ii in idxs:
		if p_idx[ii] == dist_idx:
			# relying here on t_from_reg being initialized with zeros so can skip entry
			past_init = True
			count = 0
		else:
			if past_init:
				count = count + 1
				t_from_reg[ii] = count

	return t_from_reg

# --------------------
# --------------------
if __name__ == "__main__":

	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130601'
	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130813'
	# data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130913_ex3d'
	data_dir = '/Users/emonson/Programming/Sam/Python/path/data/json_20130927_img_d02'
	path = PathObj(data_dir)
	
	idx = 81
	t_thresh = 100
	idx2 = 104
	shi = regions_hit_within_time_window(path.path_info['path_index'],81,100,104)

