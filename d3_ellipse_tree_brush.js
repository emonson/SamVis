var site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/"
// var site_root = "http://localhost/~emonson/Sam/"

// Arrays to hold all nodes scalar data
var scalardata = [];
var scalars_name = 'labels';
// Convenience tree data structures -- may not always need these...
var scales_by_id = [];
var ids_by_scale = {};
var visible_ellipse_ids = [];
var background_ellipse_ids = [];
var all_ellipse_data = [];
var all_ellipse_bounds = [];

var selectColor = "gold";
var ellipseStrokeWidth = 2;
var cScale = d3.scale.linear()
						.domain([0.0, 0.5, 1.0])
						.range(["#CA0020", "#999999", "#0571B0"]);

// - - - - - - - - - - - - - - - -
// Ellipse plot variables
var w_el = 400;
var h_el = 400;
var padding = 40;
// Initial selection. node_id sets the scale for now...
var node_id = 50;
var basis_id = 0;

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
			.attr("height", h_el);

// Ellipse plot axes
svg.append("g")
	.attr("class", "x axis")
	.attr("transform", "translate(0," + (h_el - padding) + ")")
	.call(xAxis);
svg.append("g")
	.attr("class", "y axis")
	.attr("transform", "translate(" + padding + ",0)")
	.call(yAxis);

// - - - - - - - - - - - - - - - -
// Icicle view variables
var w_ice = 500;
var h_ice = 300;
var x_ice = d3.scale.linear().range([0, w_ice]);
var y_ice = d3.scale.linear().range([0, h_ice]);
var color = d3.scale.category20c();
var brush_on = false;

// Icicle view tree layout calculation function
// JSON object member keys have simplified names to keep file and transfer size down.
// d.c = d.children
// d.v = d.value (number of leaf members / node)
// d.i = d.id
var partition_ice = d3.layout.partition()
		.children(function(d){ return d.c ? d.c : null;})
		.value(function(d){return d.v ? d.v : null;});

// Icicle view SVG element
var vis = d3.select("#tree").append("svg:svg")
		.attr("width", w_ice)
		.attr("height", h_ice)
		.on("mouseout", function() {d3.select("#nodeinfo").text("id = , scale = ")});


// - - - - - - - - - - - - - - - -
// Utility functions

var getScalarsFromServer = function(s_name) {
	d3.json(site_root + "treescalarsfacade.php?name=" + s_name, function(json) {
	
		scalardata = json;
	
		// Update colors in both visualizations when this returns
		svg.selectAll("ellipse")
				.attr("stroke", function(d,i){return cScale(scalardata[d[5]]);});
	
		vis.selectAll("rect")
				.attr("fill", function(d) { return cScale(scalardata[d.i]); });
	});
};

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

// Get all projected ellipses from the server for now rather than just the displayed ones
var getReprojectedEllipsesFromServer = function() {

	d3.json(site_root + "treeallellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

		// NOTE: Domains and bounds are being set to _all_ ellipses...
		
		// Update scale domains
		// data = [[X, Y, RX, RY, Phi, i], ...]
		all_ellipse_data = json.data;
		// bounds = [[Xmin, Xmax], [Ymin, Ymax]]
		all_ellipse_bounds = json.bounds;
		xScale.domain(all_ellipse_bounds[0]);
		yScale.domain(all_ellipse_bounds[1]);
		xrScale.domain([0, all_ellipse_bounds[0][1]-all_ellipse_bounds[0][0]]);
		yrScale.domain([0, all_ellipse_bounds[1][1]-all_ellipse_bounds[1][0]]);

		// NOTE: Updating ellipses here - may not always be the right thing to do...
		updateEllipses();
	});
};

var updateEllipses = function() {

		// Regenerate visible ellipse data from two lists of ids
		// For now tag on extra flag identifying class of ellipse (background, visible)
		var visible_ellipse_data = [];
		for (var ii = 0; ii < background_ellipse_ids.length; ii++) {
			var tmp_data = all_ellipse_data[background_ellipse_ids[ii]].slice();
			tmp_data.push('background');
			visible_ellipse_data.push(tmp_data);
		}
		for (var ii = 0; ii < visible_ellipse_ids.length; ii++) {
			var tmp_data = all_ellipse_data[visible_ellipse_ids[ii]].slice();
			tmp_data.push('visible');
			visible_ellipse_data.push(tmp_data);
		}

		// Update the ellipses
		var els = svg.selectAll("ellipse")
				.data(visible_ellipse_data, function(d){return d[5];});
		
		els.transition()
				.duration(500)		
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("stroke", function(d,i){return d[5] == node_id ? selectColor : cScale(scalardata[d[5]]);})
				.attr("stroke-width", function(d) {
						// Selected overrides background
						if (d[5] == node_id) { return ellipseStrokeWidth; }
						if (d[6] == 'background') {return 0;}
						else {return ellipseStrokeWidth;}
				 })
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });

		
		els.enter()
				.append("ellipse")
				.attr("id", function(d) {return "e_" + d[5];})
				.attr("stroke", function(d) {return d[5] == node_id ? selectColor : cScale(scalardata[d[5]]);})
				.attr("stroke-width", function(d) {
						// Selected overrides background
						if (d[5] == node_id) { return ellipseStrokeWidth; }
						if (d[6] == 'background') {return 0;}
						else {return ellipseStrokeWidth;}
				 })
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); })
				.on("click", clickfctn)
				.on("dblclick", dblclickfctn);
		
		els.exit()
				.remove();
		
		updateAxes();
};

// Ellipse click function (update projection basis)
var clickfctn = function() {
				
	var that = this;
	d3.select(this)
			.attr("stroke", selectColor);
			
	node_id = that.__data__[5];
	highlightEllipse(node_id);
	highlightRect(node_id);
	
	// Only change projection basis if pressing alt
	if (d3.event && d3.event.altKey) {
		basis_id = node_id;
		getReprojectedEllipsesFromServer();
	}
};

// Ellipse double-click function (reset projection basis)
var dblclickfctn = function() {
				
	basis_id = 0;
// 	highlightEllipse(0);
// 	highlightRect(0);
	getReprojectedEllipsesFromServer();
};

// ============
// Icicle view

var zoomIcicleView = function(sel_id) {
		
	// Change icicle zoom
	vis.selectAll("rect")
		.transition()
			.duration(750)
			.attr("x", function(d) { return x_ice(d.x); })
			.attr("y", function(d) { return y_ice(d.y); })
			.attr("width", function(d) { return x_ice(d.x + d.dx) - x_ice(d.x); })
			.attr("height", function(d) { return y_ice(d.y + d.dy) - y_ice(d.y); });
};

var highlightEllipse = function(sel_id) {

	// Unhighlight previously selected ellipse
	d3.select(".el_selected")
		.attr("stroke", function(d,i){return cScale(scalardata[d[5]]);})
		.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : ellipseStrokeWidth;})
		.classed("el_selected", false);

	// Highlight ellipse corresponding to current rect selection
	d3.select("#e_" + sel_id)
		.attr("stroke", function(d,i){return selectColor;})
		.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : ellipseStrokeWidth;})
		.classed("el_selected", true);
};

var highlightRect = function(sel_id) {

	// Unhighlight previously selected icicle rectangle
	d3.select(".r_selected")
		.classed("r_selected", false);

	// Highlight currently clicked rectangle
	d3.select("#r_" + sel_id)
		.classed('r_selected', true);			
};

var rect_click = function(d) {
	
	// NOTE: If click on a different scale rectangle while scatterplot is
	//   projected into a non-scale-0 basis, change to that different scale
	//   representation in the scatterplot, but basis projected into is now not
	//   one that is present in the ellipses on the plot...
	
	// TODO: Make separate colors for highlight and projection basis...
	
	// Only update icicle zoom if alt has been selected
	if (d3.event && d3.event.altKey) {
		x_ice.domain([d.x, d.x + d.dx]);
		y_ice.domain([d.y, 1]).range([d.y ? 20 : 0, h_ice]);
		
		zoomIcicleView(d.i);
	}
	
	// Only transition ellipses if new rect has been selected
	if (node_id != d.i) {
		var new_scale = scales_by_id[node_id] == scales_by_id[d.i] ? false : true;
		node_id = d.i;
		highlightRect(node_id);
		
		// Making a copy of the array with concat(), slice() would also work...
		if (new_scale) {
			visible_ellipse_ids = [0].concat(ids_by_scale[scales_by_id[node_id]]);
			updateEllipses();
		}
		highlightEllipse(node_id);
	}
};

var rect_dblclick = function(d) {
	
	// Reset scales to original domain and y range
	x_ice.domain([0, 1]);
	y_ice.domain([0, 1]).range([0, h_ice]);
	
	zoomIcicleView(0);
};

var rect_hover = function(d) {

	d3.select("#nodeinfo")
		.text("id = " + d.i + ", scale = " + d.s);
};

var brush = d3.svg.brush()
	.x(x_ice)
	.y(y_ice)
	.on("brush", brushmove)
	.on("brushend", brushend);

var thereIsNoOverlap = function(a,b) {
	// [[ax1,ay1],[ax2,ay2]] = a
	// [[bx1,by1],[bx2,by2]] = b
	// return((ax2<bx1) or (ax1>bx2) or (ay2<by1) or (ay1>by2))
	return ((a[1][0] < b[0][0]) | (a[0][0] > b[1][0]) | (a[1][1] < b[0][1]) | (a[0][1] > b[1][1]));
};

// Brushing: Gray out non-brushed rectangles and generate list of ellipse ids to show
function brushmove(p) {

	var e = brush.extent();
	var no_overlap = true;
	// Saving all scale nodes and 0 from selection mode
	background_ellipse_ids = [0].concat(ids_by_scale[scales_by_id[node_id]]);
	visible_ellipse_ids = [];
	
	d3.selectAll("rect").classed("hidden", function(d) {
		dd = [[d.x, d.y], [d.x + d.dx, d.y + d.dy]];
		no_overlap = thereIsNoOverlap(dd,e);
		// Update global visible_ellipse_ids array
		// NOTE: There are some rect elements that aren't tree nodes, trying to filter...
		if(!no_overlap && d.hasOwnProperty('i')) {
			// Make sure item not already in list from selection or 0 node
			if (visible_ellipse_ids.indexOf(d.i) < 0) {
				visible_ellipse_ids.push(d.i);
			}
		}
		return no_overlap;
	});
	updateEllipses();
}

// If the brush is empty, select all circles.
function brushend() {
	if (brush.empty()) d3.selectAll("rect").classed("hidden", false);
}

function setIceInstructionsToBrush() {
		d3.select("#ice_instructions")
			.text("Brush Mode: Draw a rectangle on the icicle view to highlight and brush nodes");
		brush_on = true;
}

function setIceInstructionsToSelect() {
		d3.select("#ice_instructions")
			.text("Click-Select Mode: Click on a node to change ellipse plot scale. \
						 Alt-click to zoom in on a node's subtree. \
						 Double-click to reset zoom.");
}

var init_icicle_view = function() {
	
	d3.json(site_root + "treedatafacade.php", function(json) {
	// d3.json("http://localhost/~emonson/Sam/treedatafacade.php", function(json) {
		
		// TODO: Don't need to send 's' as an attribute, partition function calculates
		//   attribute 'depth'...
		
		// Before building tree, compile convenience data structures
		var ice_partition = partition_ice(json);
		scales_by_id = new Array(ice_partition.length);
		for (var ii = 0; ii < ice_partition.length; ii++) {
			var node = ice_partition[ii];
			var scale = node.s
			scales_by_id[node.i] = scale;
			if (!ids_by_scale.hasOwnProperty(scale)) {
				ids_by_scale[scale] = [];
			}
			ids_by_scale[scale].push(node.i);
		}
		
		// Build tree
		var rect = vis.selectAll("rect")
				.data(ice_partition)
			.enter().append("svg:rect")
				.attr("id", function(d) {return "r_" + d.i;})
				.classed("r_selected", function(d){return d.i == node_id;})
				.attr("x", function(d) { return x_ice(d.x); })
				.attr("y", function(d) { return y_ice(d.y); })
				.attr("width", function(d) { return x_ice(d.dx); })
				.attr("height", function(d) { return y_ice(d.dy); })
				.attr("fill", function(d) { return cScale(scalardata[d.i]); })
				.on("click", rect_click)
				.on("dblclick", rect_dblclick)
				.on("mouseover", rect_hover);
		
		if (brush_on) { 
			setIceInstructionsToBrush();
		}
		else {
			setIceInstructionsToSelect();
		}

		// Toggle icicle brushing
		d3.select("body")
			.on("keydown", function() {
				if (d3.event && String.fromCharCode(d3.event.keyCode) == "B") {
					if (brush_on) {
						// Turn off brush
						// NOTE: Not calling brush.empty() so keep brush shape for now...
						d3.selectAll(".brush").remove();
						// Restore colormap to icicle rectangles
						d3.selectAll("rect").classed("hidden", false);
						setIceInstructionsToSelect();
						background_ellipse_ids = [];
						visible_ellipse_ids = [0].concat(ids_by_scale[scales_by_id[node_id]]);
						updateEllipses();
						brush_on = false;
					}
					else {
						// Add brushing to icicle view
						// NOTE: If a brush already exists, colors won't reset around brush until moved
						// TODO: Do a pass through movebrush routine after switching...
						vis.append("g")
							.attr("class", "brush")
							.call(brush);
						setIceInstructionsToBrush();
						brush_on = true;
					}
				}
			});
	});
};

// ===============
// MAIN

// Do initial scalars retrieval
getScalarsFromServer(scalars_name);

// Initialize icicle view
// NOTE: This is where scales_by_id and ids_by_scale get created
init_icicle_view();

// Grab the initial ellipses
getReprojectedEllipsesFromServer();
