// ============
// Icicle view

var ICICLE = (function(d3, $, g){

	var ic = { version: '0.0.1' };

	// - - - - - - - - - - - - - - - -
	// Icicle view variables

	var w_ice = 420;
	var h_ice = 420;
	var x_ice = d3.scale.linear().range([0, w_ice]);
	var y_ice = d3.scale.linear().range([0, h_ice]);
    var r_sun = Math.min(w_ice, h_ice) / 2;
    var x_sun = d3.scale.linear().range([0, 2 * Math.PI]);
    var y_sun = d3.scale.sqrt().range([0, r_sun]);
	var color = d3.scale.category20c();
	var brush_on = false;
	var ice_partition = null;
	var ice_data = null;
	var partition_toggle = true;

	// Icicle view tree layout calculation function
	// JSON object member keys have simplified names to keep file and transfer size down.
	// d.c = d.children
	// d.v = d.value (number of leaf members / node)
	// d.i = d.id
	var partition_ice = d3.layout.partition()
			.sort(function(a,b){ return b.i - a.i; })
			.children(function(d){ return d.c ? d.c : null;})
			.value(function(d){return d.v ? d.v : null;});
			
	var partition_ice_inv = d3.layout.partition()
			.sort(function(a,b){ return b.i - a.i; })
			.children(function(d){ return d.c ? d.c : null;})
			.value(function(d){return d.v ? 1.0/d.v : null;});

    var arc = d3.svg.arc()
        .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x_sun(d.x))); })
        .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x_sun(d.x + d.dx))); })
        .innerRadius(function(d) { return Math.max(0, y_sun(d.y)); })
        .outerRadius(function(d) { return Math.max(0, y_sun(d.y + d.dy)); });
	
    // Interpolate the scales!
    function arcTween(d) {
      var xd = d3.interpolate(x_sun.domain(), [d.x, d.x + d.dx]),
          yd = d3.interpolate(y_sun.domain(), [d.y, 1]),
          yr = d3.interpolate(y_sun.range(), [d.y ? 20 : 0, r_sun]);
      return function(d, i) {
        return i
            ? function(t) { return arc(d); }
            : function(t) { x_sun.domain(xd(t)); y_sun.domain(yd(t)).range(yr(t)); return arc(d); };
      };
    }
    
	// Icicle view SVG element
	var vis = d3.select("#tree").append("svg:svg")
			.attr("width", w_ice)
			.attr("height", h_ice)
		.append("g")
            .attr("transform", "translate(" + w_ice / 2 + "," + h_ice / 2 + ")");
			// TODO: Need some sort of mostly transparent rectangle behind tree
			//   elements so that mousing out of an individual icicle rectangle doesn't
			//   cause a "mouseout"
// 			.on("mouseout", function() {
// 					d3.select("#nodeinfo").text("id = , scale = ");
// 					$.publish("/icicle/mouseout", g.node_id);
// 				});

	ic.zoomIcicleView = function(sel_id) {
		
		var d = g.nodes_by_id[sel_id];
		
		// Change icicle zoom
		vis.selectAll("path")
			.transition()
            .duration(750)
            .attrTween("d", arcTween(d));
	};

	var rescaleIcicleRectangles = function() {
		
		ice_partition = do_partition(ice_data);
		
		// Change icicle zoom
		vis.selectAll("path")
				.data(ice_partition, function(d){return d.i;})
			.transition()
				.duration(750)
				.attr("d", arc);
	};
	
	var do_partition = function(data) {
		if (partition_toggle) {
			return partition_ice(data);
		} else {
			return partition_ice_inv(data);
		}
	};

	var rect_click = function(d) {
	
		// TODO: Decouple the events from the responses, and move them to main.js!!
		
		if (d3.event && d3.event.altKey) {
			$.publish("/icicle/rect_alt_click", d.i);
		}
		if (d3.event && d3.event.shiftKey) {
			// TODO: Move this to a combo box or button instead of key click!
			partition_toggle = partition_toggle ? false : true;
			rescaleIcicleRectangles();
			$.publish("/icicle/rect_shift_click", d.i);
		}
		else {
			var new_scale = g.scales_by_id[g.node_id] == g.scales_by_id[d.i] ? false : true;
			g.node_id = d.i;
			$.publish("/icicle/rect_click", d.i);
		}
	};

	var rect_dblclick = function(d) {
	
	    // Pass root node to zoom
		ic.zoomIcicleView(g.root_node_id);
	};

	// Set up a hover timer to rate-limit sending of requests for detailed data views
	var hover_timer;
	var rect_enter = function(d) {
		d3.select("#nodeinfo")
			.text("id = " + d.i + ", scale = " + d.s);
		hover_timer = setTimeout(function(){$.publish("/icicle/rect_hover", d.i);}, 20);
	};
	var rect_exit = function(d) {
		clearTimeout(hover_timer);
	};

	ic.updateScalarData = function() {
		vis.selectAll("path")
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
        ice_partition = do_partition(ice_data);
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
        }
    
        // Build tree
        var rect = vis.selectAll("path")
                .data(ice_partition)
            .enter().append("path")
                .attr("id", function(d) {return "r_" + d.i;})
                .attr("d", arc)
                .attr("fill", function(d) { return g.cScale(g.scalardata[d.i]); })
                .on("click", rect_click)
                .on("dblclick", rect_dblclick)
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
