import cherrypy
from path_obj import PathObj

class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		self.path = PathObj('data/json_20130601')
		
	@cherrypy.expose
	def index(self):
		
		return self.path.path_data_dir
		
	# ------------
	# Paths

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def rawpathcoords(self):
		
		return self.path.GetRawPathCoordList_JSON()
		
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def netcoords(self):
		
		return self.path.GetNetCoordList_JSON()
		
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def netpathcoords(self):
		
		return self.path.GetNetPathCoordList_JSON()
		
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def globalpathcoords(self):
		
		return self.path.GetGlobalPathCoordList_JSON()

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def globalpathpairs(self):
		
		return self.path.GetGlobalPathCoordPairs_JSON()

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtpathcoords(self, district_id = None):
		
		if district_id is not None:
			dist_id = int(district_id)
			return self.path.GetDistrictPathCoordList_JSON(dist_id)

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtpathpairs(self, district_id = None):
		
		if district_id is not None:
			dist_id = int(district_id)
			return self.path.GetDistrictPathCoordPairs_JSON(dist_id)

	# ------------
	# Ellipses
	
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def allellipses(self):
		
		return self.path.GetAllEllipses_JSON()

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def pathellipses(self):
		
		return self.path.GetPathEllipses_JSON()

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def pathellipses(self):
		
		return self.path.GetPathEllipses_JSON()

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtellipses(self, district_id = None):
		
		if district_id is not None:
			dist_id = int(district_id)
			return self.path.GetDistrictEllipses_JSON(dist_id)


# ------------
cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(PathServer())
