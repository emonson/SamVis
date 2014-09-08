import numpy as N
import os
import h5py

import time

# http://stackoverflow.com/questions/8889083/how-to-time-execution-time-of-a-batch-of-code-in-python
def time_this(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print 'func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts)
        return result

    return timed

@time_this
def read_hdf5_ipcadata(tree_data_filename):
    """ Read IPCA tree and data from Sam's binary file format which he dumps variables
    from his tree in C++. Return root of tree (which is just a bunch of dictionaries
    linked to each other through children and parent) and a dictionary of same node element objects
    but indexed by id rather than in a tree structure."""
    
    with h5py.File(tree_data_filename, 'r') as f:
        
        # Make a first pass through nodes_by_id and grab node data
        nodes_by_id = {}
        n_nodes = f['/full_tree'].attrs['n_nodes']
        nodes_g = f['/full_tree/nodes']

        print '...first pass for node data'
        for id_str, node_g in nodes_g.iteritems():
            
            # temp space for the id
            id = -1
            node_data = {}
            
            for d_name, d_item in node_g.items():
                if isinstance(d_item, h5py.Group) and d_name == 'children':
                    node_data['child_ids'] = []
                    for c_name in d_item:
                        node_data['child_ids'].append(int(c_name))
                elif isinstance(d_item, h5py.Dataset):
                    # There is some sort of difference between h5py and matlab high-level
                    # hdf5 api, where h5py specified single scalar value datasets as
                    # shape = (), whereas can't get Matlab to do this, shape = (1,)
                    if d_item.shape and (d_item.size > 1):
                        data = N.empty(d_item.shape, dtype=d_item.dtype)
                        d_item.read_direct(data)
                        node_data[d_name] = data
                    else:
                        # Return native python type with asscalar() so scalars are JSON serializable
                        node_data[d_name] = N.asscalar(d_item[()])
            
            nodes_by_id[node_data['id']] = node_data
    
        print '...second pass for children'
        # Make a second pass through to put in hard links to children now that they all exist
        for id, node in nodes_by_id.iteritems():
            
            if 'child_ids' in node:
                node['children'] = []
                for cid in node['child_ids']:
                    node['children'].append(nodes_by_id[cid])
                    
        # Get the tree root by id from the hard link
        tree_root_id = N.asscalar(f['/full_tree/tree_root']['id'][()])
        tree_root = nodes_by_id[tree_root_id]
    
        print '...ipca tree data finished reading'

    return tree_root, nodes_by_id
    

def read_hdf5_labeldata(label_data_filename):
    """Read IPCA original data labels and store them in dictionary by name"""
    
    labels = {}
    label_descriptions = {}
    
    with h5py.File(label_data_filename, 'r') as f:

        # Original data labels
        labels_g = f['/original_data/labels']
        for lname in labels_g.keys():
            ld = labels_g[lname]
            label_data = N.empty(ld.shape, dtype=ld.dtype)
            ld.read_direct(label_data)
            labels[lname] = label_data
            label_descriptions[lname] = ld.attrs['description']
            
    return labels #, label_descriptions


def checked_filename(filename):
    if filename and type(filename) == str:
        return  os.path.abspath(filename)
    else:
        raise IOError, "filename needs to be a non-empty string"

    if not os.path.isfile(self.label_file):
        raise IOError, "input file does not exist"
    
    return ""


def read_hdf5_originaldata(orig_data_file):
    """Read the original data used for IPCA"""

    with h5py.File(orig_data_file, 'r') as f:
    
        # Original data
        original_data_g = f['/original_data']
        od = original_data_g['data']
        
        orig_data = N.empty(od.shape, dtype=od.dtype)
        od.read_direct(orig_data)
    
        dataset_type = original_data_g.attrs['dataset_type']
        if dataset_type == 'image':
            image_n_rows = original_data_g.attrs['image_n_rows']
            image_n_columns = original_data_g.attrs['image_n_columns']
    
    return orig_data

def read_hdf5_data_info(orig_data_file):
    """Read some metadata from the hdf5 file"""

    with h5py.File(orig_data_file, 'r') as f:
    
        data_info = {}
        
        # Original data
        original_data_g = f['/original_data']
        
        data_info['original_data'] = {}
        
        for k,v in original_data_g.attrs.items():
            # try to deal with matlab-saved values which show up as single arrays...
            if isinstance(v, N.ndarray) and v.dtype.char == 'l' and (len(v) == 1):
                data_info['original_data'][k] = N.asscalar(v)
            else:
                data_info['original_data'][k] = v

    
    return data_info


# --------------------
if __name__ == "__main__":

    hdf = '../../test/test1_mnist12.hdf5'       
    
    print 'reading ipca data'
    tree_root, nodes_by_id = read_hdf5_ipcadata(hdf)
    print tree_root.keys()
    print nodes_by_id[20].keys()
    
    print 'reading labels'
    labels, label_descriptions = read_hdf5_labeldata(hdf)
    print labels
    print label_descriptions
    
    print 'reading original data'
    orig_data = read_hdf5_originaldata(hdf)
    print orig_data.shape, orig_data.dtype
    print orig_data