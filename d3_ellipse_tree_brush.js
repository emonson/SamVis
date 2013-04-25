var site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/"
// var site_root = "http://localhost/~emonson/Sam/"

// Arrays to hold all nodes scalar data
var scalardata = [];
var scalars_name = 'labels';
var selectColor = "gold";
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

var updateEllipses = function() {

	d3.json(site_root + "treeellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

		// Update scale domains
		// data = [[X, Y, RX, RY, Phi, i], ...]
		dataset = json.data;
		// bounds = [[Xmin, Xmax], [Ymin, Ymax]]
		bounds = json.bounds;
		xScale.domain(bounds[0]);
		yScale.domain(bounds[1]);
		xrScale.domain([0, bounds[0][1]-bounds[0][0]]);
		yrScale.domain([0, bounds[1][1]-bounds[1][0]]);

		//Update all circles
		var els = svg.selectAll("ellipse")
				.data(dataset, function(d){return d[5];});
		
		els.transition()
				.duration(500)		
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });

		
		els.enter()
				.append("ellipse")
				.attr("id", function(d) {return "e_" + d[5];})
				.attr("stroke", function(d,i){return d[5] == node_id ? selectColor : cScale(scalardata[d[5]]);})
				.attr("fill-opacity", function(d,i){return 0.1;})
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.classed("el_selected", function(d){return d[5] == node_id;})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); })
				.on("click", clickfctn)
				.on("dblclick", dblclickfctn);
		
		els.exit()
				.remove();
		
		updateAxes();
	});
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
		updateEllipses();
	}
};

// Ellipse double-click function (reset projection basis)
var dblclickfctn = function() {
				
	basis_id = 0;
	highlightEllipse(0);
	highlightRect(0);
	updateEllipses();
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
		.attr("stroke", function(d) {return cScale(scalardata[d[5]]);})
		.classed("el_selected", false);

	// Highlight ellipse corresponding to current rect selection
	d3.select("#e_" + sel_id)
		.attr("stroke", selectColor)
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
		node_id = d.i;
		highlightRect(node_id);
		highlightEllipse(node_id);
		
		// HACK: Until fix scatterplot data extents, not letting update on scale 0
		if (node_id != 0) {
			updateEllipses();
		}
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

// Highlight the selected circles.
function brushmove(p) {
	var e = brush.extent();
	d3.selectAll("rect").classed("hidden", function(d) {
		dd = [[d.x, d.y], [d.x + d.dx, d.y + d.dy]];
		return thereIsNoOverlap(dd,e);
	});
}

// If the brush is empty, select all circles.
function brushend() {
	if (brush.empty()) d3.selectAll("rect").classed("hidden", false);
}

var init_icicle_view = function() {
	
	d3.json(site_root + "treedatafacade.php", function(json) {
	// d3.json("http://localhost/~emonson/Sam/treedatafacade.php", function(json) {
		var rect = vis.selectAll("rect")
				.data(partition_ice(json))
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
		
		vis.append("g")
			.attr("class", "brush")
			.call(brush);
		
		// NOTE: Remove brush with d3.selectAll(".brush").remove()
		// https://groups.google.com/forum/?fromgroups=#!topic/d3-js/YnjYAV3wcpU
		
	});
};

// ===============
// MAIN

// Do initial scalars retrieval
getScalarsFromServer(scalars_name);

// Grab the initial ellipses
updateEllipses();

// Initialize icicle view
init_icicle_view();
