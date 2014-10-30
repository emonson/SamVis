// --------------------------
// Ellipse plot variables

var SCATTER = (function(d3, $, g){

	var sc = { version: '0.0.1' };

    // resizable: http://eyeseast.github.io/visible-data/2013/08/28/responsive-charts-with-d3/
    
    var w_frac = 0.65;
	var w_el = $("#embedding_container").width() * w_frac;
	var aspect = 350/350; // height/width
	var h_el = aspect * w_el;
	var bl_pad = 30;
	var tr_pad = 10;
	var default_point_size = 6;
	var highlighted_point_size = 12;

	// Ellipse plot scale functions with placeholder domains
	var xScale = d3.scale.linear().domain([0, 1]).range([bl_pad, w_el - tr_pad]);
	var yScale = d3.scale.linear().domain([0, 1]).range([h_el - bl_pad, tr_pad]);

	// Define X axis
	var xAxis = d3.svg.axis()
						.scale(xScale)
						.orient("bottom")
						.ticks(0);

	// Define Y axis
	var yAxis = d3.svg.axis()
						.scale(yScale)
						.orient("left")
						.ticks(0);

	// Ellipse plot SVG element
	var svg_base = d3.select("#embedding")
				.append("svg")
				.attr("width", w_el)
				.attr("height", h_el);
// 				.on("mouseout", function() {
// 					$.publish("/plot/mouseout", g.node_id);
// 				});
    
	// Ellipse plot axes
	svg_base.append("g")
		.attr("class", "x axis");
	svg_base.append("g")
		.attr("class", "y axis");
	
	var svg = svg_base.append("g");
	
	var xlabel = svg.append("text")
        .attr("class", "x axislabel")
        .attr("text-anchor", "middle")
        .attr("x", (w_el - bl_pad - tr_pad)/2.0 + bl_pad)
        .attr("y", h_el - bl_pad/4.0)
        .text( g.xdim );
        
	var ylabel = svg.append("text")
        .attr("class", "y axislabel")
        .attr("text-anchor", "middle")
        .attr("x", bl_pad/2.0)
        .attr("y", h_el - (h_el - bl_pad - tr_pad)/2.0 - bl_pad)
        .text( g.ydim );
        
    sc.resize = function() {
        w_el = $("#embedding_container").width() * w_frac;
        h_el = aspect * w_el;

        svg_base.attr("width", w_el);
        svg_base.attr("height", h_el);

        xScale.range([bl_pad, w_el - tr_pad]);
        yScale.range([h_el - bl_pad, tr_pad]);

	    xlabel.attr("x", (w_el - bl_pad - tr_pad)/2.0 + bl_pad).attr("y", h_el - bl_pad/4.0);
	    ylabel.attr("x", bl_pad/2.0).attr("y", h_el - (h_el - bl_pad - tr_pad)/2.0 - bl_pad);

        sc.updatePoints(0.001);
        updateAxes();
    };

	var updateAxes = function() {
		
		//Update X axis
		svg_base.select(".x.axis")
		    .attr("transform", "translate(0," + (h_el - bl_pad) + ")")
			.call(xAxis);

		//Update Y axis
		svg_base.select(".y.axis")
		    .attr("transform", "translate(" + bl_pad + ",0)")
			.call(yAxis);
	};
	
	// Adding transformation and axis call to axes
	updateAxes();

	var hoverfctn = function(d) {
		$.publish("/node/hover", d[2]);
	};

	// Ellipse click function (update projection basis)
	var clickfctn = function() {
				
		var that = this;

		// Not changing projection basis if pressing alt
		if (d3.event && $("#scatter_treezoom_button").hasClass("active")) {
			$.publish("/node/alt_click", that.__data__[2]);
		}
		else if (d3.event && $("#scatter_info_button").hasClass("active")) {
		    $.publish("/node/info", that.__data__[2]);
		}
		else {
			g.node_id = that.__data__[2];
			$.publish("/node/click", that.__data__[2]);
		}
	};
	
 	var setItemColor = function(d) {
		// Selected overrides basis
		// if (d[2] == g.node_id) { return g.selectColor; }
		// else { return g.cScale(g.scalardata[d[2]]);}
		return g.cScale(g.scalardata[d[2]]);
	};

 	var setPointSize = function(d) {
		// return d[2] == g.node_id ? highlighted_point_size : default_point_size;
		return default_point_size;
	};

	sc.updateScalarData = function() {
	
		// Update colors in both visualizations when this returns
		svg.selectAll("circle")
				.attr("fill", setItemColor);
		
	};

	sc.updateActiveNodes = function() {
	    
		// Unhighlight previously active icicle rectangles
		d3.selectAll(".sc_active")
			.classed("sc_active", false);

		// Go through foreground ellipses and mark as "active"
		for (var ii=0; ii < g.foreground_ellipse_data.length; ii++) {
		    var sel_id = g.foreground_ellipse_data[ii][5];
            d3.select("#sc_" + sel_id)
                .classed('sc_active', true); 
		}
	};
	
	sc.updatePoints = function(trans_dur) {
	
		// Default value for transition duration
		trans_dur = trans_dur || 500;
		
		// Check if this is the first time through
		var initial_circle_count = svg.selectAll("circle").size();
	
		// Update the circles
		// data = [[X, Y, i], ...]
		var els = svg.selectAll("circle")
				.data(g.embedding, function(d){return d[2];});
	
		els.transition()
			.duration(trans_dur)		
				.attr("cx", function(d) { return xScale(d[0]); })
				.attr("cy", function(d) { return yScale(d[1]); })
				.attr("r", setPointSize)
				.attr("fill", setItemColor);
	
		els.enter()
			.append("circle")
				.attr("id", function(d) {return "sc_" + d[2];})
				.attr("cx", function(d) { return xScale(d[0]); })
				.attr("cy", function(d) { return yScale(d[1]); })
				.attr("r", setPointSize)
				.attr("fill", setItemColor)
					.on("click", clickfctn)
					.on("mouseover", hoverfctn);
	
		els.exit()
			.remove();
	
		xlabel.text( g.xdim );
		ylabel.text (g.ydim );
		
		updateAxes();
		
		if (initial_circle_count == 0) {
		    $.publish("/scatter/initialized");
		}
	};
	
	sc.resort_points = function() {
		// Reorder plot points so current scale is at the top of drawing order
		
		// Make an array with current scale at the beginning, going to max_scale, then top scales last
		// e.g. [3, 4, 5, 6, 0, 1, 2] and put current scale at top in sort
		scales = [];
		for (var ii=0; ii <= g.max_scale; ii++) { scales.push(ii); }
		scales.rotate(g.scales_by_id[g.node_id]);
		scales_rev_lookup = {};
		for (var ii=0; ii < scales.length; ii++) { scales_rev_lookup[scales[ii]] = ii; }

		var els = svg.selectAll("circle")
		els.sort(function(a,b) {
		    return scales_rev_lookup[g.scales_by_id[b[2]]] - scales_rev_lookup[g.scales_by_id[a[2]]];
		});
	};

    function useUpdatedEmbedding(json) {	

        // Flag for keeping track of whether this is the first selection
        var first_selection = (g.embedding.length == 0);
        
        // Update data store
        // data = [[X, Y], [X, Y], ...]
        g.embedding = json.data;
        // bounds = [[Xmin, Xmax], [Ymin, Ymax]]
        g.embedding_bounds = json.bounds;
        
        // Update plot scaling domains
        xScale.domain(g.embedding_bounds[0]);
        yScale.domain(g.embedding_bounds[1]);

        // Broadcast that the data has been updated
        if (first_selection) {
            $.publish("/embedding/updated", 150);
        }
        else {
            $.publish("/embedding/updated", 750);
        }
    }

	// Get diffusion embedded points from server
	sc.getEmbeddingFromServer = function() {
        if (g.comm_method == 'http') {
            d3.json('/' + g.dataset + "/embedding?xdim=" + g.xdim + "&ydim=" + g.ydim, useUpdatedEmbedding );
        } else {
            g.session.call('test.ipca.embedding', [], {dataset: g.dataset, 
                                                                   xdim: g.xdim, 
                                                                   ydim: g.ydim}).then( useUpdatedEmbedding );
        }
	};

	sc.highlightSelectedPoint = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select(".sc_selected")
			.classed("sc_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#sc_" + sel_id)
			.classed("sc_selected", true);
			
	    // NOTE: Right now just using CSS to color selected point. Would need
	    //   to call update on data if want to change size of selected point.
	    
	    // NOTE: Resorting on each selection right now!!
	    sc.resort_points();
	};

	return sc;

}(d3, jQuery, GLOBALS));

// END ELPLOT
// --------------------------
