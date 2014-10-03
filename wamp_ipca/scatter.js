// --------------------------
// Canvas-based scatterplot

var SCATTER = (function(d3, $, g){

	var sc = { version: '0.0.1' };


	var w_sc = 400;
	var h_sc = 400;
	var padding = 40;

    var x_scale = d3.scale.linear()
        .range([padding, w_sc-padding])
        .domain([0, 1]);
    var y_scale = d3.scale.linear()
        .range([padding, h_sc-padding])
        .domain([0, 1]);
  
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
    sc.drawCustom = function() {

        var dataBinding = dataContainer.selectAll("custom.rect")
            .data(g.embedding);

        dataBinding
            .attr("size", 8)
            .transition()
            .duration(1000)
            .attr("size", 15)
            .attr("fillStyle", "green");

        dataBinding.enter()
            .append("custom")
            .classed("rect", true)
            .attr("id", function(d,i){ return "sc_" + i; })
            .attr("x", function(d){ return x_scale(d[0]);})
            .attr("y", function(d){ return y_scale(d[1]);})
            .attr("size", 8)
            .attr("fillStyle", "red");

        dataBinding.exit()
            .attr("size", 8)
            .transition()
            .duration(1000)
            .attr("size", 5)
            .attr("fillStyle", "lightgrey");
        
        sc.drawCanvas();
    };

    // Function to render out to canvas our custom
    // in memory nodes
    sc.drawCanvas = function() {

        // clear canvas
        context.fillStyle = "#cac";
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

    // d3.timer(sc.drawCanvas);
    // sc.drawCustom([1,2,13,20,23]);
    // sc.drawCustom([1,2,12,16,20]);

    // ==========================

	sc.updateScalarData = function() {
	
		// Update colors 
		
	};

    function useUpdatedEmbedding(json) {	

        // Flag for keeping track of whether this is the first selection
        var first_selection = (g.embedding.length == 0);
        console.log("useUPdatedEmbedding");
        
        // Update scale domains
        // data = [[X, Y], [X, Y], ...]
        g.embedding = json.data;
        // bounds = [[Xmin, Xmax], [Ymin, Ymax]]
        g.embedding_bounds = json.bounds;
    
        x_scale.domain(g.embedding_bounds[0]);
        y_scale.domain(g.embedding_bounds[1]);

        // Updating ellipses
        if (first_selection) {
            $.publish("/embedding/updated", 150);
        }
        else {
            $.publish("/embedding/updated", 750);
        }
    }

	// Get diffusion embedded points from server
	sc.getEmbeddingFromServer = function() {
	    console.log('getting embedding from server');
        if (g.comm_method == 'http') {
            d3.json('/' + g.dataset + "/embedding?xdim=" + g.xdim + "&ydim=" + g.ydim, useUpdatedEmbedding );
        } else {
            g.session.call('test.ipca.contextellipses', [], {dataset: g.dataset, 
                                                                   xdim: g.xdim, 
                                                                   ydim: g.ydim}).then( useUpdatedEmbedding );
        }
	};

	sc.highlightSelectedEllipse = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select("custom.rect.sc_selected")
			.classed("el_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#sc_" + sel_id)
			.classed("el_selected", true);
	};

	return sc;

}(d3, jQuery, GLOBALS));

// END ELPLOT
// --------------------------
