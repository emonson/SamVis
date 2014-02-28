// --------------------------
// Ellipse (district) Center 1D Function plot

var CENTER_VIS = (function(d3, $, g){

	var ci = { version: '0.0.1' };

	// Append vis-specific div
	d3.select("#district_center_data_vis").append('div').attr('id', 'district_center_func');

	// Keep around a consistent place to store the line plot data
	// and fill with dummy data
  var data = [];
  for (var ii = 0; ii < 100; ii++) {
  	data.push(0);
  }

  var margin = {top: 6, right: 0, bottom: 6, left: 6},
      width = 180 - margin.left - margin.right,
      height = 120 - margin.top - margin.bottom;

  var x = d3.scale.linear()
      .domain([0, data.length-1])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([-1, 1])
      .range([height, 0]);

	var yAxis = d3.svg.axis()
			.scale(y)
			.orient("left")
			.ticks(0);

  var line = d3.svg.line()
      .x(function(d, i) { return x(i); })
      .y(function(d, i) { return y(d); });

  var svg = d3.select("#district_center_func").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("defs").append("clipPath")
      .attr("id", "clip")
    .append("rect")
      .attr("width", width)
      .attr("height", height);

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);

  var path = svg.append("g")
      .attr("clip-path", "url(#clip)")
    .append("path")
      .data([data])
      .attr("class", "plotline")
      .attr("d", line);


	var updatePlot = function(delay) {
		
	 delay = delay || 100;
	 
	 // transition the line
		path.data([data])
			.transition()
				.duration(delay)
				.attr("d", line)
		
		svg.selectAll("g.y.axis").call(yAxis);
		
	};

	// PUBLIC methods
	
	// Get basis images from server
	ci.getCenterDataFromServer = function(id) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/districtcenterdata?district_id=" + id, function(json) {
	
			var orig_n = data.length;
			
			g.district_center_data = json.data;
			g.district_center_data_dims = json.data_dims;
			g.district_center_range = json.data_range;

			// Assign the plot data
			data = g.district_center_data[0];
			x.domain([0, data.length-1]);
			y.domain(g.data_bounds);
			
			// First transition fast
			if (orig_n == 2) {
				updatePlot(0);
			} else {
				updatePlot(1000);
			}
		});
	};

	return ci;

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------