// --------------------------
// Individual visualization for center and bases for a tree node
// NOTE: required to have var name NODE_BASIS_VIS and implement 
// .getBasisDataFromServer()
//
// "image" data_type – center and bases images
//

var NODE_BASIS_VIS = (function(d3, $, g){

	var nbv = { version: '0.0.1' };

	// Lay out attachment DOM elements needed later
	d3.select("#node_basis_data_vis").append('div').attr('id', 'center_image');
	d3.select("#node_basis_data_vis").append('div').attr('id', 'basis_images');

	// Actual data dimensions
	var img_w_px = g.data_info.original_data.image_n_columns;
	var img_h_px = g.data_info.original_data.image_n_rows;
	// Screen dimensions
	var img_w = 56;
	var img_h = img_w * (img_h_px / img_w_px);
	var n_bases = 0;

	// TODO: Should be resetting image width and height on each read...?
	var center_canvas = d3.select("#center_image").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var center_context = center_canvas.node().getContext("2d");
	var center_image = center_context.createImageData(img_w_px, img_h_px);
	
	// Set up variable number of basis images and canvases
	var b_can;
	var b_con, basis_contexts = [];
	var b_im, basis_images = [];
	
	var set_number_of_images = function(num) {
		var orig_n_images = basis_images.length;
		
		// Don't have enough images
		if (num > orig_n_images) {
			for (var bb = orig_n_images; bb < num; bb++) {
				b_can = d3.select("#basis_images").append("canvas")
							.attr("width", img_w_px)
							.attr("height", img_h_px)
							.attr("class", "basis_im")
							.style("width", img_w + "px")
							.style("height", img_h + "px");
				b_con = b_can.node().getContext("2d");
				b_im = b_con.createImageData(img_w_px, img_h_px);
		
				basis_contexts.push(b_con);
				basis_images.push(b_im);
			}
		}
		// Have too many images
		if (num < orig_n_images) {
			for (var bb = orig_n_images; bb > num; bb--) {
				// Remove first element
				d3.select("#basis_images").select("canvas").remove();
				basis_contexts.shift();
				basis_images.shift();
			}
		}
	};

	// Image color scales
	var center_color = d3.scale.linear()
				.domain([0, 255])
				.range(["#000", "#fff"]);
				
	var bases_color = d3.scale.linear()
				.domain([-1, 0, 1])
				.range(["#A6611A", "#fff", "#018571"]);

	// Get basis images from server
	nbv.getBasisDataFromServer = function(id) {

		d3.json('/' + g.dataset + "/ellipsebasis?id=" + id, function(json) {
	
			g.center_data = json.center;
			g.bases_data = json.bases;

			g.center_range = json.center_range;
			g.bases_range = json.bases_range;
			
			// Adjust number of basis images if necessary
			var n = g.bases_data.length;
			if (n !== n_bases) {
				set_number_of_images(n);
				n_bases = n;
			}

			updateEllipseBasisImages();
		});
	};

	var updateEllipseBasisImages = function() {

		// update color ranges
		center_color.domain(g.center_range);
		// TODO: These aren't quite right -- need to even out range on each side of 0...
		bases_color.domain([g.bases_range[0], 0, g.bases_range[1]]);
		
		for (var y = 0, p = -1; y < g.center_data.length; ++y) {
			var c0 = d3.rgb(center_color(g.center_data[y]));
			center_image.data[++p] = c0.r;
			center_image.data[++p] = c0.g;
			center_image.data[++p] = c0.b;
			center_image.data[++p] = 255;
		}
		// TODO: Need to loop through images!
		for( var im = 0; im < n_bases; im++ ) {
			for (var y = 0, p = -1; y < g.bases_data[0].length; ++y) {
				var c1 = d3.rgb(bases_color(g.bases_data[im][y]));
				basis_images[im].data[++p] = c1.r;
				basis_images[im].data[++p] = c1.g;
				basis_images[im].data[++p] = c1.b;
				basis_images[im].data[++p] = 255;
			}
		}
		center_context.putImageData(center_image, 0, 0);
		for( var im = 0; im < n_bases; im++ ) {
			basis_contexts[im].putImageData(basis_images[im], 0, 0);
		}
	};

	return nbv

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------