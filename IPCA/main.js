// ===============
// MAIN

window.onload = function() {

	// Populate scalars select 
	// http://stackoverflow.com/questions/3446069/populate-dropdown-select-with-array-using-jquery
	$.each(GLOBALS.scalar_names, function(val, text) {
					$('#scalars_name').append( $('<option></option>').val(text).html(text) )
				});
	$.each(GLOBALS.scalar_aggregators, function(val, text) {
					$('#scalars_aggregator').append( $('<option></option>').val(text).html(text) )
				});


	// Set combo boxes to default values before setting callback so can change defaults
	// in globals.js rather than in the html
	$("#scalars_name").val(GLOBALS.scalars_name);
	$("#scalars_aggregator").val(GLOBALS.scalars_aggregator);

	// COMBO Box callback
	$("#scalars_name").on('change', function(){
		var name = $(this).val();
		GLOBALS.scalars_name = name;
		$.publish("/scalars/change");
	});
	
	$("#scalars_aggregator").on('change', function(){
		var agg = $(this).val();
		GLOBALS.scalars_aggregator = agg;
		$.publish("/scalars/change");
	});
	
	$.subscribe("/scalars/change", UTILITIES.getScalarsFromServer);
	$.subscribe("/scalars/updated", ELPLOT.updateScalarData);
	$.subscribe("/scalars/updated", ICICLE.updateScalarData);
	
	$.subscribe("/icicle/rect_click", BASIS_IMS.getBasisImagesFromServer);
	$.subscribe("/icicle/rect_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/icicle/rect_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/icicle/rect_click", ICICLE.highlightSelectedRect);
	
	$.subscribe("/icicle/rect_hover", BASIS_IMS.getBasisImagesFromServer);
	$.subscribe("/icicle/mouseout", BASIS_IMS.getBasisImagesFromServer);
	
	$.subscribe("/elplot/ellipse_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/elplot/ellipse_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/elplot/ellipse_click", ICICLE.highlightSelectedRect);
	$.subscribe("/elplot/ellipse_click", BASIS_IMS.getBasisImagesFromServer);

	$.subscribe("/elplot/ellipse_hover", BASIS_IMS.getBasisImagesFromServer);
	$.subscribe("/elplot/mouseout", BASIS_IMS.getBasisImagesFromServer);

	$.subscribe("/ellipses/updated", ELPLOT.updateEllipses);
	

	// Initialize icicle view
	// NOTE: This is where scales_by_id and ids_by_scale get created
	ICICLE.init_icicle_view();
	ELPLOT.getContextEllipsesFromServer();
	
	// Do initial scalars retrieval
	UTILITIES.getScalarsFromServer();

	// TODO: Right now don't have it set up so there's a way to wait for the icicle data
	//   to come back and then highlight an initial selection, which will populate the 
	//   ellipse plot and grab images...
};