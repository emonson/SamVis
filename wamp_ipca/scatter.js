// --------------------------
// Canvas-based scatterplot

var SCATTER = (function(d3, $, g){

	var sc = { version: '0.0.1' };


	var w_sc = 400;
	var h_sc = 400;
	var padding = 40;

    // ==========================

    var base = d3.select("#embedding");

    var chart = base.append("canvas")
      .attr("width", w_sc)
      .attr("height", h_sc);
    var context = chart.node().getContext("2d");

    // Create an in memory only element of type 'custom'
    var detachedContainer = document.createElement("custom");

    // Create a d3 selection for the detached container. We won't
    // actually be attaching it to the DOM.
    var dataContainer = d3.select(detachedContainer);

    // Function to create our custom data containers
    sc.drawCustom = function(data) {

      var x_scale = d3.scale.linear()
        .range([padding, w_sc-padding])
        .domain(d3.extent(data));
      var y_scale = d3.scale.linear()
        .range([padding, h_sc-padding])
        .domain(d3.extent(data));
  
      var dataBinding = dataContainer.selectAll("custom.rect")
        .data(data, function(d) { return d; });
  
      dataBinding
        .attr("size", 8)
        .transition()
        .duration(1000)
        .attr("size", 15)
        .attr("fillStyle", "green");
  
      dataBinding.enter()
          .append("custom")
          .classed("rect", true)
          .attr("x", x_scale)
          .attr("y", y_scale)
          .attr("size", 8)
          .attr("fillStyle", "red");
  
      dataBinding.exit()
        .attr("size", 8)
        .transition()
        .duration(1000)
        .attr("size", 5)
        .attr("fillStyle", "lightgrey");
    };

    // Function to render out to canvas our custom
    // in memory nodes
    sc.drawCanvas = function() {

      // clear canvas
      context.fillStyle = "#fff";
      context.rect(0,0,chart.attr("width"),chart.attr("height"));
      context.fill();

      // select our dummy nodes and draw the data to canvas.
      var elements = dataContainer.selectAll("custom.rect");
      elements.each(function(d) {
        var node = d3.select(this);

        context.beginPath();
        context.fillStyle = node.attr("fillStyle");
        context.rect(node.attr("x"), node.attr("y"), node.attr("size"), node.attr("size"));
        context.fill();
        context.closePath();

      })
    };

    d3.timer(sc.drawCanvas);
    sc.drawCustom([1,2,13,20,23]);
    sc.drawCustom([1,2,12,16,20]);

    // ==========================

    sc.init_scatterplot = function() {

    };
    
	sc.updateScalarData = function() {
	
		// Update colors 
		
	};

    function useUpdatedContextEllipses(json) {	

        // Flag for keeping track of whether this is the first selection
        var first_selection = (g.foreground_ellipse_data.length == 0);
    
        // Update scale domains
        // data = [[X, Y, RX, RY, Phi, i], ...]
        g.foreground_ellipse_data = json.foreground;
        g.background_ellipse_data = json.background;
        // bounds = [[Xmin, Xmax], [Ymin, Ymax]]
        g.ellipse_bounds = json.bounds;
    
        xScale.domain(g.ellipse_bounds[0]);
        yScale.domain(g.ellipse_bounds[1]);
        xrScale.domain([0, g.ellipse_bounds[0][1]-g.ellipse_bounds[0][0]]);
        yrScale.domain([0, g.ellipse_bounds[1][1]-g.ellipse_bounds[1][0]]);

        // Updating ellipses
        if (first_selection) {
            $.publish("/ellipses/updated", 150);
        }
        else {
            $.publish("/ellipses/updated", 750);
        }
    }

	// Get diffusion embedded points from server
	sc.getContextEllipsesFromServer = function(dim_pair) {
        if (g.comm_method == 'http') {
            d3.json('/' + g.dataset + "/embedding?xdim=" + dim_pair[0] + "&ydim=" + dim_pair[1], useUpdatedContextEllipses );
        } else {
            g.session.call('test.ipca.contextellipses', [], {dataset: g.dataset, 
                                                           id: node_id, 
                                                           bkgdscale: g.bkgd_scale}).then( useUpdatedContextEllipses );
        }
	};

	sc.highlightSelectedEllipse = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select(".el_selected")
			.attr("stroke", function(d,i){return g.cScale(g.scalardata[d[5]]);})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : g.ellipseStrokeWidth;})
			.classed("el_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#e_" + sel_id)
			.attr("stroke", function(d,i){return g.selectColor;})
			.attr("stroke-width", function(d,i){return d[6] == 'background' ? 0 : g.ellipseStrokeWidth;})
			.classed("el_selected", true);
	};

	return el;

}(d3, jQuery, GLOBALS));

// END ELPLOT
// --------------------------
