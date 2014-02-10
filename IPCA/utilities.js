// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };

	ut.getScalarsFromServer = function(s_name) {
		d3.json(g.data_proxy_root + '/' + g.dataset + "/scalars?name=" + s_name + "&aggregation=mode", function(json) {
	
			g.scalardata = json;
			$.publish("/scalars/updated");
		});
	};

	return ut;

}(d3, jQuery, GLOBALS));

// END UTILITY FUNCTIONS
// --------------------------