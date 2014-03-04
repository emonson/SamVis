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
	d3.select("#node_basis_data_vis").append('div').attr('id', 'paralle_coords');

	// d3 setup
	
	// Get basis images from server
	nbv.getBasisDataFromServer = function(id) {

		d3.json(g.data_proxy_root + '/' + g.dataset + "/ellipsebasis?id=" + id, function(json) {
	
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

			// Update visualization
			
		});
	};

	// Update visualization function
	
	return nbv

}(d3, jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------