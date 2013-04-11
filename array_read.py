# from scipy.io.numpyio import fread
import numpy as N
import os

in_header = '/Users/emonson/Programming/Sam/test/mnist12.data.hdr'

f = open(in_header, 'r')

vectype = f.readline().strip()
if vectype != 'DenseMatrix':
	raise IOError, "Data file needs to be a DenseMatrix"

size = f.readline().strip().split()
if size[0] != 'Size:' or size[2] != 'x':
	raise IOError, "Problem reading data matrix size"
m = int(size[1])
n = int(size[3])

elsize = f.readline().strip().split()
if elsize[0] != 'ElementSize:':
	raise IOError, "Problem reading data matrix element size"
n_bytes = int(elsize[1])

rowmaj = f.readline().strip().split()
if rowmaj[0] != 'RowMajor:':
	raise IOError, "Problem reading data matrix row major order"
row_major = int(rowmaj[1])

datafile = f.readline().strip().split()
if datafile[0] != 'DataFile:':
	raise IOError, "Problem reading data matrix file name"
data_file = os.path.abspath(os.path.join(os.path.dirname(in_header),datafile[1]))

f.close()

fd = open(data_file, 'rb')
data = fd.read(8*m*n)
X = N.fromstring(data, dtype=N.dtype('d8'), count=m*n).reshape(m,n)
# X = N.fromfile(fd, dtype=N.float64, count=m*n)
fd.close()
