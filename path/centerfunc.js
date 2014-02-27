// --------------------------
// Ellipse (district) Center 1D Function plot

var CENTER_VIS = (function(d3, $, g){

	var ci = { version: '0.0.1' };

	// Append vis-specific div
	d3.select("#district_center_data_vis").append('div').attr('id', 'district_center_func');

	var margin = {top: 10, right: 10, bottom: 20, left: 30},
			width = 200 - margin.left - margin.right,
			height = 150 - margin.top - margin.bottom;

	var x = d3.scale.linear()
			.range([0, width]);

	var y = d3.scale.linear()
			.range([height, 0]);

	var xAxis = d3.svg.axis()
			.scale(x)
			.orient("bottom")
			.ticks(3);

	var yAxis = d3.svg.axis()
			.scale(y)
			.orient("left")
			.ticks(0);

	var line = d3.svg.line()
			.x(function(d,i) { return x(i); })
			.y(function(d) { return y(d); });

	var svg = d3.select("#district_center_func").append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
		.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

	// Since we're using the whole center data set bounds, shouldn't have to update axes
	svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis);

	svg.append("g")
			.attr("class", "y axis")
			.call(yAxis);

	// Get basis images from server
	ci.getCenterDataFromServer = function(id) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/districtcenterdata?district_id=" + id, function(json) {
	
			g.district_center_data = json.data;
			g.district_center_data_dims = json.data_dims;
			g.district_center_range = json.data_range;

			x.domain([0, g.district_center_data[0].length]);
			y.domain(g.data_bounds);

			updatePlot();
		});
	};

	var updatePlot = function() {
		
		// TODO: Use transition instead of replacing line each time!
		svg.selectAll(".line").remove();
		
		svg.selectAll("g.y.axis").call(yAxis);
		svg.selectAll("g.x.axis").call(xAxis);
		
		// This is hard-coded to only take one data series in a 2d array right now...
		svg.append("path")
				.datum(g.district_center_data[0])
				.attr("class", "line")
				.attr("d", line);
		
	};

	return ci;

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------