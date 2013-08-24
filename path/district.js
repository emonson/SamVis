// --------------------------
// Ellipse plot variables

var DISTRICT = (function(d3, $, g){

	var dis = { version: '0.0.1' };

	var x_extent, y_extent, x_diff, y_diff, diff_max;
	var divElem2 = d3.select("#svgpath");
	var circle;
	var width = 800;
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
	
	// Setting up the base SVG element for the visualization
	var svgcanvas2 = divElem2.append("svg:svg")
				.attr("width", width)
				.attr("height", height)
			.append("g")
				.attr("transform", "translate(0,0)");
	
	// Clipping box for paths and ellipses which go outside of bounds
	// since vis is scaled right now to ellipse bounds and not paths
	svgcanvas2.append("defs").append("clipPath")
				.attr("id", "clip")
			.append("rect")
				.attr("width", width)
				.attr("height", height);
			
	// Individual g elements in which to place ellipses and paths
	var pathbox = svgcanvas2.append("g")
							.attr("clip-path", "url(#clip)");
	
	// Ellipses on top for now because listed second
	var elbox = svgcanvas2.append("g")
							.attr("clip-path", "url(#clip)");

	// SLIDER
	
	$(function(){

		// Slider
		$('#slider').dragslider({
			animate: true,
			range: true,
			rangeDrag: true,
			min: 0,
			max: 500,
			values: [30, 70],
			slide: function( event, ui ) {
						$.publish("/slider/slide", ui);
					}  
		});
	});



	// UTILITY private methods
	
	var coords_to_pairs = function(p_info, range) {
	
		var pairs_list = [];

		var path = p_info.path;
		var time_idx = p_info.time_idx;
		var district_id = p_info.district_id;
		var depth = p_info.depths;
		
		if (arguments.length == 2) {
			// Range supplied
			for (var ii = 0; ii < time_idx.length-1; ii++) {
				// only connect pairs that are sequential in time
				if (time_idx[ii] >= range[0] && time_idx[ii+1] <= range[1]) {
					if ((time_idx[ii+1] - time_idx[ii]) == 1) {
						pairs_list.push( path[ii].concat(path[ii+1], time_idx[ii], district_id[ii], depth[ii]) );
					}
				}
			}
		} else {
			// No range supplied
			for (var ii = 0; ii < time_idx.length-1; ii++) {
				// only connect pairs that are sequential in time
				if ((time_idx[ii+1] - time_idx[ii]) == 1) {
					pairs_list.push( path[ii].concat(path[ii+1], time_idx[ii], district_id[ii], depth[ii]) );
				}
			}
		}
	
		return pairs_list;
	};
	
	var scale_to_bounds = function(bounds) {

		// equalizing bounds so even x,y spacing even in w,h that doesn't match ratio
		// NOTE: setting against origin and adding padding on positive side
		//   (i.e. not centered on bounds)
		// TODO: this will probably have to change if adding padding, inverting y, etc...
		
		var xb = bounds[0];
		var yb = bounds[1];
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
	
	};

	// PUBLIC methods

	dis.slide_fcn = function(ui) {
	
		$( "#amount" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] )
		// values in global variable
		g.slider_values = ui.values;
		
		// Update path visualization
		var path_pairs = coords_to_pairs(g.path_info, ui.values);
		dis.update_paths(path_pairs, 0);
		
	};

	dis.el_hover = function(ellipse_id) {
	
		d3.select("#el_id").text("id = " + ellipse_id);
			
	};

	dis.update_ellipses = function(ellipse_data) {
	
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
				.on("mouseover", function(d) { $.publish("/district/ellipse_hover", d[5]);} )
				.on("click", function(d) { $.publish("/district/ellipse_click", d[5]);} )
			.transition()
			.delay(1000)
			.duration(500)
				.style("opacity", 1.0);

		els.exit()
				.remove();
	
	};
	
	dis.update_paths = function(path_pairs, t_delay) {
		
		// Creating actual path
		var pth = pathbox.selectAll("line")
				.data(path_pairs, function(d){return d[4];});

		pth.transition()
				.duration(t_delay)
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
			.delay(t_delay)
			.duration(t_delay/2.0)
				.style("stroke-opacity", function(d){return (d[6] < 2) ? 1.0 : 0.2;});

		pth.exit()
				.remove();
	
	};
	
	// Get data for both the paths and ellipses surrounding a certain district
	// and update visualizations for both
	dis.visgen = function(district_id) {
		
		d3.json( g.data_proxy_root + '/districtcoords?district_id=' + district_id + '&depth=2', function(path_info) {
			d3.json( g.data_proxy_root + '/districtellipses?district_id=' + district_id, function(ellipse_data) {
			
			// Store data in global object so can filter without retrieving
			g.ellipse_data = ellipse_data;
			g.path_info = path_info;
			
			// Only reset range values and t_max if this is the first time through
			// TODO: I don't like this method...
			if (g.slider_values[1] < 0) {
				$("#slider").dragslider({	'min': 0,
																	'max': path_info.t_max_idx,
																	'values': [0, path_info.t_max_idx]});
				g.slider_values = [0, path_info.t_max_idx];
			}
			
			// Scale X and Y scales correctly so they can be equal within unequal width and height
			scale_to_bounds(g.ellipse_data.bounds);
			
			// Update ellipse visualization
			dis.update_ellipses(g.ellipse_data);
	
			// Do the manipulation of path coordinates into line segment pairs with ids, etc here
			var path_pairs = coords_to_pairs(g.path_info, g.slider_values);
		
			// Update path visualization
			dis.update_paths(path_pairs, 1000);
			
			});
		});
	};

	return dis;

}(d3, jQuery, GLOBALS));

// END DISTRICT
// --------------------------
