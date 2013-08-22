// var host_path = 'localhost';
var host_path = 'emo2.trinity.duke.edu';

var x_extent, y_extent, x_diff, y_diff, diff_max;
var divElem2 = d3.select("#svgpath");
var circle;
var width = 600;
var height = 600;

var x_scale = d3.scale.linear().range([0,width]);
var y_scale = d3.scale.linear().range([0,height]);
var xr_scale = d3.scale.linear().range([0,width]);
var yr_scale = d3.scale.linear().range([0,height]);
var path_depth_color = d3.scale.linear()
		.domain([0, 2])
		.range(["saddlebrown", "#ddd"]);
		
var idx_ints = [];

// HACK: Hard-coding color scale for 1127 ellipse IDs...
for (var i=0; i<1127; i++) { idx_ints.push(i); }
var c_scale = d3.scale.category20().domain(idx_ints);

var svgcanvas2 = divElem2.append("svg:svg")
			.attr("width", width)
			.attr("height", height)
		.append("g")
			.attr("transform", "translate(0,0)");

svgcanvas2.append("defs").append("clipPath")
			.attr("id", "clip")
		.append("rect")
			.attr("width", width)
			.attr("height", height);
			
var pathbox = svgcanvas2.append("g")
						.attr("clip-path", "url(#clip)");

var elbox = svgcanvas2.append("g")
						.attr("clip-path", "url(#clip)");

var el_hover = function(d) {
	d3.select("#el_id")
		.text("id = " + d[5]);
}

var district_id = 162;

var el_click_function = function() {
				
	var that = this;
	visgen(that.__data__[5]);
	
	// $.publish("/elplot/ellipse_click", that.__data__[5]);
};

var coords_to_pairs = function(p_info) {
	
	var pairs_list = [];

	var path = p_info.path;
	var time_idx = p_info.time_idx;
	var district_id = p_info.district_id;
	var depth = p_info.depths;
	
	for (var ii = 0; ii < time_idx.length-1; ii++) {
		// only connect pairs that are sequential in time
		if ((time_idx[ii+1] - time_idx[ii]) == 1) {
			pairs_list.push( path[ii].concat(path[ii+1], time_idx[ii], district_id[ii], depth[ii]) );
		}
	}
	
	return pairs_list;
}

var visgen = function(district_id) {
	d3.json('http://' + host_path + '/remote/districtdeeplocalcoords?district_id=' + district_id + '&depth=2', function(path_info) {
		d3.json('http://' + host_path + '/remote/districtlocalellipses?district_id=' + district_id, function(ellipse_data) {
	
	// Do the manipulation of path coordinates into line segment pairs with ids, etc here
	var path_pairs = coords_to_pairs(path_info);
	
	// equalizing bounds so even x,y spacing even in w,h that doesn't match ratio
	// setting against origin and adding padding on positive side
	// TODO: this will probably have to change if adding padding, inverting y, etc...
	var xb = ellipse_data.bounds[0];
	var yb = ellipse_data.bounds[1];
	var x_range = xb[1]-xb[0];
	var y_range = yb[1]-yb[0];
	var display_ratio = width/height;
	var data_ratio = x_range/y_range;
	var extra;
	if (display_ratio <= data_ratio) { 
		// display taller than data
		extra = x_range/display_ratio - y_range;
		yb[1] = yb[1] + extra;
	} else { 
		// display wider than data
		extra = y_range*display_ratio - x_range;
		xb[1] = xb[1] + extra;
	};
	// calculate new range
	x_range = xb[1]-xb[0];
	y_range = yb[1]-yb[0];
	
	x_scale.domain(xb);
	y_scale.domain(yb);
	xr_scale.domain([0, x_range]);
	yr_scale.domain([0, y_range]);

	// Specify the function for generating path data             
	var lineFunction = d3.svg.line()
									.x(function(d){return x_scale(d[0]);})
									.y(function(d){return y_scale(d[1]);})
									.interpolate("linear");

	// Update the ellipses
	// data = [[X, Y, RX, RY, Phi, i], ...]
	var els = elbox.selectAll("ellipse")
			.data(ellipse_data.data, function(d){return d[5];});
	
	els.transition()
		.duration(1000)		
			.attr("transform", function(d){return "translate(" + x_scale(d[0]) + "," + y_scale(d[1]) + ")  rotate(" + -d[4] + ")";})
			.attr("rx", function(d) { return xr_scale(d[2]); })
			.attr("ry", function(d) { return yr_scale(d[3]); });

	els.enter()
			.append("ellipse")
			// NOTE: since Y-axis is inverted in SVG coordinate system, need to invert rotation angle...
			.attr("transform", function(d){return "translate(" + x_scale(d[0]) + "," + y_scale(d[1]) + ")  rotate(" + -d[4] + ")";})
			.attr("rx", function(d) { return xr_scale(d[2]); })
			.attr("ry", function(d) { return yr_scale(d[3]); })
			.attr("fill", function(d) {return c_scale(d[5]); })
			// .attr("fill", 'gray')
			.style("opacity", 0.0)
			.on("mouseover", el_hover)
			.on("click", el_click_function)
		.transition()
		.delay(1000)
		.duration(500)
			.style("opacity", 1.0);
	
	els.exit()
			.remove();

	
	// Creating actual path
	// Creating actual path
	var pth = pathbox.selectAll("line")
			.data(path_pairs, function(d){return d[4];});
	
	pth.transition()
			.duration(1000)
			.attr("x1", function(d){return x_scale(d[0]);})
			.attr("y1", function(d){return y_scale(d[1]);})
			.attr("x2", function(d){return x_scale(d[2]);})
			.attr("y2", function(d){return y_scale(d[3]);})
			.style("stroke", function(d){return c_scale(d[5]);})
			.style("stroke-opacity", function(d){return (d[6] < 2) ? 1.0 : 0.2;});
			// .style("stroke", function(d){return (d[6] < 2) ? 'saddlebrown' : 'papayawhip';});
	
	pth.enter()
			.append("line")
			.attr("x1", function(d){return x_scale(d[0]);})
			.attr("y1", function(d){return y_scale(d[1]);})
			.attr("x2", function(d){return x_scale(d[2]);})
			.attr("y2", function(d){return y_scale(d[3]);})
			.style("stroke-width", 2.0)
			.style("stroke-opacity", 0.0)
			.style("stroke", function(d){return c_scale(d[5]);})
			// .style("stroke", function(d){return (d[6] < 2) ? 'saddlebrown' : 'papayawhip';})
			.style("fill", "none")
		.transition()
		.delay(1000)
		.duration(500)
			.style("stroke-opacity", function(d){return (d[6] < 2) ? 1.0 : 0.2;});
	
	pth.exit()
			.remove();
	
		});
	});
};

// MAIN
//
// Generate initial vis
visgen(district_id);