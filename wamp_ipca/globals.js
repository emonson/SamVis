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
	
    // Since can't turn off retries on WS connection, default to http and try request
    $.ajax({
        url: "resource_index/datasets",
		async:false,
        dataType: "json",
        success: function(response) {
            console.log('http server present');
            globals.comm_method = 'http';
            $.publish('/connection/open');
        },
        error: function(jqXHR, textStatus, errorThrown) {

            // WAMP / Websockets initialization
            globals.session = null;

            // the URL of the WAMP Router (e.g. Crossbar.io)
            //
            globals.wsuri = "ws://" + globals.server_conf.server_name + ":" + globals.server_conf.ipca_ws_port;

            // connect to WAMP server
            // Would like to set retries to zero to switch to http if ws isn't working...
            globals.connection = new autobahn.Connection({
                url: globals.wsuri,
                max_retries: 1,
                realm: 'realm1'
            });

            globals.connection.onopen = function (new_session) {
                console.log("connected to " + globals.wsuri);
                globals.session = new_session;
                globals.comm_method = 'wamp';
                $.publish('/connection/open');
            };

            globals.connection.onclose = function (reason, details) {
                console.log("connection gone", reason, details);
                new_session = null;
            }

            globals.connection.open();
        }
    });
	 
    // NOTE: only allowing dataset passed in query string
    // TODO: Handle better no dataset passed...
    globals.uri = parseUri(location.toString());
    globals.dataset = globals.uri.queryKey.data;
    // Filled in later from server
    globals.dataset_names = [];

	// Obj/dict to hold all nodes scalar data
	globals.scalardata = {};
    globals.scalardomain = [0,1];
    // NOTE: not testing for queryKey in scalar_names array...
    globals.scalars_name = globals.uri.queryKey.scalars;
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

