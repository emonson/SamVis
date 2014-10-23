// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };
    
    // -------------------------------------
    // Establish whether http or WS, and if latter, make connection
    
    ut.establish_connection = function() {
        // Since can't turn off retries on WS connection, default to http and try request
        $.ajax({
            url: "resource_index/datasets",
            async:false,
            dataType: "json",
            success: function(response) {
                console.log('http server present');
                g.comm_method = 'http';
                $.publish('/connection/open');
            },
            error: function(jqXHR, textStatus, errorThrown) {

                // WAMP / Websockets initialization
                g.session = null;

                // the URL of the WAMP Router (e.g. Crossbar.io)
                //
                g.wsuri = "ws://" + g.server_conf.server_name + ":" + g.server_conf.ipca_ws_port;

                // connect to WAMP server
                // Would like to set retries to zero to switch to http if ws isn't working...
                g.connection = new autobahn.Connection({
                    url: g.wsuri,
                    max_retries: 1,
                    realm: 'realm1'
                });

                g.connection.onopen = function (new_session) {
                    console.log("connected to " + g.wsuri);
                    g.session = new_session;
                    g.comm_method = 'wamp';
                    $.publish('/connection/open');
                };

                g.connection.onclose = function (reason, details) {
                    console.log("connection gone", reason, details);
                    new_session = null;
                }

                g.connection.open();
            }
        });
    };

    // -------------------------------------
    // Callback function once have data_info
    
    function useUpdatedDataInfo(data) {
        g.data_info = data.data_info;
        g.centers_bounds = data.centers_bounds;
        g.bases_bounds = data.bases_bounds;
        g.scalar_names = data.scalar_names;
        if (!g.scalars_name && g.scalar_names.length > 0) {
            g.scalars_name = g.scalar_names[0];
        }
        g.root_node_id = data.root_node_id;
        // Start selection off at root
        g.node_id = g.root_node_id;
        g.has_embedding = data.has_embedding;
        if (g.has_embedding) {
            g.n_embedding_dims = data.n_embedding_dims;
        }
        $.publish("/data_info/loaded", g.root_node_id);
    }
    
    // Get DataInfo
    ut.get_data_info = function() {
        if (g.comm_method == 'http') {
            $.ajax({
                url:'/' + g.dataset + '/datainfo',
                async:false,
                dataType:'json',
                success:useUpdatedDataInfo
            });	
        } else {
            g.session.call("test.ipca.datainfo", [], {dataset:g.dataset}).then(useUpdatedDataInfo);
        }
    };
    
    // -------------------------------------
    // Callback function once have scalar names
    
    function useUpdatedScalars(json) {
        
        // Keep track of first time through for app timing
        var first_time = false;
        if ($.isEmptyObject(g.scalardata)) {
            first_time = true;
        }
        
        // TODO: This doesn't work for histogram yet...
        // This is scalar data on the tree, coming in as a dict/obj
        g.scalardata = json.labels;
        g.scalardomain = json.domain;
        g.scalars_aggregator = json.aggregator;
        
        // Use different color maps depending on aggregator function
        switch(g.scalars_aggregator) {
        
            case 'mean':
            
                var sr_mean = (g.scalardomain[0] + g.scalardomain[1]) / 2.0;
                g.cScale = d3.scale.linear()
                    .domain([g.scalardomain[0], sr_mean, g.scalardomain[1]])
                        .range(["#0571B0", "#999999", "#CA0020"]);
                break;
                
            case 'mode':
            
                if (g.scalardomain.length <= 10) {
                 g.cScale = d3.scale.category10()
                     .domain(g.scalardomain);
                } else {
                 g.cScale = d3.scale.category20()
                     .domain(g.scalardomain);
                }
                break;
            
            case 'entropy':
            
                g.cScale = d3.scale.linear()
                    .domain(g.scalardomain)
                        .range(["#333", "#C44"])
                        .interpolate(d3.interpolateHsl);;
                break;
            
            default:
            
                // interpolateLab, Hsl, Hcl, Rgb
                g.cScale.domain(g.scalardomain).range(["red","blue"])
                        .interpolate(d3.interpolateLab);
        }
        
        if (first_time) {
            $.publish("/scalars/initialized");
        } else {
            $.publish("/scalars/updated");
        }
    }
	
	// Scalars
	ut.getScalarsFromServer = function() {
        
        if (g.comm_method == 'http') {
		    d3.json('/' + g.dataset + "/nodescalars?name=" + g.scalars_name, useUpdatedScalars);
		} else {
		    g.session.call('test.ipca.nodescalars', [], {dataset: g.dataset, 
		                                               name: g.scalars_name}).then( useUpdatedScalars ); 
		}
	};

    // -------------------------------------
    // Callback function once have dataset names
    
    function useDatasetNames(res) {
        g.dataset_names = res;
        $.publish('/dataset_names/acquired');
    }
    
    // Get dataset names
    ut.get_dataset_names = function() {
        if (g.comm_method == 'http') {
            // Grabbing possible data set names (not async)
            $.ajax({
                url:'/resource_index/datasets',
                async:false,
                dataType:'json',
                success: useDatasetNames
            });	
        } else {
            // WAMP dataset names
            // TODO: Update some dataset combo box upon return...
            g.session.call("test.ipca.datasets").then(useDatasetNames);
        }
    };
    
	return ut;

}(d3, jQuery, GLOBALS));

// END UTILITY FUNCTIONS
// --------------------------
