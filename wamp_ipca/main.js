// ===============
// MAIN

window.onload = function() {

	// Populate scalars select 
	// http://stackoverflow.com/questions/3446069/populate-dropdown-select-with-array-using-jquery
	var update_scalar_names_combobox = function() {
        $.each(GLOBALS.scalar_names, function(val, text) {
            $('#scalars_name').append( $('<option></option>').val(text).html(text) )
        });
	    
	    // Set default value
	    $("#scalars_name").val(GLOBALS.scalars_name);
	    
	    // Set callback on change
        $("#scalars_name").on('change', function(){
            var name = $(this).val();
            GLOBALS.scalars_name = name;
            $.publish("/scalars/change");
        });
	};
	
	// Populate datasets names / links select 
	var update_dataset_names_combobox = function() {
        $('#dataset_name').append( $('<option></option>').val("init").html("Select a dataset") )
        $.each(GLOBALS.dataset_names, function(val, text) {
            var pg_url = "http://" + GLOBALS.server_conf.server_name + 
                                  ":" + GLOBALS.server_conf.ipca_http_port + 
                                  "/" + GLOBALS.server_conf.vis_page + 
                           "?data=" + text;
            $('#dataset_name').append( $('<option></option>').val(pg_url).html(text) )
        });
        
        // Set default selection to current dataset
	    if (GLOBALS.dataset) {
	        $("#dataset_name").val(location.toString());
	    } else {
	        $("#dataset_name").val("init");
	    }
	    
        // And set callback function
	    // http://stackoverflow.com/questions/13709716/open-a-new-webpage-from-a-combo-box-onclick-event-for-the-option-selected
        $("#dataset_name").on('change', function(){
            window.open(this.value, '_self');
        });
	};
	
	// Scalar aggregation functions. Hard coded in globals for now, so just load in combobox
	$.each(GLOBALS.scalar_aggregators, function(val, text) {
        $('#scalars_aggregator').append( $('<option></option>').val(text).html(text) )
    });


	// Set combo boxes to default values before setting callback so can change defaults
	// in globals.js rather than in the html
	$("#scalars_aggregator").val(GLOBALS.scalars_aggregator);

	// COMBO Box callback
	$("#scalars_aggregator").on('change', function(){
		var agg = $(this).val();
		GLOBALS.scalars_aggregator = agg;
		$.publish("/scalars/change");
	});
	
	function set_individual_subscriptions() {
        $.subscribe("/icicle/rect_click", NODE_BASIS_VIS.getBasisDataFromServer);
        // $.subscribe("/icicle/rect_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/icicle/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_click", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);	
	};
	
    // Initialization
    $.subscribe('/dataset_names/acquired', update_dataset_names_combobox);
	$.subscribe("/data_info/loaded", update_scalar_names_combobox);
	$.subscribe("/data_info/loaded", INDIV.load_individual_vis);
	$.subscribe("/individual_vis/loaded", set_individual_subscriptions);
    $.subscribe("/connection/open", UTILITIES.get_data_info);
    $.subscribe("/connection/open", UTILITIES.get_dataset_names);
	
	// Do initial scalars retrieval
	$.subscribe("/data_info/loaded", UTILITIES.getScalarsFromServer);
	
	// NOTE: This is where scales_by_id and ids_by_scale get created
	$.subscribe("/scalars/updated", ICICLE.init_icicle_view);
	
	function initialSelection() {
	    GLOBALS.node_id = GLOBALS.root_node_id;
	    $.publish("/icicle/rect_click", GLOBALS.node_id);
	};
    $.subscribe("/icicle/initialized", initialSelection);
	
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
	
	// See if connection has already been made / comm_method established
	if (GLOBALS.comm_method) {
	    $.publish('/connection/open');
	}
};