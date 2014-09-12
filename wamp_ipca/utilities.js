// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };
    
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
        $.publish("/data_info/loaded", g.root_node_id);
    }
    
    // DataInfo
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
    
    function useUpdatedScalars(json) {
        // TODO: This doesn't work for histogram yet...
        // This is scalar data on the tree, coming in as a dict/obj
        g.scalardata = json.labels;
        g.scalardomain = json.domain;
        
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
                g.cScale.domain([0, 1]).range(["red","blue"])
                        .interpolate(d3.interpolateLab);
        }
        
        $.publish("/scalars/updated");
    }
	
	// Scalars
	ut.getScalarsFromServer = function() {
        
        if (g.comm_method == 'http') {
		    d3.json('/' + g.dataset + "/scalars?name=" + g.scalars_name + "&aggregation=" + g.scalars_aggregator, useUpdatedScalars);
		} else {
		    g.session.call('test.ipca.scalars', [], {dataset: g.dataset, 
		                                               name: g.scalars_name, 
		                                               aggregation: g.scalars_aggregator}).then( useUpdatedScalars ); 
		}
	};

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
