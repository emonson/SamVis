import cherrypy
from ipca_tree import IPCATree

class HelloWorld:
	
	def __init__(self):
		
		# self.tree = IPCATree('../test/orig2-copy2.ipca')
		# self.tree = IPCATree('../test/mnist12_d2.ipca')
		self.tree = IPCATree('../test/mnist12.ipca')
		self.tree.SetLabelFileName('../test/mnist12_labels.data.hdr')
		self.tree.LoadLabelData()
		self.maxID = self.tree.GetMaxID()
		
	def index(self):
		
		return self.tree.GetLiteTreeJSON()
		
	def scaleellipses(self, id=None):
		
		if id is not None:
			# parameters come in and get parsed out as strings
			node_id = int(id)
		
			return self.tree.GetScaleEllipsesJSON(node_id)
		
	index.exposed = True
	scaleellipses.exposed = True

cherrypy.config.update({
		'server.socket_port': 9000, 
		'server.socket_host':'127.0.0.1'
		# 'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(HelloWorld())
