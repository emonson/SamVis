import cherrypy
from path_obj import PathObj

class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		self.path = PathObj('data/json_20130601')
		
	def index(self):
		
		return self.path.path_data_dir
		
	@cherrypy.tools.gzip()
	def rawpathcoords(self):
		
		return self.path.GetRawPathCoordList_JSON()
		
	@cherrypy.tools.gzip()
	def netcoords(self):
		
		return self.path.GetNetCoordList_JSON()
		
	@cherrypy.tools.gzip()
	def netpathcoords(self):
		
		return self.path.GetNetPathCoordList_JSON()
		
	@cherrypy.tools.gzip()
	def globalpathcoords(self):
		
		return self.path.GetGlobalPathCoordList_JSON()

	@cherrypy.tools.gzip()
	def allellipses(self):
		
		return self.path.GetAllEllipses_JSON()

	@cherrypy.tools.gzip()
	def pathellipses(self):
		
		return self.path.GetPathEllipses_JSON()


	index.exposed = True
	rawpathcoords.exposed = True
	netcoords.exposed = True
	netpathcoords.exposed = True
	globalpathcoords.exposed = True
	allellipses.exposed = True
	pathellipses.exposed = True

cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(PathServer())
