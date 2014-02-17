// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };

	ut.getScalarsFromServer = function(s_obj) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/scalars?name=" + g.scalars_name + "&aggregation=" + g.scalars_aggregator, function(json) {
			
			// TODO: This doesn't work for histogram yet...
			g.scalardata = json.labels;
			g.scalarrange = json.range;
			// TODO: Need to find a better way to deal with specifying a multi-color ramp...
			var mean = (g.scalarrange[0] + g.scalarrange[1]) / 2.0;
			g.cScale.domain([g.scalarrange[0], mean, g.scalarrange[1]]);
			
			$.publish("/scalars/updated");
		});
	};

	return ut;

}(d3, jQuery, GLOBALS));

// END UTILITY FUNCTIONS
// --------------------------
