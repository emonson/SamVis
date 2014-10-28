// ============
// Icicle view

var ICICLE = (function(d3, $, g){

	var ic = { version: '0.0.1' };

	// - - - - - - - - - - - - - - - -
	// Icicle view variables

    var w_frac = 1.0;
	var w_ice = $("#tree_container").width() * w_frac;
	var aspect = 280/350; // height/width
	var h_ice = aspect * w_ice;

	var x_ice = d3.scale.linear().range([0, w_ice]);
	var y_ice = d3.scale.linear().range([0, h_ice]);
	var color = d3.scale.category20c();
	var brush_on = false;
	var ice_partition = null;
	var ice_data = null;

	// Icicle view tree layout calculation function
	// JSON object member keys have simplified names to keep file and transfer size down.
	// d.c = d.children
	// d.v = d.value (number of leaf members / node)
	// d.i = d.id
	var partition_ice = d3.layout.partition()
			.sort(function(a,b){ return b.i - a.i; })
			.children(function(d){ return d.c ? d.c : null;})
			.value(function(d){return d.v ? d.v : null;});
			
	// Icicle view SVG element
	var vis = d3.select("#tree").append("svg:svg")
			.attr("width", w_ice)
			.attr("height", h_ice);
			// TODO: Need some sort of mostly transparent rectangle behind tree
			//   elements so that mousing out of an individual icicle rectangle doesn't
			//   cause a "mouseout"
// 			.on("mouseout", function() {
// 					d3.select("#nodeinfo").text("id = , scale = ");
// 					$.publish("/icicle/mouseout", g.node_id);
// 				});

    ic.resize = function() {
        w_ice = $("#tree_container").width() * w_frac;
        h_ice = aspect * w_ice;

	    x_ice.range([0, w_ice]);
	    y_ice.range([0, h_ice]);

        vis.attr("width", w_ice);
        vis.attr("height", h_ice);
        
        rescaleIcicleRectangles(0.001);
    };

	ic.zoomIcicleView = function(sel_id) {
		
		var node = g.nodes_by_id[sel_id];
		
        x_ice.domain([node.x, node.x + node.dx]);
        y_ice.domain([node.y, 1]).range([node.y ? 20 : 0, h_ice]);
        
		// Change icicle zoom
		vis.selectAll("rect")
			.transition()
				.duration(750)
				.attr("x", function(d) { return x_ice(d.x); })
				.attr("y", function(d) { return y_ice(d.y); })
				.attr("width", function(d) { return x_ice(d.x + d.dx) - x_ice(d.x); })
				.attr("height", function(d) { return y_ice(d.y + d.dy) - y_ice(d.y); });
	};

	var rescaleIcicleRectangles = function(trans_dur) {
		
		// Default value for transition duration
		trans_dur = trans_dur || 750;
	
		ice_partition = partition_ice(ice_data);
		
		// Change icicle zoom
		vis.selectAll("rect")
				.data(ice_partition, function(d){return d.i;})
			.transition()
				.duration(trans_dur)
					.attr("x", function(d) { return x_ice(d.x); })
					.attr("y", function(d) { return y_ice(d.y); })
					.attr("width", function(d) { return x_ice(d.x + d.dx) - x_ice(d.x); })
					.attr("height", function(d) { return y_ice(d.y + d.dy) - y_ice(d.y); });
	};
	
	var rect_click = function(d) {
	
		if (d3.event && $("#tree_treezoom_button").hasClass("active")) {
			$.publish("/node/alt_click", d.i);
		} 
		else if (d3.event && $("#tree_info_button").hasClass("active")) {
		    $.publish("/node/info", d.i);
		}
		else {
			var new_scale = g.scales_by_id[g.node_id] == g.scales_by_id[d.i] ? false : true;
			g.node_id = d.i;
			$.publish("/node/click", d.i);
		}
	};

	ic.reset_zoom = function(d) {
	
	    // Pass root node to zoom
		ic.zoomIcicleView(g.root_node_id);
	};

	// Set up a hover timer to rate-limit (throttle) sending of requests for detailed data views
	var hover_timer;
	var rect_enter = function(d) {
		d3.select("#nodeinfo")
			.text("id = " + d.i + ", scale = " + d.s);
		hover_timer = setTimeout(function(){$.publish("/node/hover", d.i);}, 20);
	};
	var rect_exit = function(d) {
		clearTimeout(hover_timer);
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
    
    function useUpdatedTree(json) {
        // TODO: Don't need to send 's' as an attribute, partition function calculates
        //   attribute 'depth'...
        ice_data = json;
        
        // Before building tree, compile convenience data structures
        ice_partition = partition_ice(ice_data);
        // Node IDs are not necessarily sequential, so need to store as objects if indexing by ID
        g.scales_by_id = {};
        g.nodes_by_id = {};
        for (var ii = 0; ii < ice_partition.length; ii++) {
            var node = ice_partition[ii];
            var scale = node.s
            g.scales_by_id[node.i] = scale;
            g.nodes_by_id[node.i] = node;
            if (!g.ids_by_scale.hasOwnProperty(scale)) {
                g.ids_by_scale[scale] = [];
            }
            g.ids_by_scale[scale].push(node.i);
            if (scale > g.max_scale) {
                g.max_scale = scale;
            }
        }
    
        // Build tree
        var rect = vis.selectAll("rect")
                .data(ice_partition)
            .enter().append("svg:rect")
                .attr("id", function(d) {return "r_" + d.i;})
                .attr("x", function(d) { return x_ice(d.x); })
                .attr("y", function(d) { return y_ice(d.y); })
                .attr("width", function(d) { return x_ice(d.x + d.dx) - x_ice(d.x); })
                .attr("height", function(d) { return y_ice(d.y + d.dy) - y_ice(d.y); })
                .attr("fill", function(d) { return g.cScale(g.scalardata[d.i]); })
                .on("click", rect_click)
                .on("mouseover", rect_enter)
                .on("mouseout", rect_exit);
		
		$.publish("/icicle/initialized");
    };
	
	ic.init_icicle_view = function() {
	    if (g.comm_method == 'http') {
		    d3.json('/' + g.dataset + "/index", useUpdatedTree );
		} else {
		    g.session.call('test.ipca.tree', [], {dataset: g.dataset}).then( useUpdatedTree );
		}
	};

	return ic;

}(d3, jQuery, GLOBALS));

// END ICICLE FUNCTIONS
// --------------------------
