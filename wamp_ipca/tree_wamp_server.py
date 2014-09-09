from twisted.internet.defer import inlineCallbacks

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession

import json
from ipca_tree import IPCATree
import os
import glob


class IPCA_DataStore(ApplicationSession):
    
    def __init__(self, config):
        ApplicationSession.__init__(self, config)
        # Dict to hold all IPCATree instances, keyed by file name
        self.trees = {}
        
        # Storing server name and port in a json file for easy config
        server_filename = 'server_conf.json'
        server_opts = json.loads(open(server_filename).read())

        # Go through data directory and add methods to root for each data set
        data_dir = server_opts['ipca_data_dir']
    
        # HDF5 files
        data_paths = [xx for xx in glob.glob(os.path.join(data_dir,'*.hdf5')) if os.path.isfile(xx)]
        data_dirnames = [os.path.splitext(os.path.basename(xx))[0] for xx in data_paths]

        # This adds the methods for each data directory
        for ii,name in enumerate(data_dirnames):
            print name, data_paths[ii]
            self.trees[name] = IPCATree(data_paths[ii])

    
    @inlineCallbacks
    def onJoin(self, details):
        
        # This takes care of all of the RPC register decorator registrations
        yield self.register(self)
        
        # This takes care of all of the pub/sub subscribe decorators
        results = yield self.subscribe(self)
        for success, res in results:
            if success:
                ## res is an Subscription instance
                print("Ok, subscribed handler with subscription ID {}".format(res.id))
            else:
                ## res is an Failure instance
                print("Failed to subscribe handler: {}".format(res.value))
                print("Ok, keyvalue-store procedures registered!")



    @wamp.register(u"test.ipca.datasets")
    def datasets(self):
        
        return self.trees.keys()
        
    @wamp.register(u"test.ipca.tree")
    def tree(self, dataset=None):
        
        if dataset in self.trees:
            return self.trees[dataset].GetLiteTree()
        
    @wamp.register(u"test.ipca.datainfo")
    def datainfo(self, dataset=None ):
        
        if dataset in self.trees:
            # {datatype:('image', 'function',...), shape:[n_rows, n_cols]}
            return self.trees[dataset].GetDataInfo()

    @wamp.register(u"test.ipca.scalars")
    def scalars(self, dataset=None, name=None, aggregation='mean'):
        
        if (dataset in self.trees) and name:
            return self.trees[dataset].GetAggregatedScalarsByName(name, aggregation)
        
    @wamp.register(u"test.ipca.scaleellipses")
    def scaleellipses(self, dataset=None, id=None, basis=None):
        
        if (dataset in self.trees) and (id is not None):
            # parameters come in and get parsed out as strings
            node_id = int(id)
            
            if basis is not None:
                basis_id = int(basis)
                if self.basis_id != basis_id:
                    self.basis_id = basis_id
                    self.trees[dataset].SetBasisID_ReprojectAll(basis_id)
                    print "id", node_id, "basis_id", basis_id
        
            # seems you can also just return the dictionary
            return self.trees[dataset].GetScaleEllipses_NoProjection(node_id)
        
    @wamp.register(u"test.ipca.allellipses")
    def allellipses(self, dataset=None, basis=None):
        
        if (dataset in self.trees) and (basis is not None):
            basis_id = int(basis)
            if self.basis_id != basis_id:
                self.basis_id = basis_id
                self.trees[dataset].SetBasisID_ReprojectAll(basis_id)
                print "basis_id", basis_id
    
        return self.trees[dataset].GetAllEllipses_NoProjection()
        
    @wamp.register(u"test.ipca.ellipsebasis")
    def ellipsebasis(self, dataset=None, id=None):
        
        if (dataset in self.trees) and (id is not None):
            node_id = int(id)
    
            # seems you can also just return the dictionary
            return self.trees[dataset].GetNodeCenterAndBases(node_id)
        
    @wamp.register(u"test.ipca.contextellipses")
    def contextellipses(self, dataset=None, id=None, bkgdscale='0'):
        # Specify a node_id that has been selected and supply a background scale.
        # Projection will be done into node's parent space, so that gives nice view of
        # the current node, plus the node itself and it and it's siblings children will be returned.
      
        if (dataset in self.trees) and (id is not None):
            # parameters come in and get parsed out as strings
            node_id = int(id)   
            bkgd_scale = int(bkgdscale)
    
            return self.trees[dataset].GetContextEllipses(node_id, bkgd_scale)
        

# =====================

if __name__ == '__main__':

    import sys, argparse

    ## parse command line arguments
    ##
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

    parser.add_argument("--web", type = int, default = 8080,
                       help = 'Web port to use for embedded Web server. Use 0 to disable.')

    args = parser.parse_args()

    # Storing server name and port in a json file for easy config
    server_filename = 'server_conf.json'
    server_opts = json.loads(open(server_filename).read())

    # add the resource index, which will list links to the data sets
    # base_url = 'http://' + server_opts['server_name'] + ':' + str(server_opts['ipca_port']) + '/' + vis_page
    # root.resource_index = ResourceIndex(server_url=base_url, data_names=data_dirnames)        
        
    if args.debug:
        from twisted.python import log
        log.startLogging(sys.stdout)     

    ## import Twisted reactor
    ##
    from twisted.internet import reactor
    print("Using Twisted reactor {0}".format(reactor.__class__))


    ## create embedded web server for static files
    ##
    if args.web:
        from twisted.web.server import Site
        from twisted.web.static import File
        root = File(".")
        root.putChild("libs", File("../libs"))
        reactor.listenTCP(args.web, Site(root))


    ## run WAMP application component
    ##
    from autobahn.twisted.wamp import ApplicationRunner
    router = 'ws://' + server_opts['server_name'] + ':' + str(server_opts['ipca_port'])

    runner = ApplicationRunner(router, u"realm1", standalone = True,
        debug = False,             # low-level logging
        debug_wamp = args.debug,   # WAMP level logging
        debug_app = args.debug     # app-level logging
    )

    ## start the component and the Twisted reactor ..
    ##
    runner.run(IPCA_DataStore)
