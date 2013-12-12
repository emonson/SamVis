import h5py
import numpy as N
import ipca_sambinary_read as IR

tdf = '../../test/mnist12.ipca'
ldf = '../../test/mnist12_labels.data.hdr'
df = '../../test/mnist12.data.hdr'		

outfile = '../../test/mnist12_test1.hdf5'

tree_root, nodes_by_id = IR.read_sambinary_ipcadata(tdf)
labels_array = IR.read_sambinary_labeldata(ldf)
original_data_array = IR.read_sambinary_originaldata(df)

print 'data read in. starting hdf5 writing'

with h5py.File(outfile, 'w') as f:
	
	# Original data
	original_data_g = f.create_group("original_data")
	original_data_g.create_dataset("data", data=original_data_array)
	
	original_data_g.attrs['dataset_type'] = 'image'
	original_data_g.attrs['image_n_rows'] = 28
	original_data_g.attrs['image_n_columns'] = 28
	
	# Original data labels
	original_data_labels_g = original_data_g.create_group('labels')
	digit_id = original_data_labels_g.create_dataset('digit_id', data=labels_array)
	digit_id.attrs['description'] = 'Identity of the digit depicted in each image. Label is the actual digit, here 1 and 2.'
	
	# Tree
	