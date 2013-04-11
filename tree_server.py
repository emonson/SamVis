import cherrypy
from ipca_tree import IPCATree

class HelloWorld:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		# self.tree = IPCATree('../test/orig2-copy2.ipca')
		# self.tree.SetLabelFileName('../test/labels02.data.hdr')
		self.tree = IPCATree('../test/mnist12.ipca')
		# self.tree = IPCATree('../test/mnist12_d2.ipca')
		self.tree.SetLabelFileName('../test/mnist12_labels.data.hdr')
		
		self.tree.LoadLabelData()
		self.maxID = self.tree.GetMaxID()
		
	@cherrypy.tools.gzip()
	def index(self):
		
		return self.tree.GetLiteTreeJSON()
		
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
				self.tree.SetBasisID(basis_id)
				print "id", node_id, "basis_id", basis_id
		
			# seems you can also just return the dictionary
			return self.tree.GetScaleEllipsesJSON(node_id)
		
	index.exposed = True
	scaleellipses.exposed = True
	# scaleellipses._cp_config = {'tools.gzip.on': True}

cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(HelloWorld())
