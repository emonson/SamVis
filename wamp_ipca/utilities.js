// --------------------------
// Utility functions

var UTILITIES = (function(d3, $, g){

	var ut = { version: '0.0.1' };

	ut.getScalarsFromServer = function(s_obj) {

		// d3.json('/' + g.dataset + "/scalars?name=" + g.scalars_name + "&aggregation=" + g.scalars_aggregator, function(json) {
		
		g.session.call('test.ipca.scalars', [], {name: g.scalars_name, aggregation: g.scalars_aggregator}).then( function(json) {
			
			// DEBUG
			console.log(json);
			
			// TODO: This doesn't work for histogram yet...
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
		});     // d3.json
	};

	return ut;

}(d3, jQuery, GLOBALS));

// END UTILITY FUNCTIONS
// --------------------------
