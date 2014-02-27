// --------------------------
// Ellipse (district) Center 1D Function plot

var CENTER_VIS = (function(d3, $, g){

	var ci = { version: '0.0.1' };

	// Append vis-specific div
	d3.select("#district_center_data_vis").append('div').attr('id', 'district_center_func');

	// Actual data dimensions (px)
	var img_h_px = g.data_shape[0];
	var img_w_px = g.data_shape[1];
	// Screen dimensions (px)
	var img_h = 75;
	var img_w = 150;

	// TODO: Should be resetting image width and height on each read...?
	var district_center_canvas = d3.select("#district_center_func").append("canvas")
				.attr("width", img_w_px)
				.attr("height", img_h_px)
				.style("width", img_w + "px")
				.style("height", img_h + "px");
	var district_center_context = district_center_canvas.node().getContext("2d");
	var district_center_image = district_center_context.createImageData(img_w_px, img_h_px);
	var district_center_color = d3.scale.linear()
				.domain(g.data_bounds)
				.range(["#000", "#ff0"]);

	// Get basis images from server
	ci.getCenterDataFromServer = function(id) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/districtcenterdata?district_id=" + id, function(json) {
	
			g.district_center_data = json.data;
			g.district_center_data_dims = json.data_dims;
			g.district_center_range = json.data_range;

			// TODO: Should be resetting image size if changes...?
			img_h_px = g.district_center_data_dims[0];
			img_w_px = g.district_center_data_dims[1];

			updateImage();
		});
	};

	var updateImage = function() {

		// update color ranges
		// district_center_color.domain(g.district_center_range);

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