// --------------------------
// Ellipse (district) Center Image

var CENTER_IM = (function(d3, $, g){

	var ci = { version: '0.0.1' };

	// TODO: WARNING: Magic numbers!!!!
	// TODO: If server is feeding arrays as 2d, then can read these values off...
	var img_w_px = 125;
	var img_h_px = 100;
	var img_w = 125;
	var img_h = 100;

	// TODO: Should be resetting image width and height on each read...?
	var district_center_canvas = d3.select("#district_center_image").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var district_center_context = district_center_canvas.node().getContext("2d");
	var district_center_image = district_center_context.createImageData(img_w_px, img_h_px);
	var district_center_color = d3.scale.linear()
				.domain([0, 255])
				.range(["#000", "#fff"]);

	// Get basis images from server
	ci.getCenterImageFromServer = function(id) {
		console.log("center image " + id);
		d3.json(g.data_proxy_root + '/' + g.dataset + "/districtcenterdata?district_id=" + id, function(json) {
	
			g.district_center_data = json.data;
			g.district_center_data_dims = json.data_dims;
			g.district_center_range = json.data_range;

			// TODO: Should be resetting image size if changes...?
			img_h_px = g.district_center_data_dims[0];
			img_w_px = g.district_center_data_dims[1];

			updateEllipseBasisImages();
		});
	};

	var updateEllipseBasisImages = function() {

		// update color ranges
		district_center_color.domain(g.district_center_range);

		for (var y = 0, p = -1; y < img_h_px; ++y) {
			for (var x = 0; x < img_w_px; ++x) {
				var c0 = d3.rgb(district_center_color(g.district_center_data[y][x]));
		
				district_center_image.data[++p] = c0.r;		
				district_center_image.data[++p] = c0.g;	
				district_center_image.data[++p] = c0.b;
				district_center_image.data[++p] = 255;

			}
		}
		district_center_context.putImageData(district_center_image, 0, 0);
	};

	return ci;

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------