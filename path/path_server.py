import cherrypy
from path_obj import PathObj

class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		self.path = PathObj('data/json_20130601')
		
	def index(self):
		
		return self.path.path_data_dir
		
	@cherrypy.tools.gzip()
	def allpathcoords(self):
		
		return self.path.GetWholePathCoordList_JSON()
		

	index.exposed = True
	allpathcoords.exposed = True

cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(PathServer())
