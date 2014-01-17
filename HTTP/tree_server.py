import cherrypy
import simplejson
from ipca_tree import IPCATree

class TreeServer:
	
	def __init__(self):
		
		# SamBinary v2 data
		# self.tree = IPCATree('../../test/mnist12.ipca')
		# self.tree.SetLabelFileName('../../test/mnist12_labels.data.hdr')
		
		# SamBinary v3 data
		self.tree = IPCATree('../../test/mnist12_v3.ipca')
		self.tree.SetLabelFileName('../../test/mnist12_labels.data.hdr')
		
		# HDF data
		# self.tree = IPCATree('../../test/test1_mnist12.hdf5')
		# self.tree.SetLabelFileName('../../test/test1_mnist12.hdf5')
		
		self.tree.LoadLabelData()
		
		self.maxID = self.tree.GetMaxID()
		self.basis_id = None
		
	@cherrypy.tools.gzip()
	def index(self):
		
		return self.tree.GetLiteTreeJSON()
		
	@cherrypy.tools.gzip()
	def scalars(self, name=None):
		
		if name:
			return self.tree.GetScalarsByNameJSON(name)
		
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
			return self.tree.GetScaleEllipses_NoProjectionJSON(node_id)
		
	@cherrypy.tools.gzip()
	def allellipses(self, basis=None):
		
		if basis is not None:
			basis_id = int(basis)
			if self.basis_id != basis_id:
				self.basis_id = basis_id
				self.tree.SetBasisID_ReprojectAll(basis_id)
				print "basis_id", basis_id
	
		return self.tree.GetAllEllipses_NoProjectionJSON()
		
	@cherrypy.tools.gzip()
	def ellipsebasis(self, id=None):
		
		if id is not None:
			node_id = int(id)
	
			# seems you can also just return the dictionary
			return self.tree.GetEllipseCenterAndFirstTwoBasesJSON(node_id)
		
	@cherrypy.tools.gzip()
	def contextellipses(self, id=None, bkgdscale='0'):
		# Specify a node_id that has been selected and supply a background scale.
		# Projection will be done into node's parent space, so that gives nice view of
		# the current node, plus the node itself and it and it's siblings children will be returned.
	  
		if id is not None:
			# parameters come in and get parsed out as strings
			node_id = int(id)	
			bkgd_scale = int(bkgdscale)
	
			return self.tree.GetContextEllipsesJSON(node_id, bkgd_scale)
		
	index.exposed = True
	scaleellipses.exposed = True
	scalars.exposed = True
	allellipses.exposed = True
	ellipsebasis.exposed = True
	contextellipses.exposed = True

# Reading server name out of a local file so it's easier to port this code
# to other machines
server_filename = '../server_conf.json'
server_opts = simplejson.loads(open(server_filename).read())

cherrypy.config.update({
		'server.socket_port': server_opts['ipca_port'], 
		'server.socket_host':server_opts['server_name']
		})
cherrypy.quickstart(TreeServer())
