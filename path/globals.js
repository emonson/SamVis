var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
		
	// Make it easier to swtich the server config when switching between machines
	$.ajax({
		url:'../server_example.json',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.data_proxy_root = "http://" + data.server_name + "/remote" + data.path_port;
		}
	});	
	
	
	// Both ends of time filter slider set to -1 until initialized with real values
	globals.time_width = -1;
	globals.time_center = -1;
	globals.time_range = [-1, -1];
	
	globals.path_depth = 2;

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

}(jQuery));

