// --------------------------
// Basis Images

var BASIS_IMS = (function(d3, $, g){

	var bi = { version: '0.0.1' };

	// TODO: WARNING: Magic numbers!!!!
	// TODO: If server is feeding arrays as 2d, then can read these values off...
	var img_w_px = 28;
	var img_h_px = 28;
	var img_w = 56;
	var img_h = 56;

	// TODO: Should be resetting image width and height on each read...?
	var ellipse_center_canvas = d3.select("#ellipse_center_image").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var ellipse_center_context = ellipse_center_canvas.node().getContext("2d");
	var ellipse_center_image = ellipse_center_context.createImageData(img_w_px, img_h_px);
	var ellipse_center_color = d3.scale.linear()
				.domain([0, 255])
				.range(["#000", "#fff"]);

	var ellipse_basis1_canvas = d3.select("#ellipse_basis1_image").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var ellipse_basis1_context = ellipse_basis1_canvas.node().getContext("2d");
	var ellipse_basis1_image = ellipse_basis1_context.createImageData(img_w_px, img_h_px);

	var ellipse_basis2_canvas = d3.select("#ellipse_basis2_image").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var ellipse_basis2_context = ellipse_basis2_canvas.node().getContext("2d");
	var ellipse_basis2_image = ellipse_basis2_context.createImageData(img_w_px, img_h_px);

	var ellipse_bases_color = d3.scale.linear()
				.domain([-1, 0, 1])
				.range(["#A6611A", "#fff", "#018571"]);

	// Get basis images from server
	bi.getBasisImagesFromServer = function(id) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/ellipsebasis?id=" + id, function(json) {
	
			// TODO: Should be reading width and height off of data itself
			// TODO: Should be resetting image size if changes...?
			g.ellipse_center_data = json.center;
			g.ellipse_bases_data = json.bases;

			g.ellipse_center_range = json.center_range;
			g.ellipse_bases_range = json.bases_range;

			updateEllipseBasisImages();
		});
	};

	var updateEllipseBasisImages = function() {

		// update color ranges
		ellipse_center_color.domain(g.ellipse_center_range);
		// TODO: These aren't quite right -- need to even out range on each side of 0...
		ellipse_bases_color.domain([g.ellipse_bases_range[0],0,g.ellipse_bases_range[1]]);
		
		for (var y = 0, p = -1; y < g.ellipse_center_data.length; ++y) {
				var c0 = d3.rgb(ellipse_center_color(g.ellipse_center_data[y]));
		
				ellipse_center_image.data[++p] = c0.r;
				ellipse_center_image.data[++p] = c0.g;
				ellipse_center_image.data[++p] = c0.b;
				ellipse_center_image.data[++p] = 255;

		}
		// TODO: Need to loop through images!
			for (var y = 0, p = -1; y < g.ellipse_bases_data[0].length; ++y) {
				var c1 = d3.rgb(ellipse_bases_color(g.ellipse_bases_data[0][y]));
				var c2 = d3.rgb(ellipse_bases_color(g.ellipse_bases_data[1][y]));
		
				ellipse_basis1_image.data[++p] = c1.r;
				ellipse_basis2_image.data[p] = c2.r;
				ellipse_basis1_image.data[++p] = c1.g;
				ellipse_basis2_image.data[p] = c2.g;
				ellipse_basis1_image.data[++p] = c1.b;
				ellipse_basis2_image.data[p] = c2.b;
				ellipse_basis1_image.data[++p] = 255;
				ellipse_basis2_image.data[p] = 255;

		}
		ellipse_center_context.putImageData(ellipse_center_image, 0, 0);
		ellipse_basis1_context.putImageData(ellipse_basis1_image, 0, 0);
		ellipse_basis2_context.putImageData(ellipse_basis2_image, 0, 0);
	};

	return bi;

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------