var site_root = "http://emo2.trinity.duke.edu/~emonson/Sam/"

//Width and height
var w_el = 500;
var h_el = 500;
var padding = 30;
var selectColor = "gold";
var node_id = 1200;
var basis_id = 0;

// Arrays to hold ellipse data pulled from JSON
var dataset = [];
var colordata = [];
var filldata = [];

// Icicle view variables
var w_ice = 600,
		h_ice = 400,
		x = d3.scale.linear().range([0, w_ice]),
		y = d3.scale.linear().range([0, h_ice]),
		color = d3.scale.category20c(),
		cLabelScale = d3.scale.linear()
									.domain([0.0, 0.5, 1.0])
									.range(["#CA0020", "#EEEEEE", "#0571B0"]);


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

d3.json(site_root + "treeellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

	dataset = json.data;

	colordata = json.labels;
	for(var i=0; i < colordata.length; i++) {
		filldata.push(0.1);
	}

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
			.attr("class", "ell")
			.attr("stroke", function(d,i){return cScale(colordata[i]);})
			.attr("fill-opacity", function(d,i){return filldata[i];})
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
		.on("mousewheel", function() {
			d3.select(this)
				.attr("fill-opacity", function(d){
					var o = filldata[d[5]]; // HACK: storing index in data…
					o += 0.005*d3.event.wheelDelta; 
					o = (o > 1.0) ? 1.0 : o;
					o = (o < 0.1) ? 0.1 : o;
					filldata[d[5]] = o;
					return o;
				});
			});
			
}); // JSON function end

var clickfctn = function() {
				
	var that = this;
	d3.select(this)
			.attr("stroke", selectColor);
	basis_id = that.__data__[5];

	d3.json(site_root + "treeellipsesfacade.php?id=" + node_id + "&basis=" + basis_id, function(json) {

		dataset = json.data;

		//Update scale domains
		var xRange = d3.extent(dataset, function(d) { return d[0]; })
		var yRange = d3.extent(dataset, function(d) { return d[1]; })
		xScale.domain(xRange);
		yScale.domain(yRange);
		xrScale.domain([0, xRange[1]-xRange[0]]);
		yrScale.domain([0, yRange[1]-yRange[0]]);

		//Update all circles
		svg.selectAll("ellipse")
				.data(dataset)
			.transition()
				.duration(1000)		
				.attr("transform", function(d){return "translate(" + xScale(d[0]) + "," + yScale(d[1]) + ")  rotate(" + d[4] + ")";})
				.attr("stroke", function(d,i){return (this === that) ? selectColor : cScale(colordata[i]);})
				.attr("rx", function(d) { return xrScale(d[2]); })
				.attr("ry", function(d) { return yrScale(d[3]); });

		//Update X axis
		svg.select(".x.axis")
			.transition()
			.duration(1000)
			.call(xAxis);

		//Update Y axis
		svg.select(".y.axis")
			.transition()
			.duration(1000)
			.call(yAxis);
	});
}; // close clickfunction


// ============
// icicle view

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
			.attr("x", function(d) { return x(d.x); })
			.attr("y", function(d) { return y(d.y); })
			.attr("width", function(d) { return x(d.dx); })
			.attr("height", function(d) { return y(d.dy); })
			.attr("fill", function(d) { return cLabelScale(d.l); })
			.on("click", click)
			.on("mouseover", hover);

	function click(d) {
		x.domain([d.x, d.x + d.dx]);
		y.domain([d.y, 1]).range([d.y ? 20 : 0, h_ice]);

		rect.transition()
			.duration(750)
			.attr("x", function(d) { return x(d.x); })
			.attr("y", function(d) { return y(d.y); })
			.attr("width", function(d) { return x(d.x + d.dx) - x(d.x); })
			.attr("height", function(d) { return y(d.y + d.dy) - y(d.y); });
	}

	function hover(d) {
		d3.select("#nodeinfo")
			.text("id = " + d.i + ", scale = " + d.s);
	}
});