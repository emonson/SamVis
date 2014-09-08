// --------------------------
// Ellipse plot variables

var ELPLOT = (function(d3, $, g){

	var el = { version: '0.0.1' };

	var w_el = 400;
	var h_el = 400;
	var padding = 40;

	// Ellipse plot scale functions with placeholder domains
	var xScale = d3.scale.linear().domain([0, 1]).range([padding, w_el - padding]);
	var yScale = d3.scale.linear().domain([0, 1]).range([h_el - padding, padding]);

	var xrScale = d3.scale.linear().domain([0, 1]).range([0, w_el - padding * 2]);
	var yrScale = d3.scale.linear().domain([0, 1]).range([0, h_el - padding * 2]);

	// Define X axis
	var xAxis = d3.svg.axis()
						.scale(xScale)
						.orient("bottom")
						.ticks(5);

	// Define Y axis
	var yAxis = d3.svg.axis()
						.scale(yScale)
						.orient("left")
						.ticks(5);

	// Ellipse plot SVG element
	var svg = d3.select("#graph")
				.append("svg")
				.attr("width", w_el)
				.attr("height", h_el)
				.on("mouseout", function() {
					$.publish("/elplot/mouseout", g.node_id);
				});

	// Ellipse plot axes
	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + (h_el - padding) + ")")
		.call(xAxis);
	svg.append("g")
		.attr("class", "y axis")
		.attr("transform", "translate(" + padding + ",0)")
		.call(yAxis);

	var updateAxes = function() {
		
		//Update X axis
		svg.select(".x.axis")
			.transition()
			.duration(500)
			.call(xAxis);

		//Update Y axis
		svg.select(".y.axis")
			.transition()
			.duration(500)
			.call(yAxis);
	};

	var setEllipseStrokeColor = function(d,i) {
		// Selected overrides basis
		if (d[5] == g.node_id) { return g.selectColor; }
		else { return g.cScale(g.scalardata[d[5]]);}
	};

	var setEllipseStrokeWidth = function(d,i) {
	    // NOTE: Scale 0 is root, then scale values go up as you go towards the leaves
	    
		// Calculate wrt current selection scale
		var main_selection_scale = g.scales_by_id[g.node_id];
		var this_scale = g.scales_by_id[d[5]];
		var width = g.ellipseStrokeWidth;
		if (this_scale > main_selection_scale) { width = width / 2.0; }
		if (this_scale < main_selection_scale) { width = width * 1.5; }
	
		// Selected ellipse coloring (stroke) overrides background (no stroke)
		if (d[5] == g.node_id) { return width; }
		if (d[6] == 'background') {return 0;}
		else {return width;}
	};

	var setEllipseStrokeOpacity = function(d,i) {
	
		// Calculate wrt current selection scale
		var main_selection_scale = g.scales_by_id[g.node_id];
		var this_scale = g.scales_by_id[d[5]];
		var op = 1.0;
		if (this_scale > main_selection_scale) { op = 0.75; }
		if (this_scale < main_selection_scale) { op = 0.5; }
	
		// Selected ellipse coloring (stroke) overrides background (no stroke)
		if (d[5] == g.node_id) { return op; }
		if (d[6] == 'background') {return 0;}
		else {return op;}
	};

	var hoverfctn = function(d) {
		$.publish("/elplot/ellipse_hover", d[5]);
	};

	// Ellipse click function (update projection basis)
	var clickfctn = function() {
				
		var that = this;

		// Not changing projection basis if pressing alt
		if (d3.event && d3.event.altKey) {
			$.publish("/elplot/ellipse_alt_click", that.__data__[5]);
		}
	
		else {
			d3.select(this)
					.attr("stroke", g.selectColor);
			
			g.node_id = that.__data__[5];
			$.publish("/elplot/ellipse_click", that.__data__[5]);
		}
	};
	
	el.updateScalarData = function() {
	
		// Update colors in both visualizations when this returns
		svg.selectAll("ellipse")
				.attr("stroke", function(d,i){return g.cScale(g.scalardata[d[5]]);});
		
	};

	el.updateEllipses = function(trans_dur) {
	
		// Default value for transition duration
		trans_dur = trans_dur || 500;
	
		// Regenerate visible ellipse data from two lists of ids
		// For now tag on extra flag identifying class of ellipse (background, visible)
		var visible_ellipse_data = [];
		for (var ii = 0; ii < g.background_ellipse_data.length; ii++) {
			var tmp_data = g.background_ellipse_data[ii].slice();
			tmp_data.push('background');
			visible_ellipse_data.push(tmp_data);
		}
		for (var ii = 0; ii < g.foreground_ellipse_data.length; ii++) {
			var tmp_data = g.foreground_ellipse_data[ii].slice();
			tmp_data.push('foreground');
			visible_ellipse_data.push(tmp_data);
		}
		
		// Update the ellipses
		// data = [[X, Y, RX, RY, Phi, i], ...]
		var els = svg.selectAll("ellipse")
				.data(visible_ellipse_data, function(d){return d[5];});
	
		els.transition()
			.duration(trans_dur)		
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("stroke", setEllipseStrokeColor )
				.attr("stroke-width", setEllipseStrokeWidth )
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });
	
		els.enter()
			.append("ellipse")
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); })
				.attr("stroke-opacity", 0.0)
				.attr("fill-opacity", 0)
					.on("click", clickfctn)
					.on("mouseover", hoverfctn)
			.transition()
			.delay(trans_dur/2.0)
			.duration(trans_dur)
				.attr("id", function(d) {return "e_" + d[5];})
				.attr("stroke", setEllipseStrokeColor )
				.attr("stroke-width", setEllipseStrokeWidth )
				.attr("stroke-opacity", setEllipseStrokeOpacity )
				.attr("fill-opacity", 0.1)
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });
	
		els.exit()
			.remove();
	
		// Reorder ellipses in the background by scale, higher scale later (drawn on top)
		els.sort(function(a,b) {
		    return g.scales_by_id[a[5]] - g.scales_by_id[b[5]];
		});
		
		updateAxes();
	};

	// Get projected ellipses from the server
	el.getContextEllipsesFromServer = function(node_id) {

		// d3.json('/' + g.dataset + "/contextellipses?id=" + g.node_id + "&bkgdscale=" + g.bkgd_scale, function(json) {
		
		g.session.call('test.ipca.contextellipses', [], {dataset: g.dataset, 
		                                               id: node_id, 
		                                               bkgdscale: g.bkgd_scale}).then( function(json) {	

			// Flag for keeping track of whether this is the first selection
			var first_selection = (g.foreground_ellipse_data.length == 0);
		
			// Update scale domains
			// data = [[X, Y, RX, RY, Phi, i], ...]
			g.foreground_ellipse_data = json.foreground;
			g.background_ellipse_data = json.background;
			// bounds = [[Xmin, Xmax], [Ymin, Ymax]]
			g.ellipse_bounds = json.bounds;
		
			xScale.domain(g.ellipse_bounds[0]);
			yScale.domain(g.ellipse_bounds[1]);
			xrScale.domain([0, g.ellipse_bounds[0][1]-g.ellipse_bounds[0][0]]);
			yrScale.domain([0, g.ellipse_bounds[1][1]-g.ellipse_bounds[1][0]]);

			// Updating ellipses
			if (first_selection) {
				$.publish("/ellipses/updated", 150);
			}
			else {
				$.publish("/ellipses/updated", 750);
			}
		});
	};

	el.highlightSelectedEllipse = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select(".el_selected")
			.attr("stroke", function(d,i){return g.cScale(g.scalardata[d[5]]);})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : g.ellipseStrokeWidth;})
			.classed("el_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#e_" + sel_id)
			.attr("stroke", function(d,i){return g.selectColor;})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : g.ellipseStrokeWidth;})
			.classed("el_selected", true);
	};

	return el;

}(d3, jQuery, GLOBALS));

// END ELPLOT
// --------------------------
