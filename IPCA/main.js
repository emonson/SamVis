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
	
	$.subscribe("/icicle/rect_click", NODE_BASIS_VIS.getBasisDataFromServer);
	$.subscribe("/icicle/rect_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/icicle/rect_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/icicle/rect_click", ICICLE.highlightSelectedRect);
	
	$.subscribe("/icicle/rect_hover", NODE_BASIS_VIS.getBasisDataFromServer);
	$.subscribe("/icicle/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);
	
	$.subscribe("/elplot/ellipse_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/elplot/ellipse_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/elplot/ellipse_click", ICICLE.highlightSelectedRect);
	$.subscribe("/elplot/ellipse_click", NODE_BASIS_VIS.getBasisDataFromServer);

	$.subscribe("/elplot/ellipse_hover", NODE_BASIS_VIS.getBasisDataFromServer);
	$.subscribe("/elplot/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);

	$.subscribe("/ellipses/updated", ELPLOT.updateEllipses);
	
	function initialSelection() {
	    GLOBALS.node_id = GLOBALS.root_node_id;
	    $.publish("/icicle/rect_click", GLOBALS.node_id);
	};
    $.subscribe("/icicle/initialized", initialSelection);
	
	// Initialize icicle view
	// NOTE: This is where scales_by_id and ids_by_scale get created
	ICICLE.init_icicle_view();
	
	// Do initial scalars retrieval
	UTILITIES.getScalarsFromServer();

};