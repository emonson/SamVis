// --------------------------
// Ellipse plot variables

var NETWORK = (function(d3, $, g){

	var net = { version: '0.0.1' };

	var w = 300,
			h = 300;
	
	var c_scale = d3.scale.linear()
									.domain([0, 1])
									.range(["#F00", "#000"]);

	var zoom = function() {
		vis.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
	};

	var svg = d3.select("#network_overview").append("svg")
			.attr("width", w)
			.attr("height", h)
		.append("g")
			.call(d3.behavior.zoom().scaleExtent([0.25, 8]).on("zoom", zoom))
		.append("g");

	svg.append("rect")
			.attr("class", "overlay")
			.attr("width", w)
			.attr("height", h);

	var vis = svg.append("g");
	
	var set_node_fill_color = function(d,i) {
		switch(g.node_color) {
			case 'time':
				return c_scale(g.nodescalars[d.i]);
				break;
			default:
				return 'black';
				break;
		}
	};

	var set_node_stroke_color = function(d,i) {
		switch(g.node_color) {
			case 'time':
				return c_scale(g.nodescalars[d.i]);
				break;
			default:
				return 'black';
				break;
		}
	};

	// Define the force-directed layout algorithm
	var force = d3.layout.force()
			.size([w, h])
			.charge(-120)
			.gravity(0.15)
			.linkDistance(30);
		
	var update_force = function() {		
		// Set the data for the force-directed layout
		force.nodes(g.nodes)
				 .links(g.edges)
				 .start();
	};
	
	net.visgen = function() {
		
		d3.json( g.data_proxy_root + '/' + g.dataset + '/transitiongraph', function(error, graph) {
		// d3.json("http://emo2.trinity.duke.edu/remote9004/json_20130813/transitiongraph", function(error, graph) {
	
			// Store network data in global variable stash
			g.nodes = graph.nodes;
			g.edges = graph.edges;
		
		update_force();
		net.update_network();
			
		}); // d3.json()
		
	} // visgen
	
	net.update_network = function() {
		
		// Edges
		var link = vis.selectAll(".link")
				.data(g.edges, function(d){return d.i;});
		
		link.enter()
			.append("svg:path")
				.attr("class", "link");
		
		link.exit()
			.remove();
		
		// Nodes
		var node = vis.selectAll(".node")
				.data(g.nodes, function(d){return d.i;});
				
		node.enter()
			.append("circle")
				.attr("class", "node")
				.attr("id", function(d) {return "n_" + d.i;})
				// .attr("r", 5)
				.attr("r", function(d){ return 0.25*Math.sqrt(d.t); })
				.attr("fill", set_node_fill_color )
				.attr("stroke", set_node_stroke_color )
				.call(force.drag)
				.on('click', function(d) {
							$.publish("/network/node_click", d.i);
						})
				// keep the node drag mousedown from triggering pan
				.on("mousedown", function() { d3.event.stopPropagation(); })
			.append("title")
				.text(function(d) { return d.i; });
		
		node.exit()
			.remove();

		// Time step update function used in force-directed layout
		force.on("tick", function() {
		
			link.attr("d", function(d) {
				var prec = 5;
				var tx = d.target.x,
						ty = d.target.y,
						sx = d.source.x,
						sy = d.source.y,
						v = 0.5*Math.sqrt(d.v);
				var d = Math.sqrt((tx-sx)*(tx-sx) + (ty-sy)*(ty-sy)),
						vx = v*(ty-sy)/d,
						vy = v*(tx-sx)/d;
				var sxplus = sx + vx,
						sxminus = sx - vx,
						syplus = sy + vy,
						syminus = sy - vy;
				return "M" +
						tx.toPrecision(prec) + "," + ty.toPrecision(prec) + "L" +
						sxplus.toPrecision(prec) + "," + syminus.toPrecision(prec) + "L" +
						sxminus.toPrecision(prec) + "," + syplus.toPrecision(prec) + "Z";
			});
		
			node.attr("cx", function(d) { return d.x; })
					.attr("cy", function(d) { return d.y; });
	
		}); // force.on
	};
	
	net.update_node_scalars = function(district_id) {
		
		d3.json( g.data_proxy_root + '/' + g.dataset + '/timesfromdistrict?district_id='+ district_id, function(error, data) {

			g.nodescalars = data.avg_time_to_district;
			// NOTE: Rescaling colors with each time range!!!
			c_scale.domain([0, d3.mean(g.nodescalars)/2]);
			net.update_node_colors();
			net.highlight_selected_node();
			
		}); // d3.json()
		
	};
	
	net.update_node_colors = function() {
	
		// Update colors in both visualizations when this returns
		svg.selectAll(".node")
				.attr("fill", set_node_fill_color )
				.attr("stroke", set_node_stroke_color );
		
	};

	net.highlight_selected_node = function() {
		
		// Unhighlight previously selected node
		// TODO: use g.prev_district_id
		d3.select(".nd_selected")
			.classed("nd_selected", false);
		
		// Highlight node corresponding to current selection
		d3.select("#n_" + g.district_id)
			.classed("nd_selected", true);
	};

	return net;

}(d3, jQuery, GLOBALS));

// END DISTRICT
// --------------------------
