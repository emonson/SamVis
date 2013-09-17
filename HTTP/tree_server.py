import cherrypy
from ipca_tree import IPCATree

class HelloWorld:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		# self.tree = IPCATree('../../test/orig2-copy2.ipca')
		# self.tree.SetLabelFileName('../../test/labels02.data.hdr')
		self.tree = IPCATree('../../test/mnist12.ipca')
		# self.tree = IPCATree('../../test/mnist12_d2.ipca')
		self.tree.SetLabelFileName('../../test/mnist12_labels.data.hdr')
		# self.tree.SetOriginalDataFileName('../../test/mnist12.data.hdr')
		
		self.tree.LoadLabelData()
		# self.tree.LoadOriginalData()
		
		self.maxID = self.tree.GetMaxID()
		self.basis_id = None
		
	@cherrypy.tools.gzip()
	def index(self):
		
		return self.tree.GetLiteTreeJSON()
		
	@cherrypy.tools.gzip()
	def scalars(self, name=None):
		
		if name:
			return self.tree.GetScalarsByNameJSON(name)
		
	# cherrypy wouldn't also gzip json generated with json_out()...
	# @cherrypy.tools.json_out()
	@cherrypy.tools.gzip()
	def scaleellipses(self, id=None, basis=None):
		# browser was having trouble accepting gzipped json with application/json type
		# cherrypy.response.headers['Content-Type'] = "application/json"
		# cherrypy.response.headers['Content-Encoding'] = "gzip"
		
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
		# browser was having trouble accepting gzipped json with application/json type
		# cherrypy.response.headers['Content-Type'] = "application/json"
		# cherrypy.response.headers['Content-Encoding'] = "gzip"
		
		if basis is not None:
			basis_id = int(basis)
			if self.basis_id != basis_id:
				self.basis_id = basis_id
				self.tree.SetBasisID_ReprojectAll(basis_id)
				print "basis_id", basis_id
	
		# seems you can also just return the dictionary
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
	
			# seems you can also just return the dictionary
			print 'context', node_id, bkgd_scale
			return self.tree.GetContextEllipsesJSON(node_id, bkgd_scale)
		
	index.exposed = True
	scaleellipses.exposed = True
	scalars.exposed = True
	allellipses.exposed = True
	ellipsebasis.exposed = True
	contextellipses.exposed = True
	# scaleellipses._cp_config = {'tools.gzip.on': True}

cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9002, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'archer.trinity.duke.edu'
		})
cherrypy.quickstart(HelloWorld())
