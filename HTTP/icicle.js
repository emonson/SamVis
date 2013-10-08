// ============
// Icicle view

var ICICLE = (function(d3, $, g){

	var ic = { version: '0.0.1' };

	// - - - - - - - - - - - - - - - -
	// Icicle view variables

	var w_ice = 420;
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
			.on("mouseout", function() {
					d3.select("#nodeinfo").text("id = , scale = ");
					$.publish("/icicle/mouseout", g.node_id);
				});

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

	var rect_click = function(d) {
	
		// NOTE: If click on a different scale rectangle while scatterplot is
		//   projected into a non-scale-0 basis, change to that different scale
		//   representation in the scatterplot, but basis projected into is now not
		//   one that is present in the ellipses on the plot...
		
		// Only update icicle zoom if alt has been selected
		if (d3.event && d3.event.altKey) {
			x_ice.domain([d.x, d.x + d.dx]);
			y_ice.domain([d.y, 1]).range([d.y ? 20 : 0, h_ice]);
		
			zoomIcicleView(d.i);
		}
		else {
			var new_scale = g.scales_by_id[g.node_id] == g.scales_by_id[d.i] ? false : true;
			g.node_id = d.i;
			$.publish("/icicle/rect_click", d.i);
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
		$.publish("/icicle/rect_hover", d.i);
	};

	ic.updateScalarData = function() {
		vis.selectAll("rect")
				.attr("fill", function(d) { return g.cScale(g.scalardata[d.i]); });
	};
	
	ic.highlightSelectedRect = function(sel_id) {

		// Unhighlight previously selected icicle rectangle
		d3.select(".r_selected")
			.classed("r_selected", false);

		// Highlight currently clicked rectangle
		d3.select("#r_" + sel_id)
			.classed('r_selected', true);			
	};

	ic.init_icicle_view = function() {
	
		d3.json(g.data_proxy_root + "/index", function(json) {
		
			// TODO: Don't need to send 's' as an attribute, partition function calculates
			//   attribute 'depth'...
		
			// Before building tree, compile convenience data structures
			var ice_partition = partition_ice(json);
			g.scales_by_id = new Array(ice_partition.length);
			for (var ii = 0; ii < ice_partition.length; ii++) {
				var node = ice_partition[ii];
				var scale = node.s
				g.scales_by_id[node.i] = scale;
				if (!g.ids_by_scale.hasOwnProperty(scale)) {
					g.ids_by_scale[scale] = [];
				}
				g.ids_by_scale[scale].push(node.i);
			}
		
			// Build tree
			var rect = vis.selectAll("rect")
					.data(ice_partition)
				.enter().append("svg:rect")
					.attr("id", function(d) {return "r_" + d.i;})
					.attr("x", function(d) { return x_ice(d.x); })
					.attr("y", function(d) { return y_ice(d.y); })
					.attr("width", function(d) { return x_ice(d.dx); })
					.attr("height", function(d) { return y_ice(d.dy); })
					.attr("fill", function(d) { return g.cScale(g.scalardata[d.i]); })
					.on("click", rect_click)
					.on("dblclick", rect_dblclick)
					.on("mouseover", rect_hover);
		});
	};

	return ic;

}(d3, jQuery, GLOBALS));

// END ICICLE FUNCTIONS
// --------------------------
