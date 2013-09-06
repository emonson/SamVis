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
	
	var color_by_time_scale = d3.scale.linear()
				.domain([0, 1])
				.range(["red", "blue"]);
	
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
	
	// Linear gradient in X to use for ellipses
	// TODO: https://gist.github.com/dholth/1368205
	var gradient = svgcanvas2.append("svg:defs")
		.append("svg:linearGradient")
			.attr("id", "gradient")
			.attr("x1", "0%")
			.attr("y1", "0%")
			.attr("x2", "100%")
			.attr("y2", "0%")
			.attr("spreadMethod", "pad");

	gradient.append("svg:stop")
			.attr("offset", "0%")
			.attr("stop-color", "#0c0")
			.attr("stop-opacity", 1);

	gradient.append("svg:stop")
			.attr("offset", "100%")
			.attr("stop-color", "#c00")
			.attr("stop-opacity", 1);
 			
	// Individual g elements in which to place ellipses and paths
	var pathbox = svgcanvas2.append("g")
							.attr("clip-path", "url(#clip)");
	
	// Ellipses on top for now because listed second
	var elbox = svgcanvas2.append("g")
							.attr("clip-path", "url(#clip)");

	// Slider creation
	$('#slider').dragslider({
		animate: true,
		range: true,
		rangeDrag: true,
		min: 0,
		max: 1000,
		values: [0, 1000],
		slide: function( event, ui ) {
					$.publish("/slider/slide", ui);
				}  
	});

	// COMBO Box callback
	$("#ellipse_type").on('change', function(){
		var type = $(this).val();
		$.publish("/ellipse_type/change", type);
	});

	// COMBO Box callback
	$("#path_color").on('change', function(){
		var type = $(this).val();
		$.publish("/path_color/change", type);
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
	
	var set_path_stroke_color = function(d,i) {
		
		switch(g.path_color) {
		
			case 'domain':
				return c_scale(d[5]);
				break;
			case 'time':
				return color_by_time_scale(d[4]);
				break;
				
			default:
				return 'saddlebrown';
				break;
		}
	};

	// PUBLIC methods

	dis.ellipse_type_change_fcn = function(val){
		
		// Store ellipse type in global object and then get proper ellipse data
		g.ellipse_type = val;
		dis.grab_only_ellipses();
	};
	
	dis.path_color_change_fcn = function(val){
		
		// Store path color in global object and rerender
		g.path_color = val;
		dis.update_paths(0);
	};
	
	dis.slide_fcn = function(ui) {
	
		$( "#time_range" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] )
		// values in global variable
		g.slider_values = ui.values;
		// also update domain of color scale for coloring by time
		color_by_time_scale.domain(ui.values);
		
		// Update path visualization
		g.path_pairs = coords_to_pairs(g.path_info, ui.values);
		dis.update_paths(0);
		
	};

	dis.el_hover = function(ellipse_id) {
	
		d3.select("#el_id").text("ellipse id = " + ellipse_id);
			
	};

	dis.update_ellipses = function(t_delay) {
	
		// Update the ellipses
		// data = [[X, Y, RX, RY, Phi, i], ...]
		var els = elbox.selectAll("ellipse")
				.data(g.ellipse_data.data, function(d){return d[5];});

		els.transition()
			.duration(t_delay)		
				.attr("transform", function(d){return "translate(" + x_scale(d[0]) + "," + y_scale(d[1]) + ")  rotate(" + -d[4] + ")";})
				.attr("rx", function(d) { return xr_scale(d[2]); })
				.attr("ry", function(d) { return yr_scale(d[3]); });

		els.enter()
				.append("ellipse")
				// NOTE: since Y-axis is inverted in SVG coordinate system, need to invert rotation angle...
				.attr("transform", function(d){return "translate(" + x_scale(d[0]) + "," + y_scale(d[1]) + ")  rotate(" + -d[4] + ")";})
				.attr("rx", function(d) { return xr_scale(d[2]); })
				.attr("ry", function(d) { return yr_scale(d[3]); })
				// .attr("fill", function(d) {return c_scale(d[5]); })
				.attr("fill", 'gray')
				// .attr("fill", "url(#gradient)")
				.style("opacity", 0.0)
				.on("mouseover", function(d) { $.publish("/district/ellipse_hover", d[5]);} )
				.on("click", function(d) { $.publish("/district/ellipse_click", d[5]);} )
			.transition()
			.delay(t_delay)
			.duration(t_delay/2.0)
				.style("opacity", 1.0);

		els.exit()
				.remove();
		
		var drift = elbox.selectAll("line")
			.data(g.ellipse_data.drift, function(d){return d[4];});
		
		drift.transition()
				.duration(t_delay)
				.attr("x1", function(d){return x_scale(d[0]);})
				.attr("y1", function(d){return y_scale(d[1]);})
				.attr("x2", function(d){return x_scale(d[2]);})
				.attr("y2", function(d){return y_scale(d[3]);})
				.style("stroke", "black")
				.style("stroke-opacity", 1.0);

		drift.enter()
				.append("line")
				.attr("x1", function(d){return x_scale(d[0]);})
				.attr("y1", function(d){return y_scale(d[1]);})
				.attr("x2", function(d){return x_scale(d[2]);})
				.attr("y2", function(d){return y_scale(d[3]);})
				.style("stroke-width", 2.0)
				.style("stroke-opacity", 0.0)
				.style("stroke", "black")
				.style("fill", "none")
			.transition()
			.delay(t_delay)
			.duration(t_delay/2.0)
				.style("stroke-opacity", 1.0);

		drift.exit()
				.remove();		
	
	};
	
	dis.update_paths = function(t_delay) {
		
		// Creating actual path
		var pth = pathbox.selectAll("line")
				.data(g.path_pairs, function(d){return d[4];});

		pth.transition()
				.duration(t_delay)
				.attr("x1", function(d){return x_scale(d[0]);})
				.attr("y1", function(d){return y_scale(d[1]);})
				.attr("x2", function(d){return x_scale(d[2]);})
				.attr("y2", function(d){return y_scale(d[3]);})
				.style("stroke", set_path_stroke_color)
				.style("stroke-opacity", function(d){return (d[6] < 2) ? 1.0 : 0.2;});

		pth.enter()
				.append("line")
				.attr("x1", function(d){return x_scale(d[0]);})
				.attr("y1", function(d){return y_scale(d[1]);})
				.attr("x2", function(d){return x_scale(d[2]);})
				.attr("y2", function(d){return y_scale(d[3]);})
				.style("stroke-width", 2.0)
				.style("stroke-opacity", 0.0)
				.style("stroke", set_path_stroke_color)
				.style("fill", "none")
			.transition()
			.delay(t_delay)
			.duration(t_delay/2.0)
				.style("stroke-opacity", function(d){return (d[6] < 2) ? 1.0 : 0.2;});

		pth.exit()
				.remove();
	
	};
	
	// Only grab ellipse data from server
	dis.grab_only_ellipses = function() {
		
		d3.json( g.data_proxy_root + '/districtellipses?district_id=' + g.district_id + '&type=' + g.ellipse_type, function(ellipse_data) {
		
			// Store data in global object so can filter without retrieving
			g.ellipse_data = ellipse_data;
		
			// Scale X and Y scales correctly so they can be equal within unequal width and height
			scale_to_bounds(g.ellipse_data.bounds);
		
			// Update ellipse visualization
			dis.update_ellipses(1000);

			// Do the manipulation of path coordinates into line segment pairs with ids, etc here
			g.path_pairs = coords_to_pairs(g.path_info, g.slider_values);
	
			// Update path visualization
			dis.update_paths(1000);
		
		});
	};

	// Get data for both the paths and ellipses surrounding a certain district
	// and update visualizations for both
	dis.visgen = function(district_id) {
		
		// Store old center for transfer routines
		g.prev_district = g.district_id;
		
		d3.json( g.data_proxy_root + '/districtcoords?district_id=' + district_id + '&depth=2&previous_id=' + g.prev_district + "&rold=" + g.R_old, function(path_info) {
			d3.json( g.data_proxy_root + '/districtellipses?district_id=' + district_id + '&type=' + g.ellipse_type, function(ellipse_data) {
			
			// Store data in global object so can filter without retrieving
			g.district_id = district_id;
			g.ellipse_data = ellipse_data;
			g.path_info = path_info;
			g.R_old = path_info.R_old;
			
			// Only reset range values and t_max if this is the first time through
			// TODO: I don't like this method...
			if (g.slider_values[1] < 0) {
				$("#slider").dragslider({	'min': 0,
																	'max': path_info.t_max_idx,
																	'values': [0, path_info.t_max_idx]});
				g.slider_values = [0, path_info.t_max_idx];
				color_by_time_scale.domain([0, path_info.t_max_idx]);
				$( "#time_range" ).val( "0 - " + path_info.t_max_idx )
			}
			
			// Scale X and Y scales correctly so they can be equal within unequal width and height
			scale_to_bounds(g.ellipse_data.bounds);
			
			// Update ellipse visualization
			dis.update_ellipses(1000);
	
			// Do the manipulation of path coordinates into line segment pairs with ids, etc here
			g.path_pairs = coords_to_pairs(g.path_info, g.slider_values);
		
			// Update path visualization
			dis.update_paths(1000);
			
			});
		});
	};

	return dis;

}(d3, jQuery, GLOBALS));

// END DISTRICT
// --------------------------
