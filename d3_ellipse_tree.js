var site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/"

//Width and height
var w_el = 400;
var h_el = 400;
var padding = 30;
var selectColor = "gold";
var node_id = 50;
var basis_id = 0;

// Arrays to hold ellipse data pulled from JSON
var dataset = [];
var scalardata = [];

// Icicle view variables
var w_ice = 500,
		h_ice = 300,
		x_ice = d3.scale.linear().range([0, w_ice]),
		y_ice = d3.scale.linear().range([0, h_ice]),
		color = d3.scale.category20c();


var partition_ice = d3.layout.partition()
		.children(function(d){ return d.c ? d.c : null;})
		.value(function(d){return d.v ? d.v : null;});

// Create ellipse graph scale functions with placeholder domains
var xScale = d3.scale.linear()
					 .domain([0, 1])
					 .range([padding, w_el - padding * 2]);

var yScale = d3.scale.linear()
					 .domain([0, 1])
					 .range([h_el - padding, padding]);

// NOTE: May not be right with rotation if unequal XY domains
var xrScale = d3.scale.linear()
					 .domain([0, 1])
					 .range([0, w_el]);

var yrScale = d3.scale.linear()
						.domain([0, 1])
						.range([0, h_el]);

var cScale = d3.scale.linear()
						.domain([0.0, 0.5, 1.0])
						.range(["#CA0020", "#999999", "#0571B0"]);

// ============
// ellipse graph

// Create ellipse graph SVG element
var svg = d3.select("#graph")
			.append("svg")
			.attr("width", w_el)
			.attr("height", h_el);

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

var scalars_name = 'labels';

// TODO: This is not a smart way to do it because with asynchronous function, could
//   move on and set up other vis elements before get this scalardata back!!!
d3.json(site_root + "treescalarsfacade.php?name=" + scalars_name, function(json) {
	
	scalardata = json;
	
});

// Grab initial ellipses
d3.json(site_root + "treeellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

	dataset = json;

	//Update scale domains
	var xRange = d3.extent(dataset, function(d) { return d[0]; })
	var yRange = d3.extent(dataset, function(d) { return d[1]; })
	xScale.domain(xRange);
	yScale.domain(yRange);
	xrScale.domain([0, xRange[1]-xRange[0]]);
	yrScale.domain([0, yRange[1]-yRange[0]]);

	//Create circles
	svg.selectAll("ellipse")
			.data(dataset)
		.enter()
			.append("ellipse")
			.attr("id", function(d) {return "e_" + d[5];})
			.attr("stroke", function(d,i){return cScale(scalardata[d[5]]);})
			.attr("fill-opacity", function(d,i){return 0.1;})
			.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
			.attr("rx", function(d) { return xrScale(d[2]); })
			.attr("ry", function(d) { return yrScale(d[3]); });

	//Create X axis
	svg.append("g")
		.attr("class", "x axis")
		.attr("transform", "translate(0," + (h_el - padding) + ")")
		.call(xAxis);

	//Create Y axis
	svg.append("g")
		.attr("class", "y axis")
		.attr("transform", "translate(" + padding + ",0)")
		.call(yAxis);

	d3.selectAll("ellipse")
		.on("click", clickfctn)
		.on("dblclick", dblclickfctn);
			
}); // JSON function end

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

var updateEllipses = function( basis_id, selectFunction ) {

	d3.json(site_root + "treeellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

		dataset = json;

		//Update scale domains
		var xRange = d3.extent(dataset, function(d) { return d[0]; })
		var yRange = d3.extent(dataset, function(d) { return d[1]; })
		xScale.domain(xRange);
		yScale.domain(yRange);
		xrScale.domain([0, xRange[1]-xRange[0]]);
		yrScale.domain([0, yRange[1]-yRange[0]]);

		// Update selected rectangle in icicle plot
		d3.select(".r_selected")
			.classed("r_selected", false);
		
		d3.select("#r_" + basis_id)
			.classed("r_selected", true);

		//Update all circles
		svg.selectAll("ellipse")
				.data(dataset)
				.classed("el_selected", function(d){return selectFunction(d,this);})
			.transition()
				.duration(500)		
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("stroke", function(d,i){return selectFunction(d,this) ? selectColor : cScale(scalardata[d[5]]);})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });

		updateAxes();

	});
};


// Ellipse click function (update projection basis)
var clickfctn = function() {
				
	var that = this;
	d3.select(this)
			.attr("stroke", selectColor);
			
	basis_id = that.__data__[5];

	var f = function(d, self) { return that === self; };
	
	updateEllipses(basis_id, f);

};

// Ellipse double-click function (reset projection basis)
var dblclickfctn = function() {
				
	d3.select('.el_selected')
		.attr("stroke", function(d) {return scalardata[d[5]];})
		.classed('el_selected', false);
		
	d3.select('#el_0')
		.attr("stroke", selectColor);
			
	basis_id = 0;

	var f = function(d) { return d[5] == 0; };
	
	updateEllipses(basis_id, f);

		
};



// ============
// Icicle view

var vis = d3.select("#tree").append("svg:svg")
		.attr("width", w_ice)
		.attr("height", h_ice)
		.on("mouseout", function() {d3.select("#nodeinfo").text("id = , scale = ")});

// JSON object member keys have simplified names to keep
// file and transfer size down.
// d.c = d.children
// d.v = d.value (number of leaf members / node)
// d.i = d.id

d3.json(site_root + "treedatafacade.php", function(json) {
// d3.json("http://localhost/~emonson/Sam/treedatafacade.php", function(json) {
	var rect = vis.selectAll("rect")
			.data(partition_ice(json))
		.enter().append("svg:rect")
			.attr("id", function(d) {return "r_" + d.i;})
			.attr("x", function(d) { return x_ice(d.x); })
			.attr("y", function(d) { return y_ice(d.y); })
			.attr("width", function(d) { return x_ice(d.dx); })
			.attr("height", function(d) { return y_ice(d.dy); })
			.attr("fill", function(d) { return cScale(scalardata[d.i]); })
			.on("click", rect_click)
			.on("dblclick", rect_dblclick)
			.on("mouseover", hover);

	function updateRect(sel_id) {
		
		// TODO: colordata only valid for current scale!!??
		d3.select(".el_selected")
			.attr("stroke", function(d) {return cScale(scalardata[d[5]]);})
			.classed("el_selected", false);

		d3.select("#e_" + sel_id)
			.attr("stroke", selectColor)
			.classed("el_selected", true);

		rect.transition()
			.duration(750)
			.attr("x", function(d) { return x_ice(d.x); })
			.attr("y", function(d) { return y_ice(d.y); })
			.attr("width", function(d) { return x_ice(d.x + d.dx) - x_ice(d.x); })
			.attr("height", function(d) { return y_ice(d.y + d.dy) - y_ice(d.y); });

	}
	
	function rect_click(d) {

		if (d3.event && d3.event.altKey) {
			x_ice.domain([d.x, d.x + d.dx]);
			y_ice.domain([d.y, 1]).range([d.y ? 20 : 0, h_ice]);
		}
		
		d3.select(".r_selected")
			.classed("r_selected", false);
		
		d3.select(this)
				.classed('r_selected', true);
				
		updateRect(d.i);
				
	}

	function rect_dblclick(d) {
		
		// Reset scales to original domain and y range
		x_ice.domain([0, 1]);
		y_ice.domain([0, 1]).range([0, h_ice]);
		
		updateRect(0);
	}

	function hover(d) {
		d3.select("#nodeinfo")
			.text("id = " + d.i + ", scale = " + d.s);
	}
});