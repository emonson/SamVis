// --------------------------
// Utility functions

var UTILITIES = (function(d3, g, I, E){

	var ut = { version: '0.0.1' };

	ut.getScalarsFromServer = function(s_name) {
		// d3.json(site_root + "treescalarsfacade.php?name=" + s_name, function(json) {
		d3.json(g.data_proxy_root + "scalars?name=" + s_name, function(json) {
	
			g.scalardata = json;
			E.updateScalarData();
			I.updateScalarData();
		});
	};

	return ut;

}(d3, globals, ICICLE, ELPLOT));

// END UTILITY FUNCTIONS
// --------------------------
