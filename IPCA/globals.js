var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
		
	// Make it easier to swtich the server config when switching between machines (not async)
	$.ajax({
		url:'../server_conf.json',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.data_proxy_root = "http://" + data.server_name + "/remote" + data.ipca_port;
		}
	});	
	
	// Grabbing possible data set names (not async)
	$.ajax({
		url:globals.data_proxy_root + '/resource_index/datasets',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.dataset_names = data;
		}
	});	
	
	// Passing initial data set value through in parameters. default to first in list
	// TODO: handle no list!!
	globals.uri = parseUri(location.toString());
	globals.dataset = globals.uri.queryKey.data || globals.dataset_names[globals.dataset_names.length-1];

	// Grabbing possible scalars names (not async)
	$.ajax({
		url:globals.data_proxy_root + '/' + globals.dataset + '/scalarnames',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.scalar_names = data;
		}
	});	
	
	// Arrays to hold all nodes scalar data
	globals.scalardata = [];
	globals.scalardomain = [0,1];
	// NOTE: not testing for queryKey in scalar_names array...
	globals.scalars_name = globals.uri.queryKey.scalars || (globals.scalar_names[0] || "");
	globals.scalar_aggregators = ["mean", "mode","entropy"];
	globals.scalars_aggregator = globals.scalar_aggregators[0];
	// Convenience tree data structures -- may not always need these...
	globals.scales_by_id = [];
	globals.ids_by_scale = {};

	globals.visible_ellipse_data = [];
	globals.foreground_ellipse_data = [];
	globals.background_ellipse_data = [];
	globals.ellipse_bounds = [];

	globals.ellipse_center_data = [];
	globals.ellipse_bases_data = [];
	globals.ellipse_center_range = [];
	globals.ellipse_bases_range = [];

	// NOTE: These are both here for ellipses and in CSS for rectangles...
	globals.selectColor = "gold";
	globals.basisColor = "black";
	globals.ellipseStrokeWidth = 2;
	globals.cScale = d3.scale.linear()
							.domain([0.0, 1.0])
							.range(["#0571B0", "#CA0020"])
							.interpolate(d3.interpolateLab);

	// Initial selection. node_id sets the scale for now...
	globals.node_id = 0;
	globals.bkgd_scale = 1;

	return globals;

}(jQuery));

