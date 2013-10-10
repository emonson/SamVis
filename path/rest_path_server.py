import cherrypy
import simplejson
from path_obj import PathObj
import os
import glob

class ResourceIndex(object):

    def __init__(self, content):
        self.content = content

    exposed = True

    def GET(self):
        return self.to_html()

    def to_html(self):
        html_item = lambda (name,value): '<div><a href="{value}">{name}</a></div>'.format(**vars())
        items = map(html_item, self.content.items())
        items = ''.join(items)
        return '<html>{items}</html>'.format(**vars())


class PathServer:
	
	# _cp_config = {'tools.gzip.on': True}
	
	def __init__(self, path):
		
		# self.path = PathObj('data/json_20130601')
		# self.path = PathObj('data/json_20130813')
		# self.path = PathObj('data/json_20130913_ex3d')
		# self.path = PathObj('data/json_20130926_imgex')
		self.path = PathObj(path)
		
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
				
			R_old = self.parse_rold(rold)
			
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
				
			R_old = self.parse_rold(rold)
			
			if type == 'diffusion':
				return self.path.GetDistrictDiffusionRotatedEllipses_JSON(dist_id, prev_id, R_old)
			else:
				return self.path.GetDistrictLocalRotatedEllipses_JSON(dist_id, prev_id, R_old)

	# ------------
	# Query
	
	@cherrypy.expose
	@cherrypy.tools.gzip()
	def pathtimedistrict(self, time=None):
		
		if time is not None:
			t = int(time)
			
			# Get district ID for path at a specified time
			return self.path.GetDistrictFromPathTime_JSON(t)

	# ------------
	# Utility
	
	def parse_rold(self, rold):
		
		# Parse comma-separated list of four floats encoded as a string
		try:
			a00, a01, a10, a11 = (float(r) for r in rold.split(','))
			R_old = [[a00, a01], [a10, a11]]
		except:
			R_old = [[1.0, 0.0], [0.0, 1.0]]
		
		return R_old
			
# ------------

class Root(object):
    pass

root = Root()
data_dir = 'data'

# Go through data directory and add methods to root for each data set
data_paths = [xx for xx in glob.glob(os.path.join(data_dir,'*')) if os.path.isdir(xx)]
data_dirnames = [os.path.basename(xx) for xx in data_paths]

# This adds the methods for each data directory
for ii,name in enumerate(data_dirnames):
	print name, data_paths[ii]
	setattr(root, name, PathServer(data_paths[ii]))

# add the resource index, which will list links to the data sets
root.resource_index = ResourceIndex(dict(zip(data_dirnames,data_paths)))

# Start up server
server_filename = '../server_example.json'
server_opts = simplejson.loads(open(server_filename).read())

conf = {
    'global': {
        'server.socket_host': server_opts['server_name'],
        'server.socket_port': server_opts['path_port'],
    },
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    }
}

cherrypy.quickstart(root, '/', conf)