import cherrypy
import json
from ipca_tree import IPCATree
import os
import glob

class ResourceIndex(object):

    def __init__(self, server_url, data_names):
        self.server_url = server_url
        self.data_names = data_names

    @cherrypy.expose
    def index(self):
        return self.to_html()

    @cherrypy.expose
    def datasets(self):
        return json.dumps(self.data_names)

    def to_html(self):
        html_item = lambda (name): '<div><a href="' + self.server_url + '?data={name}">{name}</a></div>'.format(**vars())
        items = map(html_item, self.data_names)
        items = ''.join(items)
        return '<html>{items}</html>'.format(**vars())


class TreeServer:
    
    def __init__(self, path):
        
        # SamBinary v2 data
        # self.tree = IPCATree('../../test/mnist12.ipca')
        # self.tree.SetLabelFileName('../../test/mnist12_labels.data.hdr')
        
        # SamBinary v3 data
        # self.tree = IPCATree('../../test/mnist12_v3.ipca')
        # self.tree = IPCATree('../../test/mnist12_v4.ipca')
        # self.tree.SetLabelFileName('../../test/mnist12_labels.data.hdr')
        
        # HDF data
        # self.tree = IPCATree('../../test/test1_mnist12.hdf5')
        # self.tree.SetLabelFileName('../../test/test1_mnist12.hdf5')
        
        # Tree now takes a path to the data, loads 'data_info.json' and knows
        # what else to grab from there
        self.tree = IPCATree(path)
        
        self.basis_id = None
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def index(self):
        
        return json.dumps(self.tree.GetLiteTree())
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def datainfo(self):
        
        # {datatype:('image', 'function',...), shape:[n_rows, n_cols]}
        return json.dumps(self.tree.GetDataInfo())

    @cherrypy.expose
    @cherrypy.tools.gzip()
    def scalars(self, name=None, aggregation='mean'):
        
        if name:
            return json.dumps(self.tree.GetAggregatedScalarsByName(name, aggregation))
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def scaleellipses(self, id=None, basis=None):
        
        if id is not None:
            # parameters come in and get parsed out as strings
            node_id = int(id)
            
            if basis is not None:
                basis_id = int(basis)
                if self.basis_id != basis_id:
                    self.basis_id = basis_id
                    self.tree.SetBasisID_ReprojectAll(basis_id)
                    print "id", node_id, "basis_id", basis_id
        
            # seems you can also just return the dictionary
            return json.dumps(self.tree.GetScaleEllipses_NoProjection(node_id))
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def allellipses(self, basis=None):
        
        if basis is not None:
            basis_id = int(basis)
            if self.basis_id != basis_id:
                self.basis_id = basis_id
                self.tree.SetBasisID_ReprojectAll(basis_id)
                print "basis_id", basis_id
    
        return json.dumps(self.tree.GetAllEllipses_NoProjection())
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def ellipsebasis(self, id=None):
        
        if id is not None:
            node_id = int(id)
    
            # seems you can also just return the dictionary
            return json.dumps(self.tree.GetNodeCenterAndBases(node_id))
        
    @cherrypy.expose
    @cherrypy.tools.gzip()
    def contextellipses(self, id=None, bkgdscale='0'):
        # Specify a node_id that has been selected and supply a background scale.
        # Projection will be done into node's parent space, so that gives nice view of
        # the current node, plus the node itself and it and it's siblings children will be returned.
        
        #DEBUG
        print "Context ellipses called with", id, bkgdscale
        
        if id is not None:
            # parameters come in and get parsed out as strings
            node_id = int(id)   
            bkgd_scale = int(bkgdscale)
    
            return json.dumps(self.tree.GetContextEllipses(node_id, bkgd_scale))
        

# =====================

# ------------

class Root(object):
    
    def __init__(self, names_list):
        
        self.data_names = names_list
        
    @cherrypy.expose
    def index(self):
        
        raise cherrypy.HTTPRedirect("/resource_index")
        

if __name__ == '__main__':
    
    # Storing server name and port in a json file for easy config
    server_filename = 'server_conf.json'
    server_opts = json.loads(open(server_filename).read())

    # Go through data directory and add methods to root for each data set
    data_dir = server_opts['ipca_data_dir']
    vis_page = 'ipca_context.html'
    
    # Sambinary files in directories
    # data_paths = [xx for xx in glob.glob(os.path.join(data_dir,'*')) if os.path.isdir(xx)]
    # data_dirnames = [os.path.basename(xx) for xx in data_paths]
    
    # HDF5 files
    data_paths = [xx for xx in glob.glob(os.path.join(data_dir,'*.hdf5')) if os.path.isfile(xx)]
    data_dirnames = [os.path.splitext(os.path.basename(xx))[0] for xx in data_paths]

    # Storing the dataset names in the root so they can easily be passed to the html pages
    root = Root(data_dirnames)

    # This adds the methods for each data directory
    for ii,name in enumerate(data_dirnames):
        print name, data_paths[ii]
        setattr(root, name, TreeServer(data_paths[ii]))

    # add the resource index, which will list links to the data sets
    # base_url = 'http://' + server_opts['server_name'] + '/~' + server_opts['account'] + '/' + server_opts['ipca_web_path'] + '/' + vis_page
    base_url = 'http://' + server_opts['server_name'] + ':' + str(server_opts['ipca_port']) + '/' + vis_page
    root.resource_index = ResourceIndex(server_url=base_url, data_names=data_dirnames)

    # Start up server
    conf = {
        '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd()),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '.'
        },
        '/libs': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '../libs'
        },
        '/conf': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': '..'
        }
    }
    cherrypy.config.update({
            # 'tools.gzip.on' : True,
            'server.socket_port': server_opts['ipca_port'], 
            # 'server.socket_host':'127.0.0.1'
            'server.socket_host':str(server_opts['server_name'])
            })
    # cherrypy.quickstart(root)
    cherrypy.quickstart(root, '/', conf)

