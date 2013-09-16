import cherrypy
from path_obj import PathObj

class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self):
		
		# self.path = PathObj('data/json_20130601')
		self.path = PathObj('data/json_20130813')
		# self.path = PathObj('data/json_20130913_ex3d')
		
	@cherrypy.expose
	def index(self):
		
		return self.path.path_data_dir
		
	# ------------
	# Paths

	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtcoords(self, district_id = None, depth = 1, previous_id = None, rold = "1.0, 0.0, 0.0, 1.0"):
				
		if district_id is not None:
			dist_id = int(district_id)
			d = int(depth)
			
			if previous_id is not None:
				prev_id = int(previous_id)
			else:
				prev_id = dist_id
				
			# Parse comma-separated list of four floats encoded as a string
			try:
				a00, a01, a10, a11 = (float(r) for r in rold.split(','))
				R_old = [[a00, a01], [a10, a11]]
			except:
				R_old = [[1.0, 0.0], [0.0, 1.0]]
			
			return self.path.GetDistrictDeepPathLocalRotatedCoordInfo_JSON(dist_id, prev_id, d, R_old)

	# ------------
	# Ellipses
	
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def districtellipses(self, district_id = None, type = 'space', previous_id = None, rold = "1.0, 0.0, 0.0, 1.0"):
		
		if district_id is not None:
			dist_id = int(district_id)
			
			if previous_id is not None:
				prev_id = int(previous_id)
			else:
				prev_id = dist_id
				
			# Parse comma-separated list of four floats encoded as a string
			try:
				a00, a01, a10, a11 = (float(r) for r in rold.split(','))
				R_old = [[a00, a01], [a10, a11]]
			except:
				R_old = [[1.0, 0.0], [0.0, 1.0]]
			
			if type == 'diffusion':
				return self.path.GetDistrictDiffusionRotatedEllipses_JSON(dist_id, prev_id, R_old)
			else:
				return self.path.GetDistrictLocalRotatedEllipses_JSON(dist_id, prev_id, R_old)

# ------------
cherrypy.config.update({
		# 'tools.gzip.on' : True,
		'server.socket_port': 9000, 
		# 'server.socket_host':'127.0.0.1'
		'server.socket_host':'152.3.61.80'
		})
cherrypy.quickstart(PathServer())
