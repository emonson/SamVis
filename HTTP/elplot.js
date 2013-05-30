// --------------------------
// Ellipse plot variables

var ELPLOT = (function(d3, g, B){

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
					B.getBasisImagesFromServer(globals.node_id);
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
		if (d[5] == globals.node_id) { return globals.selectColor; }
		else { return globals.cScale(globals.scalardata[d[5]]);}
	};

	var setEllipseStrokeWidth = function(d,i) {
	
		// Calculate wrt current selection scale
		var main_selection_scale = globals.scales_by_id[globals.node_id];
		var this_scale = globals.scales_by_id[d[5]];
		var width = globals.ellipseStrokeWidth;
		if (this_scale > main_selection_scale) { width = width / 2.0; }
		if (this_scale < main_selection_scale) { width = width * 1.5; }
	
		// Selected ellipse coloring (stroke) overrides background (no stroke)
		if (d[5] == globals.node_id) { return width; }
		if (d[6] == 'background') {return 0;}
		else {return width;}
	};

	var setEllipseStrokeOpacity = function(d,i) {
	
		// Calculate wrt current selection scale
		var main_selection_scale = globals.scales_by_id[globals.node_id];
		var this_scale = globals.scales_by_id[d[5]];
		var op = 1.0;
		if (this_scale > main_selection_scale) { op = 0.75; }
		if (this_scale < main_selection_scale) { op = 0.5; }
	
		// Selected ellipse coloring (stroke) overrides background (no stroke)
		if (d[5] == globals.node_id) { return op; }
		if (d[6] == 'background') {return 0;}
		else {return op;}
	};

	var hoverfctn = function(d) {
		B.getBasisImagesFromServer(d[5]);
	};

	// Ellipse click function (update projection basis)
	var clickfctn = function() {
				
		var that = this;

		// Only change projection basis if pressing alt
		if (d3.event && d3.event.altKey) {
			globals.node_id = that.__data__[5];
			el.getContextEllipsesFromServer();
		}
	
		else {
			d3.select(this)
					.attr("stroke", globals.selectColor);
			
			globals.node_id = that.__data__[5];
			el.highlightSelectedEllipse(globals.node_id);
			// TODO: global...
			ICICLE.highlightSelectedRect(globals.node_id);
			B.getBasisImagesFromServer(globals.node_id);
			el.getContextEllipsesFromServer();
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
		for (var ii = 0; ii < globals.background_ellipse_data.length; ii++) {
			var tmp_data = globals.background_ellipse_data[ii].slice();
			tmp_data.push('background');
			visible_ellipse_data.push(tmp_data);
		}
		for (var ii = 0; ii < globals.foreground_ellipse_data.length; ii++) {
			var tmp_data = globals.foreground_ellipse_data[ii].slice();
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
	
		updateAxes();
	};

	// Get all projected ellipses from the server for now rather than just the displayed ones
	el.getContextEllipsesFromServer = function() {

		d3.json(globals.data_proxy_root + "contextellipses?id=" + globals.node_id + "&bkgdscale=" + globals.bkgd_scale, function(json) {

			// Flag for keeping track of whether this is the first selection
			var first_selection = (globals.foreground_ellipse_data.length == 0);
		
			// Update scale domains
			// data = [[X, Y, RX, RY, Phi, i], ...]
			globals.foreground_ellipse_data = json.foreground;
			globals.background_ellipse_data = json.background;
			// bounds = [[Xmin, Xmax], [Ymin, Ymax]]
			globals.ellipse_bounds = json.bounds;
		
			xScale.domain(globals.ellipse_bounds[0]);
			yScale.domain(globals.ellipse_bounds[1]);
			xrScale.domain([0, globals.ellipse_bounds[0][1]-globals.ellipse_bounds[0][0]]);
			yrScale.domain([0, globals.ellipse_bounds[1][1]-globals.ellipse_bounds[1][0]]);

			// Updating ellipses
			if (first_selection) {
				el.updateEllipses(150);
			}
			else {
				el.updateEllipses(750);
			}
		});
	};

	el.highlightSelectedEllipse = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select(".el_selected")
			.attr("stroke", function(d,i){return globals.cScale(globals.scalardata[d[5]]);})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : globals.ellipseStrokeWidth;})
			.classed("el_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#e_" + sel_id)
			.attr("stroke", function(d,i){return globals.selectColor;})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : globals.ellipseStrokeWidth;})
			.classed("el_selected", true);
	};

	return el;

}(d3, globals, BASIS_IMS));

// END ELPLOT
// --------------------------
