var GLOBALS = (function(){

	var globals = { version: '0.0.1' };

	globals.site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/path"
	globals.data_proxy_root = "http://emo2.trinity.duke.edu/remote/"
	// var site_root = "http://localhost/~emonson/Sam/"
	
	// Both ends of time filter slider set to -1 until initialized with real values
	globals.slider_values = [-1, -1];

	// Keeping value for type of ellipses to grab/display in globals for now
	globals.ellipse_type = 'space';
	globals.path_color = 'brown';
	
	// Path and ellipse data
	globals.path_pairs = {};
	globals.path_info = {};
	globals.ellipse_data = {};
	
	// Keep track of previous center, clicked destination center, and previous transformation matrix
	// (which eliminates rotation of coordinates bewteeen districts)
	globals.district_id = -1;
	globals.prev_district = -1;
	globals.R_old = "1.0, 0.0, 0.0, 1.0";

	return globals;

}());

