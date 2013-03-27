import cherrypy
from ipca_tree import IPCATree

class HelloWorld:
  
  def __init__(self):
  	
  	# self.tree = IPCATree('../test/orig2-copy2.ipca')
  	self.tree = IPCATree('../test/mnist12.ipca')
  	
  def index(self):
  	
  	return self.tree.GetLiteTreeJSON()
  	
  index.exposed = True

cherrypy.config.update({
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(HelloWorld())
