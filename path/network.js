// --------------------------
// Ellipse plot variables

var NETWORK = (function(d3, $, g){

	var net = { version: '0.0.1' };

	var w = 300,
			h = 300,
			fill = d3.scale.category20();

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
	
	// TODO: track down why this doesn't work if you declare as
	// var zoom = function() {...
	function zoom() {
		vis.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
	};

	var force = d3.layout.force()
			.size([w, h])
			.charge(-120)
			.gravity(0.15)
			.linkDistance(30);
		
	net.visgen = function() {
		
		d3.json( g.data_proxy_root + '/' + g.dataset + '/transitiongraph', function(error, graph) {
		// d3.json("http://emo2.trinity.duke.edu/remote9004/json_20130813/transitiongraph", function(error, graph) {
	
			force
					.nodes(graph.nodes)
					.links(graph.edges)
					.start();

			var link = vis.selectAll(".link")
					.data(graph.edges)
				.enter().append("svg:path")
					.attr("class", "link");

			var node = vis.selectAll(".node")
					.data(graph.nodes)
				.enter().append("circle")
					.attr("class", "node")
					// .attr("r", 5)
					.attr("r", function(d){ return 0.25*Math.sqrt(d.t); })
					// .style("fill", function(d) { return color(d.group); })
					.call(force.drag)
					// keep the node drag mousedown from triggering pan
					.on("mousedown", function() { d3.event.stopPropagation(); });

			node.append("title")
					.text(function(d) { return d.i; });

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
			
		}); // d3.json()
		
	} // visgen

	return net;

}(d3, jQuery, GLOBALS));

// END DISTRICT
// --------------------------
