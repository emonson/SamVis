import ipca_sambinary_read as IR
import ipca_hdf5_read as IH
import numpy as N
# from scipy import stats
import collections as C
import pprint
import json
import os
import math

# http://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module
class PrettyPrecision2SciFloat(float):
    def __repr__(self):
        return '%.2g' % self

class PrettyPrecision3SciFloat(float):
    def __repr__(self):
        return '%.3g' % self

# --------------------
class IPCATree(object):
    
    def __init__(self, data_path = None):
        """Loads all tree and node label data. data_path is the path to the directory
      in which the data and label files reside. There needs to be a file called
      data_info.json which contains the file names, etc."""
       
        self.tree_data_loaded = False
        
        # These things defined here because they are not calculated until they're needed
        self.basis_id = None
        self.lite_tree_root = None
        self.orig_data = None

        if data_path:

            # NOTE: Parsing data_info here for now... May want to move this to reader instead?
            
            # Read data from binary file
            # self.data_info = IR.read_data_info(data_path)
            
            # Read some metadata from the hdf5 file
            self.data_info = IH.read_hdf5_data_info(data_path)
            
            # Read tree data from binary file
            # tree_data_file = os.path.join(data_path, self.data_info['full_tree']['filename'])
            # print 'Trying to load data set from .ipca file... ', tree_data_file
            # self.tree_root, self.nodes_by_id = IR.read_sambinary_v3_ipcadata(tree_data_file)
            
            # Read tree data from HDF5 file
            self.tree_root, self.nodes_by_id = IH.read_hdf5_ipcadata(data_path)
            
            self.post_process_nodes(self.tree_root)

            # Since nodes now have scale (depth) info attached, can make nice 
            # reference map (lists of lists) indexed first by scale
            self.nodes_by_scale = self.collect_nodes_by_scale(self.nodes_by_id)
        
            # Using node 0 center as data center
            self.data_center = self.tree_root['center']
        
            self.tree_data_loaded = True

            # Read labels from binary file(s)
            # self.labels = {}
            # for name, info in self.data_info['original_data']['labels'].iteritems():
            #   label_data_file = os.path.join(data_path, info['filename'])
            #   self.labels[name] = IR.read_sambinary_labeldata(label_data_file, info['data_type'])

            # Read labels from hdf5 file
            self.labels = IH.read_hdf5_labeldata(data_path)

            # For now loading original data if the filename field is specified in the metadata
            # if 'filename' in self.data_info['original_data']:
            #   orig_data_path = os.path.join(data_path, self.data_info['original_data']['filename'])
            #   self.orig_data = IR.read_sambinary_originaldata(orig_data_path, self.data_info['original_data']['data_type'])

            # Now that data is loaded, default projection basis is
            # root node first two PCA directions
            # Using Sam's notation for now on matrices / arrays
            # self.V = self.nodes_by_id[0]['phi'][:2,:].T
            # self.SetBasisID_ReprojectAll(0)
        
    # --------------------
    def post_process_nodes(self, root_node, child_key='children', scale_key='scale'):
    
        # Clear out empty children from tree and convert deques into lists
        # and add scale (depth in tree starting with 0 at root) as we go

        MODE = 'breadth_first'
        # MODE = 'depth_first'

        # Iterative traversal
        #       Note: for Python deque, 
        #               extendleft / appendleft --> [0, 1, 2] <-- extend / append
        #                                            popleft <--                         --> pop

        nodes = C.deque()
        scales = C.deque()
        nodes.appendleft(root_node)
        scales.appendleft(0)

        while len(nodes) > 0:
            # Get next node to process from deque for iterative traversal
            if MODE == 'breadth_first':
                current_node = nodes.pop()
                current_scale = scales.pop()
            elif MODE == 'depth_first':
                current_node = nodes.popleft()
                current_scale = scales.popleft()
            else:
                break
        
            # Add scale (depth) on to current node
            current_node[scale_key] = current_scale
            
            # Delete empty children deques and change rest into lists
            if child_key in current_node:
                if len(current_node[child_key]) == 0:
                    del current_node[child_key]
                else:
                    current_node[child_key] = list(current_node[child_key])
    
            # Add on to deque for ongoing iterative tree traveral
            if child_key in current_node:
                nodes.extendleft(current_node[child_key])
                scales.extendleft([current_scale+1]*len(current_node[child_key]))

    # --------------------
    def collect_nodes_by_scale(self, nodes_by_id, scale_key='scale'):
        """Returns nodes_by_scale"""
        
        if len(nodes_by_id) == 0 or scale_key not in nodes_by_id[0]:
            return None
        
        # This will be a list of lists
        nodes_by_scale = []
        
        # TODO: since nodes_by_id is now a dictionary rather than a list, need
        #  to make sure this doesn't need to be traversed in any particular order...
        for id, node in nodes_by_id.iteritems():
            scale = node[scale_key]
            
            if scale > (len(nodes_by_scale) - 1):
                nodes_by_scale.extend(list([[]]*((scale+1)-len(nodes_by_scale))))
            
            nodes_by_scale[scale].append(node)
        
        return nodes_by_scale
    
    # --------------------
    def calculate_node_projected_data(self, node_id):
        """Calculate data for this node_id projected into """
        
        if self.orig_data is not None:
            
            node = self.nodes_by_id[node_id]
            data_idxs = node['indices']
            node_data = self.orig_data[:,data_idxs]
            
            # Compute projection of this node's data
            # 2 x n_points
            projected_data = self.V.T * node_data
            
            # return 2 x n_points matrix
            return projected_data

    # --------------------
    def calculate_node_ellipse(self, node_id):
        """Calculate tuple containing (X, Y, RX, RY, Phi, i) for a node for a D3 ellipse"""
        
        node = self.nodes_by_id[node_id]
        
        # Compute projection of this node's covariance matrix
        A = node['phi'].T
        sigma = N.matrix(N.diag(node['sigma']))
        center = node['center']
        
        print 'A', A.shape, 'sigma', sigma.shape
        A = A * N.sqrt(sigma)
        C1 = self.V.T * A
        C = C1 * C1.T

        # ALT METHOD for transforming the unit circle according to projected covariance
        # Compute svd in projected space to find rx, ry and rotation for ellipse in D3 vis
        U, S, V = N.linalg.svd(C)

        # Project mean
        xm = N.dot(self.V.T, center)
        xrm = N.dot(self.V.T, self.data_center)
        xm = N.squeeze(N.asarray(xm - xrm))
        
        # Calculate scalings (not needed because it's in sigma
        # N.squeeze(N.asarray(N.sum(N.square(a),1)))
        
        # Calculate angles
        phi_deg = 360 * ( N.arctan(-U[0,1]/U[0,0] )/(2*N.pi))
        # t2 = 360 * ( N.arctan(U[1,0]/U[1,1] )/(2*N.pi))
        
        # How many sigma ellipses cover
        s_mult = 2.0
        results_tuple = (xm[0], xm[1], s_mult*S[0], s_mult*S[1], phi_deg)
        # print results_tuple
        result_list = self.pretty_sci_floats(results_tuple)
        result_list.append(node['id'])
        # print result_list
        
        return result_list
    
    # --------------------
    def calculate_ellipse_bounds(self, e_params):
        """Rough calculation of ellipse bounds by major and minor extrema points of ellipses"""
        
        # Ellipse params is a list of tuples (X, Y, RX, RY, Phi, i)
        params_array = N.array(e_params)
        # print params_array
        n_ellipses = params_array.shape[0]
        X = params_array[:,0]
        Y = params_array[:,1]
        RX = params_array[:,2]
        RY = params_array[:,3]
        PhiR = 2.0*N.pi*params_array[:,4]/360.0
        PhiRmin = N.pi/2.0 - PhiR
        
        Xs = N.zeros(4*n_ellipses)
        Ys = N.zeros(4*n_ellipses)
        
        # Collect Xs and Ys for each of the 4 ends of each of the ellipses
        idxs = N.arange(n_ellipses)
        Xs[0*n_ellipses + idxs] = X + RX * N.cos(PhiR)
        Ys[0*n_ellipses + idxs] = Y + RX * N.sin(PhiR)
        Xs[1*n_ellipses + idxs] = X - RX * N.cos(PhiR)
        Ys[1*n_ellipses + idxs] = Y - RX * N.sin(PhiR)
        Xs[2*n_ellipses + idxs] = X - RY * N.cos(PhiRmin)
        Ys[2*n_ellipses + idxs] = Y + RY * N.sin(PhiRmin)
        Xs[3*n_ellipses + idxs] = X + RY * N.cos(PhiRmin)
        Ys[3*n_ellipses + idxs] = Y - RY * N.sin(PhiRmin)
        # print Xs
        # print Ys
         
        minX = N.min(Xs)
        maxX = N.max(Xs)
        minY = N.min(Ys)
        maxY = N.max(Ys)
        # print [(minX, maxX), (minY, maxY)]
        
        return [(minX, maxX), (minY, maxY)]
    
    # --------------------
    def RegenerateLiteTree(self, children_key='c', parent_id_key='p', key_dict = {'id':'i', 
                                                                                    'npoints':'v',
                                                                                    'scale':'s'}
                                                                                    ):
        """Keeping full tree as true record of data, and regenerate new lite tree
        when needed, like after labels update. Children and parent keys required,
        so they're not in the key string map (originals assumed to be 'children' and 'parent_id')"""
        
        # Doing a two-pass strategy for constructing the tree. Fill in basic lite_nodes_by_id
        # first, with all object-local fields, then take another pass through, filling in the
        # children after being assured all nodes exist.
        
        # This is only for helping fill in children. Not keeping it around.
        lite_nodes_by_id = {}
        
        # First pass with object-local fields
        for id,node in self.nodes_by_id.iteritems():
            lite_node = {}
            # NOTE: Not copying parent id to lite tree for now!
            # if 'parent_id' in node:
                # lite_node[parent_id_key] = parent_id
            # All other values copied over
            for k,v in key_dict.items():
                lite_node[v] = node[k]
            
            lite_nodes_by_id[id] = lite_node
        
        # Second pass for children list
        for id,node in self.nodes_by_id.iteritems():
            if 'children' in node:
                lite_nodes_by_id[id][children_key] = []
                for child in node['children']:
                    cid = child['id']
                    lite_nodes_by_id[id][children_key].append(lite_nodes_by_id[cid])
        
        # This assignment of root node keeps whole lite tree
        self.lite_tree_root = lite_nodes_by_id[self.tree_root['id']]

    # --------------------
    def SetBasisID(self, id):
    
        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            
            self.V = self.nodes_by_id[id]['phi'][:2,:].T

    # --------------------
    def SetBasisID_ReprojectAll(self, id):
    
        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            
            if id != self.basis_id:
                self.basis_id = id
                self.V = self.nodes_by_id[id]['phi'][:2,:].T
                
                self.all_ellipse_params = []
                for id,node in self.nodes_by_id.iteritems():
                    self.all_ellipse_params.append(self.calculate_node_ellipse(node['id']))

    # --------------------
    def GetMaxID(self):
    
        if self.tree_data_loaded:
            return len(self.nodes_by_id)-1

    # --------------------
    def GetScaleEllipses(self, id = None):
        """Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
    
        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            
            scale = self.nodes_by_id[id]['scale']
            
            ellipse_params = []
            # Always include node 0 for now
            if scale != 0:
                ellipse_params.append(self.calculate_node_ellipse(0))
            for node in self.nodes_by_scale[scale]:
                ellipse_params.append(self.calculate_node_ellipse(node['id']))
            
            bounds = self.calculate_ellipse_bounds(ellipse_params)
            return_obj = {'data':ellipse_params, 'bounds':bounds}

            return return_obj
        
    # --------------------
    def GetScaleEllipsesJSON(self, id = None):
    
        return json.dumps(self.GetScaleEllipses(id))
        
    # --------------------
    def GetContextEllipses(self, id = None, bkgd_scale = None):
        """Take in node_id and scale for background ellipses for vis context.
           Project into parent scale basis, and return ellipses for parent, self, sibling and
           self and sibling's children, as well as background scale ellipses."""

        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            if (bkgd_scale is not None) and (bkgd_scale < len(self.nodes_by_scale)):
            
                ellipse_params = []
                bkgd_ellipse_params = []
                
                selected_node = self.nodes_by_id[id]
                
                # If this is not the root node
                if 'parent_id' in selected_node:
                    # Project into parent space
                    chose_root_node = False
                    parent_id = selected_node['parent_id']
                else:
                    chose_root_node = True
                    parent_id = self.tree_root['id']
                
                self.SetBasisID(parent_id)
                ellipse_params.append(self.calculate_node_ellipse(parent_id))

                parent_node = self.nodes_by_id[parent_id]
                # also get children, if present
                if 'children' in parent_node:
                    for node in parent_node['children']:
                        ellipse_params.append(self.calculate_node_ellipse(node['id']))
                        # and children of children
                        # unless choosing root node...
                        if 'children' in node and not chose_root_node:
                            for child_node in node['children']:
                                ellipse_params.append(self.calculate_node_ellipse(child_node['id']))
                
                for node in self.nodes_by_scale[bkgd_scale]:
                    # * * * NOTE * * * Not passing any background scales!!
                    pass
                    # bkgd_ellipse_params.append(self.calculate_node_ellipse(node['id']))
                bounds = self.calculate_ellipse_bounds(ellipse_params + bkgd_ellipse_params)
                return_obj = {'foreground':ellipse_params, 'background':bkgd_ellipse_params, 'bounds':bounds}

                return return_obj
        
    # --------------------
    def GetContextEllipsesJSON(self, id = None, bkgd_scale = None):
    
        return json.dumps(self.GetContextEllipses(id, bkgd_scale))
        
    # --------------------
    def GetScaleEllipses_NoProjection(self, id = None):
        """Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
    
        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            
            scale = self.nodes_by_id[id]['scale']
            
            ellipse_params = []
            # Always include node 0 for now
            if scale != 0:
                ellipse_params.append(self.all_ellipse_params[0])
            for node in self.nodes_by_scale[scale]:
                ellipse_params.append(self.all_ellipse_params[node['id']])
            
            bounds = self.calculate_ellipse_bounds(ellipse_params)
            return_obj = {'data':ellipse_params, 'bounds':bounds}

            return return_obj
        
    # --------------------
    def GetAllEllipses_NoProjection(self):
        """Return dict of all ellipses in tree"""
    
        if self.tree_data_loaded:
            
            bounds = self.calculate_ellipse_bounds(self.all_ellipse_params)
            return_obj = {'data':self.all_ellipse_params, 'bounds':bounds}

            return return_obj
        
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
    # http://stackoverflow.com/questions/15450192/fastest-way-to-compute-entropy-in-python
    def entropy(self, labels):
        """ Computes entropy of label distribution. Originally called entropy2()"""

        if not hasattr(labels, '__len__'):
            return 0
        
        n_labels = len(labels)

        if n_labels <= 1:
            return 0

        counts = N.bincount(labels)
        probs = counts / float(n_labels)
        n_classes = N.count_nonzero(probs)

        if n_classes <= 1:
            return 0

        ent = 0.0

        # Compute standard entropy.
        for p in probs:
            # NOTE: not sure if this test is right, but I was getting math errors...
            if p > 0:
                ent -= p * math.log(p, n_classes)

        return ent

  # --------------------
    def GetNodeCenterAndBases(self, id = None):
        """Take in _node ID_ and get out dict of all ellipses for that nodes's scale in tree"""
    
        if (id is not None) and self.tree_data_loaded and id >= 0 and id < len(self.nodes_by_id):
            
            center = self.nodes_by_id[id]['center'].tolist()
            bases = self.nodes_by_id[id]['phi'].tolist()
            return_obj = {'center':center, 'center_range':(N.min(center), N.max(center)),
                          'bases':bases, 'bases_range':(N.min(bases), N.max(bases))}

            return return_obj
        
    # --------------------
    def GetScaleEllipses_NoProjectionJSON(self, id = None):
        """Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""
    
        return json.dumps(self.GetScaleEllipses_NoProjection(id))
        
    # --------------------
    def GetAllEllipses_NoProjectionJSON(self):
        """Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""
    
        return json.dumps(self.GetAllEllipses_NoProjection())
        
    # --------------------
    def GetNodeCenterAndBasesJSON(self, id = None):
        """Take in _node ID_ and get out JSON of all ellipses for that nodes's scale in tree"""

        return json.dumps(self.pretty_sci_floats(self.GetNodeCenterAndBases(id)))
        
    # --------------------
    def GetDataInfo_JSON(self):
        """Get the original data information. This is a slightly enhanced version of
        the data_info.json file stored on disk with the data."""
        
        n_nodes = len(self.nodes_by_id)
        
        # centers bounds
        c_bounds = N.zeros((n_nodes,2))
        # bases bounds
        b_bounds = N.zeros((n_nodes,2))
        
        # NOTE: nodes_by_id is a dict
        for ii, k in enumerate(self.nodes_by_id):
            center = self.nodes_by_id[k]['center']
            bases = self.nodes_by_id[k]['phi']
            c_bounds[ii,:] = (center.min(), center.max())
            b_bounds[ii,:] = (bases.min(), bases.max())

        results = {}
        results['data_info'] = self.data_info
        results['centers_bounds'] = (N.asscalar(c_bounds[:,0].min()),N.asscalar(c_bounds[:,1].max()))
        results['bases_bounds'] = (N.asscalar(b_bounds[:,0].min()),N.asscalar(b_bounds[:,1].max()))
        results['scalar_names'] = self.labels.keys()
        results['root_node_id'] = self.tree_root['id']

        return json.dumps(results)

    # --------------------
    def GetAggregatedScalarsByNameJSON(self, name = None, aggregation = 'mean'):
        """Take in scalar "name" and aggregation method
        and get out JSON of scalars for all nodes by id, calculated 'on the fly'.
        aggregation = 'mean', 'mode', 'entropy', 'hist'...
        NOTE: only works with non-negative integer labels!!
        Output is a dict/obj of scalar labels by id and range array"""
        
        if name:
            if name in self.labels:
                # Original data labels is a numpy array
                data_labels_arr = self.labels[name]
                
                # Average of only requested scalar
                if aggregation == 'mean':
                    node_labels_dict = {}
                    for id,node in self.nodes_by_id.iteritems():
                        indices = node['indices']
                        node_labels_dict[id] = N.mean(data_labels_arr[indices])
                    output = self.pretty_sci_floats(node_labels_dict)
                    output_arr = N.array(node_labels_dict.values())
                    max = N.asscalar(N.max(output_arr))
                    min = N.asscalar(N.min(output_arr))
                    domain = self.pretty_sci_floats([min, max])
                        
                # Winner is most highly represented label (integer in and out)
                elif aggregation == 'mode':
                    node_labels_dict = {}
                    for id,node in self.nodes_by_id.iteritems():
                        indices = node['indices']
                        # NOTE: Sometimes a single point in a node ends up as a scalar index
                        # rather than an array of indices...
                        if hasattr(indices, '__len__'):
                            counts = N.bincount(data_labels_arr[indices])
                        else:
                            counts = N.bincount([data_labels_arr[indices]])
                        node_labels_dict[id] = N.argmax(counts)
                    output = node_labels_dict
                    output_arr = N.array(node_labels_dict.values(), dtype='int')
                    max = N.asscalar(N.max(output_arr))
                    min = N.asscalar(N.min(output_arr))
                    domain = N.unique(output_arr).tolist()
                
                # "Standard" entropy
                elif aggregation == 'entropy':
                    node_labels_dict = {}
                    for id,node in self.nodes_by_id.iteritems():
                        indices = node['indices']
                        node_labels_dict[id] = self.entropy(data_labels_arr[indices])
                    output = self.pretty_sci_floats(node_labels_dict)
                    output_arr = N.array(node_labels_dict.values())
                    max = N.asscalar(N.max(output_arr))
                    min = N.asscalar(N.min(output_arr))
                    domain = self.pretty_sci_floats([min, max])
                
                # 'hist'
                elif aggregation == 'hist':
                    unique_labels = N.unique(data_labels_arr)
                    # want to be able to look up the indices of each of the labels
                    # for cases in which they're not sequential and individual nodes where
                    # not all labels are present
                    reverse_lookup = N.zeros(N.max(unique_labels)+1, dtype='int')-1
                    for ii,ul in enumerate(unique_labels):
                        reverse_lookup[ul] = ii
                    n_bins = len(unique_labels)
                    node_labels_dict = {}
                    for id,node in self.nodes_by_id.iteritems():
                        indices = node['indices']
                        bincount = N.bincount(data_labels_arr[indices])
                        node_unique_labels = N.nonzero(bincount)
                        label_indices = reverse_lookup[node_unique_labels]
                        tmp_labels_arr = N.zeros((1,n_bins),dtype='int')
                        tmp_labels_arr[label_indices] = bincount[node_unique_labels]
                        node_labels_dict[id] = tmp_labels_arr.tolist()
                    output = node_labels_dict
                    # For a histogram lower bound assumed to be zero, so only computing max
                    domain = {'domain':unique_labels.tolist(), 'max':N.max(labels, axis=0).tolist()}
                                
                # Error on unsupported aggregation method
                else:
                    return "Aggregation method " + aggregation + " not supported. Use mean, hist or mode"

                return json.dumps({'labels':output, 'domain':domain})


    # --------------------
    def GetLiteTreeJSON(self, pretty = False):
        
                # Lite node key names are minimized to reduce transferred JSON size
                # 'i' = 'id'
                # 'c' = 'children'
                # 'v' = 'value'
                # 's' = 'scale'
        if not self.lite_tree_root:
            self.RegenerateLiteTree()
        
        if pretty:
            return json.dumps(self.lite_tree_root, indent=2)
        else:
            return json.dumps(self.lite_tree_root)
    
    # --------------------
    def WriteLiteTreeJSON(self, filename, pretty = False):
    
        out_file = None
        
        if filename and type(filename) == str:
            out_file = os.path.abspath(filename)
        else:
            raise IOError, "output filename needs to be a non-empty string"

        f = open(out_file, 'w')
        if pretty:
            f.write(self.GetLiteTreeJSON(True))
        else:
            f.write(self.GetLiteTreeJSON())
        f.close()

# --------------------
# --------------------
if __name__ == "__main__":

    # from tkFileDialog import askopenfilename
    # data_file = askopenfilename()
#   data_file = '/Users/emonson/Programming/Sam/test/orig2-copy2.ipca'
#   label_file = '/Users/emonson/Programming/Sam/test/labels02.data.hdr'
    
    # v2 sambinary
    # tree_file = '/Users/emonson/Programming/Sam/test/mnist12.ipca'
    # label_file = '/Users/emonson/Programming/Sam/test/mnist12_labels.data.hdr'
    # data_file = '/Users/emonson/Programming/Sam/test/mnist12.data.hdr'

    # v3 sambinary
    # tree_file = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2/tree.ipca'
    # label_file = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2/labels.data.hdr'
    # data_path = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2'
    
    # HDF5
    # tree_file = '/Users/emonson/Programming/Sam/test/test1_mnist12.hdf5'
    # label_file = '/Users/emonson/Programming/Sam/test/test1_mnist12.hdf5'
    data_path = '/Users/emonson/Data/GMRA_data/mnist12_v5_d8c2_test1.hdf5'

    # DataSource loads .ipca file and can generate data from it for other views
    # tree = IPCATree(tree_file)
    # tree.SetLabelFileName(label_file)
    # tree.LoadLabelData()
    
    tree = IPCATree(data_path)
    
    # print tree.GetLiteTreeJSON()

        
