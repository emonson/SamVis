var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
		
	// Make it easier to swtich the server config when switching between machines
	$.ajax({
		url:'../server_conf.json',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.data_proxy_root = "http://" + data.server_name + "/remote" + data.ipca_port;
		}
	});	
	
	// Arrays to hold all nodes scalar data
	globals.scalardata = [];
	globals.scalars_name = 'labels';
	// Convenience tree data structures -- may not always need these...
	globals.scales_by_id = [];
	globals.ids_by_scale = {};

	globals.visible_ellipse_data = [];
	globals.foreground_ellipse_data = [];
	globals.background_ellipse_data = [];
	globals.ellipse_bounds = [];

	globals.ellipse_center_data = [];
	globals.ellipse_basis1_data = [];
	globals.ellipse_basis2_data = [];
	globals.ellipse_center_range = [];
	globals.ellipse_basis1_range = [];
	globals.ellipse_basis2_range = [];

	// NOTE: These are both here for ellipses and in CSS for rectangles...
	globals.selectColor = "gold";
	globals.basisColor = "black";
	globals.ellipseStrokeWidth = 2;
	globals.cScale = d3.scale.linear()
							.domain([0.0, 0.5, 1.0])
							.range(["#0571B0", "#999999", "#CA0020"]);

	// Initial selection. node_id sets the scale for now...
	globals.node_id = 0;
	globals.bkgd_scale = 1;

	return globals;

}(jQuery));

