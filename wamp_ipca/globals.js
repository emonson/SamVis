var GLOBALS = (function($){

	var globals = { version: '0.0.1' };
		
     // WAMP / Websockets initialization
     
     globals.session = null;

     // the URL of the WAMP Router (e.g. Crossbar.io)
     //
     if (document.location.origin == "file://") {
        globals.wsuri = "ws://localhost:9002";
     } else {
        globals.wsuri = "ws://" + document.location.hostname + ":9002";
     }

     // connect to WAMP server
     //
     globals.connection = new autobahn.Connection({
        url: globals.wsuri,
        realm: 'realm1'
     });

     globals.connection.onopen = function (new_session) {
        console.log("connected to " + globals.wsuri);
        globals.session = new_session;


        // WAMP dataset names
        // TODO: Need to wait for return!!
        globals.session.call("test.ipca.datasets").then(
            function (res) {
                globals.dataset_names = res;

                // Passing initial data set value through in parameters
                // Setting specific data set – default to first in list
                // TODO: handle no list!!
                globals.uri = parseUri(location.toString());
                globals.dataset = globals.uri.queryKey.data || globals.dataset_names[globals.dataset_names.length-1];

                // WAMP datainfo
                // TODO: Need to wait for return!!
                globals.session.call("test.ipca.datainfo").then(
                   function (data) {
                        globals.data_info = data.data_info;
                        globals.centers_bounds = data.centers_bounds;
                        globals.bases_bounds = data.bases_bounds;
                        globals.scalar_names = data.scalar_names;


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




                   }
                );


           }
        );
    



     };

     globals.connection.onclose = function (reason, details) {
        console.log("connection gone", reason, details);
        new_session = null;
     }

     globals.connection.open();


}(jQuery));

