var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
	
	 // Load server config to check ports & methods
    $.ajax({
        url: "server_conf.json",
		async:false,
        dataType: "json",
        success: function(response) {
            globals.server_conf = response;
        }
    });
	
	// After main.js is loaded, going to test whether this has a value already,
	// and if so, fire off /connection/open since probably fired already...
	globals.comm_method = false;
	// If WS session established, will use these variables
	globals.session = null;
	globals.wsuri = null;
	globals.connection = null;
	
    // Data set name passed in URI
    globals.uri = parseUri(location.toString());
    globals.dataset = globals.uri.queryKey.data;
    // Filled in later from server
    globals.dataset_names = [];

    // Scalars name passed in URI
    globals.scalars_name = globals.uri.queryKey.scalars;
	// Obj/dict to hold a set of scalar data to color the nodes by
	globals.scalardata = {};
    globals.scalardomain = [0,1];
    
    // Convenience tree data structures -- may not always need these...
    globals.scales_by_id = [];
    globals.ids_by_scale = {};
    globals.max_scale = -1;

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
    
    // Embedding scatterplot
    globals.has_embedding = false;
    globals.n_embedding_dims = -1;
    globals.embedding = [];
    globals.xdim = 1;
    globals.ydim = 2;
    
    return globals;

}(jQuery));

