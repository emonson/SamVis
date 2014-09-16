// ===============
// MAIN

window.onload = function() {

	// Gray out main panels until a real dataset is loaded
	if (!GLOBALS.dataset) {
        $('#left_panel').css({'opacity':0.3});
        $('#right_panel').css({'opacity':0.3});
	}
	
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
	    // Place a selection to sit if no dataset was chosen in URL data= query
        $('#dataset_name').append( $('<option></option>').val("init").html("Select a dataset") )
        // Loop through the actual data set names
        $.each(GLOBALS.dataset_names, function(val, text) {
            var pg_url = "http://" + GLOBALS.server_conf.server_name + 
                                  ":" + GLOBALS.server_conf.ipca_http_port + 
                                  "/" + GLOBALS.server_conf.vis_page + 
                           "?data=" + text;
            $('#dataset_name').append( $('<option></option>').val(pg_url).html(text) )
        });
        
        // Set default selection to current dataset, or "init" if none chosen in URL data= query
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
	
	var update_scalar_aggregators_combobox = function() {
        // Scalar aggregation functions. Hard coded in globals for now, so just load in combobox
        $.each(GLOBALS.scalar_aggregators, function(val, text) {
            $('#scalars_aggregator').append( $('<option></option>').val(text).html(text) )
        });

        // Set combo boxes to default values before setting callback so can change defaults
        // in globals.js rather than in the html
        $("#scalars_aggregator").val(GLOBALS.scalars_aggregator);

        // Set callback on scalars aggregator combo box change
        $("#scalars_aggregator").on('change', function(){
            var agg = $(this).val();
            GLOBALS.scalars_aggregator = agg;
            $.publish("/scalars/change");
        });
	};
	
	// Callback : After icicle initialized, make inital selection
	function makeInitialSelection() {
	    GLOBALS.node_id = GLOBALS.root_node_id;
	    $.publish("/icicle/rect_click", GLOBALS.node_id);
	}
	
	// Callback : Only subscribe individual vis after JS loaded
	function set_individual_subscriptions() {
        $.subscribe("/icicle/rect_click", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/icicle/rect_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/icicle/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_click", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/ellipse_hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/elplot/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);	
	}
	
	// Callback : Only dataset names should be loaded if there is no valid dataset name passed in URL data= query
    function set_have_dataset_subscriptions() {
        if ($.inArray(GLOBALS.dataset, GLOBALS.dataset_names) >= 0) {
            // Remove lowered opacity when really have dataset
            $('#left_panel').removeAttr('style');
            $('#right_panel').removeAttr('style');
            
            $.subscribe("/data_info/loaded", update_scalar_names_combobox);
            $.subscribe("/data_info/loaded", update_scalar_aggregators_combobox);
            $.subscribe("/data_info/loaded", INDIV.load_individual_vis);
            $.subscribe("/data_info/loaded", UTILITIES.getScalarsFromServer);
            $.subscribe("/individual_vis/loaded", set_individual_subscriptions);
        
            // NOTE: This is where scales_by_id and ids_by_scale get created
            $.subscribe("/scalars/initialized", ICICLE.init_icicle_view);
            $.subscribe("/icicle/initialized", makeInitialSelection);
    
            // Normal operation after initializations
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
        }
	}
	
    // Initialization
    $.subscribe("/connection/open", UTILITIES.get_dataset_names);
    $.subscribe('/dataset_names/acquired', update_dataset_names_combobox);
    $.subscribe('/dataset_names/acquired', set_have_dataset_subscriptions);
	// Need at least a dataset name (doesn't have to be valid) to try to get data_info
	if (GLOBALS.dataset) {
            $.subscribe("/connection/open", UTILITIES.get_data_info);	
	}
	    
	// Now that everything else is loaded, figure out type of connection
	UTILITIES.establish_connection()
};