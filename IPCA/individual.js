// --------------------------
// Node basis individual visualization loading based on data_type

var INDIV = (function($, g){

	var ind = { version: '0.0.1' };
	
	ind.load_individual_vis = function() {
        // Now load individual ellipse center visualization based on data type
        // Load nothing if 
        switch (g.data_info.original_data.dataset_type) {
            case 'image':
                $.ajax({
                    url:'/basisims.js',
                    async:false,
                    dataType:'script',
                    success:function(response) {
                        console.log( "loaded image script" );
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        console.log( xhr + ajaxOptions + thrownError + "Triggered ajaxError handler." );
                    }
                });	
                break;
            case 'gene':
                $.ajax({
                    url:'/basispcoords.js',
                    async:false,
                    dataType:'script',
                    success:function(response) {
                        console.log( "loaded function script" );
                    },
                    error: function (xhr, ajaxOptions, thrownError) {
                        console.log( xhr + ajaxOptions + thrownError + "Triggered ajaxError handler." );
                    }
                });	
                break;
        }
        $.publish("/individual_vis/loaded");
	};

	return ind;

}(jQuery, GLOBALS));

// END BASIS IMAGES
// --------------------