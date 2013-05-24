// var site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/"
var site_root = "http://localhost/~emonson/Sam/"

// Arrays to hold all nodes scalar data
var scalardata = [];
var scalars_name = 'labels';
var selectColor = "gold";
var cScale = d3.scale.linear()
						.domain([0.0, 0.5, 1.0])
						.range(["#CA0020", "#999999", "#0571B0"]);

// Initial selection. node_id sets the scale for now...
var node_id = 50;
var basis_id = 0;

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
	
		// Update colors in visualizations when this returns
		vis.selectAll("rect")
				.attr("fill", function(d) { return cScale(scalardata[d.i]); });
	});
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

var highlightRect = function(sel_id) {

	// Unhighlight previously selected icicle rectangle
	d3.select(".r_selected")
		.classed("r_selected", false);

	// Highlight currently clicked rectangle
	d3.select("#r_" + sel_id)
		.classed('r_selected', true);			
};

var rect_click = function(d) {
	
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

function thereIsNotOverlap(a,b) {
	// [[ax1,ay1],[ax2,ay2]] = a
	// [[bx1,by1],[bx2,by2]] = b
	// return((ax2<bx1) or (ax1>bx2) or (ay2<by1) or (ay1>by2))
	return ((a[1][0] < b[0][0]) | (a[0][0] > b[1][0]) | (a[1][1] < b[0][1]) | (a[0][1] > b[1][1]));
}

// Highlight the selected circles.
function brushmove(p) {
	var e = brush.extent();
	d3.selectAll("rect").classed("hidden", function(d) {
		dd = [[d.x, d.y], [d.x + d.dx, d.y + d.dy]];
		return thereIsNotOverlap(dd,e);
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
				.on("mouseover", rect_hover);
		vis.call(brush);
	});
};

// ===============
// MAIN

// Do initial scalars retrieval
getScalarsFromServer(scalars_name);

// Initialize icicle view
init_icicle_view();
