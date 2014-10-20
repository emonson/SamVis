// --------------------------
// Canvas-based scatterplot

var SCATTER = (function(d3, $, g){

	var sc = { version: '0.0.1' };


	var w_sc = 300;
	var h_sc = 300;
	var padding = 40;
	var default_point_size = 8;
	var highlighted_point_size = 12;

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
            .data(g.embedding, function(d){return d[2];});

        dataBinding
            .transition()
            .duration(750)
            .attr("x", function(d){ return x_scale(d[0]);})
            .attr("y", function(d){ return y_scale(d[1]);})
            .each("start", function(d,i){ 
                if(i===0){
                    d3.timer(sc.drawCanvas);
                }
            })
            .each("end", function(d,i){ 
                if(i===(g.embedding.length-1)){
                    g.stop_drawloop=true; 
                }
            });

        dataBinding.enter()
            .append("custom")
            .classed("rect", true)
            .attr("id", function(d,i){ return "sc_" + i; })
            .attr("x", function(d){ return x_scale(d[0]);})
            .attr("y", function(d){ return y_scale(d[1]);});

        dataBinding.exit()
            .remove();
        
        sc.drawCanvas();
    };

 	var setItemColor = function(d) {
		// Selected overrides basis
		if (d[2] == g.node_id) { return g.selectColor; }
		else { return g.cScale(g.scalardata[d[2]]);}
	};

   // Function to render out to canvas our custom
    // in memory nodes
    
    // Playing around with ways to stop render loop when not needed
    // https://github.com/mbostock/d3/wiki/Force-Layout
    // http://bl.ocks.org/cloudshapes/5662234
    // https://groups.google.com/forum/#!msg/d3-js/WC_7Xi6VV50/j1HK0vIWI-EJ
    // https://github.com/mbostock/d3/blob/master/src/layout/force.js
    
    sc.drawCanvas = function() {
        
        // Using global flag for whether to stop drawloop d3.timer
        if (g.stop_drawloop) {
            // function has to be ready to run next time
            g.stop_drawloop = false;
            return true;
        }
        
        // clear canvas
        context.fillStyle = "#fff";
        context.rect(0,0,chart.attr("width"),chart.attr("height"));
        context.globalAlpha = 1.0;
        context.fill();
        context.globalAlpha = 0.4;

        // select our dummy nodes and draw the data to canvas.
        var elements = dataContainer.selectAll("custom.rect");
        elements.each(function(d) {
            var node = d3.select(this);
            
            context.beginPath();
            if (d[2] == g.node_id) {
                context.fillStyle = g.selectColor;
                context.rect(node.attr("x"), node.attr("y"), highlighted_point_size, highlighted_point_size);
                context.stroke();
            } else {
                context.fillStyle = g.cScale(g.scalardata[d[2]]);
                context.rect(node.attr("x"), node.attr("y"), default_point_size, default_point_size);
            }
            context.fill();
            context.closePath();
      })
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
        x_scale.domain(g.embedding_bounds[0]);
        y_scale.domain(g.embedding_bounds[1]);

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
            g.session.call('test.ipca.contextellipses', [], {dataset: g.dataset, 
                                                                   xdim: g.xdim, 
                                                                   ydim: g.ydim}).then( useUpdatedEmbedding );
        }
	};

	sc.highlightSelectedPoint = function(sel_id) {

		// Unhighlight previously selected ellipse
		d3.select("custom.rect.sc_selected")
			.classed("sc_selected", false);

		// Highlight ellipse corresponding to current rect selection
		d3.select("#sc_" + sel_id)
			.classed("sc_selected", true);
		
		sc.drawCustom();
	};

	return sc;

}(d3, jQuery, GLOBALS));

// END ELPLOT
// --------------------------
