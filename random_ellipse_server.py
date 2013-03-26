import cherrypy
import json

class HelloWorld:
  
  def __init__(self):
  	
  	self.tree = IPCATree('../test/mnist12.ipca')
  	
  def index(self):
  	return "Random Ellipse Server"
  
  def ellipses(self, n=20):
  	
  	return self.tree.GetLiteTreeJSON()
  	
  index.exposed = True

cherrypy.config.update({
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(HelloWorld())
