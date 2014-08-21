var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
		
	// Grabbing possible data set names (not async)
	$.ajax({
		url:'/resource_index/datasets',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.dataset_names = data;
		}
	});	
	
	// Passing initial data set value through in parameters
	// Setting specific data set – default to first in list
	// TODO: handle no list!!
	globals.uri = parseUri(location.toString());
	globals.dataset = globals.uri.queryKey.data || globals.dataset_names[globals.dataset_names.length-1];

	// Grabbing data infomation (type, bounds, scalar names, etc) (not async)
	//  data_info.json MNIST example:
	// 	{
	// 		"original_data": {
	// 			"description": "MNIST handwritten digits subset of 1000 1s and 2s",
	// 			"url": "",
	// 			"dataset_type": "image",
	// 			"image_n_rows": 28,
	// 			"image_n_columns": 28,
	// 			"labels": {
	// 				"digit_id": {
	// 					"filename": "labels.data.hdr",
	// 					"variable_type": "categorical",
	// 					"data_type": "i",
	// 					"description": "integers 0 and 1 corresponding to actual handwritten digits 1 and 2",
	// 					"key": {
	// 						"0": "digit1",
	// 						"1": "digit2"
	// 					}
	// 				}
	// 			}
	// 		},
	// 		"full_tree": {
	// 			"filename": "tree.ipca"
	// 		}
	// 	}

	$.ajax({
		url:'/' + globals.dataset + '/datainfo',
		async:false,
		dataType:'json',
		success:function(data) {
			globals.data_info = data.data_info;
			globals.centers_bounds = data.centers_bounds;
			globals.bases_bounds = data.bases_bounds;
			globals.scalar_names = data.scalar_names;
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

	// Node basis center and axes data and ranges
	globals.center_data = [];
	globals.bases_data = [];
	globals.center_range = [];
	globals.bases_range = [];

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

