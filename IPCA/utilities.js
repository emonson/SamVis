// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };

	ut.getScalarsFromServer = function(s_obj) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/scalars?name=" + g.scalars_name + "&aggregation=" + g.scalars_aggregator, function(json) {
	
			g.scalardata = json;
			console.log(json);
			$.publish("/scalars/updated");
		});
	};

	return ut;

}(d3, jQuery, GLOBALS));

// END UTILITY FUNCTIONS
// --------------------------
