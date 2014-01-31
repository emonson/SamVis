// --------------------------
// Ellipse (district) Center Image

var CENTER_IM = (function(d3, $, g){

	var ci = { version: '0.0.1' };

	// TODO: WARNING: Magic numbers!!!!
	// TODO: If server is feeding arrays as 2d, then can read these values off...
	var img_w_px = 62;
	var img_h_px = 50;
	var img_w = 125;
	var img_h = 100;

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

	// Get basis images from server
	bi.getBasisImagesFromServer = function(id) {

		d3.json(g.data_proxy_root + "/ellipsebasis?id=" + id, function(json) {
	
			// TODO: Should be reading width and height off of data itself
			// TODO: Should be resetting image size if changes...?
			g.ellipse_center_data = json.center;

			g.ellipse_center_range = json.center_range;

			updateEllipseBasisImages();
		});
	};

	var updateEllipseBasisImages = function() {

		// update color ranges
		ellipse_center_color.domain(g.ellipse_center_range);

		for (var y = 0, p = -1; y < img_h_px; ++y) {
			for (var x = 0; x < img_w_px; ++x) {
				var c0 = d3.rgb(ellipse_center_color(g.ellipse_center_data[y][x]));
		
				ellipse_center_image.data[++p] = c0.r;		
				ellipse_center_image.data[++p] = c0.g;	
				ellipse_center_image.data[++p] = c0.b;
				ellipse_center_image.data[++p] = 255;

			}
		}
		ellipse_center_context.putImageData(ellipse_center_image, 0, 0);
	};

	return ci;

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------