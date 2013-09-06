import cherrypy
from path_obj import PathObj

class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		# self.path = PathObj('data/json_20130601')
		self.path = PathObj('data/json_20130813')
		
	@cherrypy.expose
	def index(self):
		
		return self.path.path_data_dir
		
	# ------------
	# Paths

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtcoords(self, district_id = None, depth = 1, previous_id = None, rold = None):
		
		if district_id is not None:
			dist_id = int(district_id)
			d = int(depth)
			
			if previous_id is not None:
				prev_id = int(previous_id)
				
				if rold is not None:
					
					# Parse comma-separated list of four floats encoded as a string
					try:
						a00, a01, a10, a11 = (float(r) for r in rold.split(','))
						Rold = [[a00, a01], [a10, a11]]
					except:
						Rold = [[1.0, 0.0], [0.0, 1.0]]
						
				else:
					Rold = [[1.0, 0.0], [0.0, 1.0]]
					
				return self.path.GetDistrictDeepPathLocalRotatedCoordInfo_JSON(dist_id, prev_id, d, Rold)
				
			# This is for old behavior without passing previous center district ID
			# and old R orthogonal transformation matrix
			else:
				return self.path.GetDistrictDeepPathLocalCoordInfo_JSON(dist_id, d)

	# ------------
	# Ellipses
	
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtellipses(self, district_id = None, type = 'space'):
		
		if district_id is not None:
			dist_id = int(district_id)
			if type == 'diffusion':
				return self.path.GetDistrictDiffusionEllipses_JSON(dist_id)
			else:
				return self.path.GetDistrictLocalEllipses_JSON(dist_id)


# ------------
cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(PathServer())
