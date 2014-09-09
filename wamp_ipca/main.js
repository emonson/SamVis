// ===============
// MAIN

window.onload = function() {

	// Populate scalars select 
	// http://stackoverflow.com/questions/3446069/populate-dropdown-select-with-array-using-jquery
	var update_scalar_names_combobox = function() {
        $.each(GLOBALS.scalar_names, function(val, text) {
            $('#scalars_name').append( $('<option></option>').val(text).html(text) )
        });
	};
	
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
	
	function load_individual_vis() {
	    INDIV.load_individual_vis();
	};
	
	function set_individual_subscriptions() {
        $.subscribe("/icicle/rect_click", NODE_BASIS_VIS.getBasisDataFromServer);
        // $.subscribe("/icicle/rect_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/icicle/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_click", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);	
	};
	
    // Initialization
    $.subscribe("/connection/open", UTILITIES.get_data_info);
	$.subscribe("/data_info/loaded", update_scalar_names_combobox);
	$.subscribe("/data_info/loaded", load_individual_vis);
	$.subscribe("/individual_vis/loaded", set_individual_subscriptions);
	// Do initial scalars retrieval
	// TODO: This may need to be timed for before icicle and ellipse plot vis...
	$.subscribe("/data_info/loaded", UTILITIES.getScalarsFromServer);
	// NOTE: This is where scales_by_id and ids_by_scale get created
	$.subscribe("/data_info/loaded", ICICLE.init_icicle_view);
	$.subscribe("/data_info/loaded", ELPLOT.getContextEllipsesFromServer);
	
	
	// Normal operation
	$.subscribe("/scalars/change", UTILITIES.getScalarsFromServer);
	$.subscribe("/scalars/updated", ELPLOT.updateScalarData);
	$.subscribe("/scalars/updated", ICICLE.updateScalarData);
    
	$.subscribe("/icicle/rect_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/icicle/rect_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/icicle/rect_click", ICICLE.highlightSelectedRect);
	$.subscribe("/icicle/rect_alt_click", ICICLE.zoomIcicleView);
	
	$.subscribe("/elplot/ellipse_click", ELPLOT.getContextEllipsesFromServer);
	$.subscribe("/elplot/ellipse_click", ELPLOT.highlightSelectedEllipse);
	$.subscribe("/elplot/ellipse_click", ICICLE.highlightSelectedRect);
	$.subscribe("/elplot/ellipse_alt_click", ICICLE.zoomIcicleView);

	$.subscribe("/ellipses/updated", ELPLOT.updateEllipses);
	
	// TODO: Right now don't have it set up so there's a way to wait for the icicle data
	//   to come back and then highlight an initial selection, which will populate the 
	//   ellipse plot and grab images...
};