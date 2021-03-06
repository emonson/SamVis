// ===============
// MAIN

// http://stackoverflow.com/questions/1985260/javascript-array-rotate

// Array.prototype.rotate = (function() {
//     // save references to array functions to make lookup faster
//     var push = Array.prototype.push,
//         splice = Array.prototype.splice;
// 
//     return function(count) {
//         var len = this.length >>> 0, // convert to uint
//             count = count >> 0; // convert to int
// 
//         // convert count to value in range [0, len[
//         count = ((count % len) + len) % len;
// 
//         // use splice.call() instead of this.splice() to make function generic
//         push.apply(this, splice.call(this, 0, count));
//         return this;
//     };
// })();

Array.prototype.rotate = (function() {
    var unshift = Array.prototype.unshift,
        splice = Array.prototype.splice;

    return function(count) {
        var len = this.length >>> 0,
            count = count >> 0;

        unshift.apply(this, splice.call(this, count % len, len));
        return this;
    };
})();

window.onload = function() {

	// Gray out main panels until a real dataset is loaded
	if (!GLOBALS.dataset) {
        $('.row').css({'opacity':0.3});
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
                                  "/" + GLOBALS.uri.file + 
                           "?data=" + text;
            $('#dataset_name').append( $('<option></option>').val(pg_url).html(text) )
        });
        
        // Set default selection to current dataset, or "init" if none chosen in URL data= query
	    if (GLOBALS.dataset) {
            var pg_url = "http://" + GLOBALS.server_conf.server_name + 
                                  ":" + GLOBALS.server_conf.ipca_http_port + 
                                  "/" + GLOBALS.uri.file + 
                           "?data=" + GLOBALS.dataset;
	        $("#dataset_name").val(pg_url);
	    } else {
	        $("#dataset_name").val("init");
	    }
	    
        // And set callback function
	    // http://stackoverflow.com/questions/13709716/open-a-new-webpage-from-a-combo-box-onclick-event-for-the-option-selected
        $("#dataset_name").on('change', function(){
            window.open(this.value, '_self');
        });
	};
	
	// Take focus away from buttons after being depressed
	// http://stackoverflow.com/questions/23443579/how-to-stop-buttons-from-staying-depressed-with-bootstrap-3
	$(".btn").mouseup(function(){
	    $(this).blur();
	});
		
	// -------------
	// Embedding scatter
	
	var dim_increment = function() {
	    if (GLOBALS.has_embedding && (GLOBALS.ydim < GLOBALS.n_embedding_dims-1)) {
            GLOBALS.xdim += 1;
            GLOBALS.ydim += 1;
            dim_button_check_disabled();
            $.publish("/embedding/dims_updated");
	    }
	};
	
	var dim_decrement = function() {
	    if (GLOBALS.has_embedding && (GLOBALS.xdim > 1)) {
            GLOBALS.xdim -= 1;
            GLOBALS.ydim -= 1;
            dim_button_check_disabled();
            $.publish("/embedding/dims_updated");
	    }
	};
    
	var dim_reset = function() {
	    if (GLOBALS.has_embedding) {
            GLOBALS.xdim = 1;
            GLOBALS.ydim = 2;
            dim_button_check_disabled();
            $.publish("/embedding/dims_updated");
	    }
	};
	
	var dim_button_check_disabled = function() {
        $("#dim_increment").toggleClass("disabled", (GLOBALS.ydim == GLOBALS.n_embedding_dims-1));
        $("#dim_decrement").toggleClass("disabled", (GLOBALS.xdim == 1));
	};
    
    // Send out message on window resize
    // $(window).resize(function(){ $.publish("/window/resize"); });
    // Debounced window resize
    $(window).resize( debounce( function(){ $.publish("/window/resize"); }, 250) );

    // Debounce (as opposed to throttling) so resize doesn't happen until movement done
    // http://colingourlay.github.io/presentations/reusable-responsive-charts-with-d3js/#/54
    //
    // window.addEventListener("resize", debounce(function () {
    //     var width = $(chart.base.node().parentNode).width();
    //     chart.width(width);
    // }, 250), false);
    function debounce(fn, wait) {
        var timeout;

        return function () {
            var context = this,              // preserve context
                args = arguments,            // preserve arguments
                later = function () {        // define a function that:
                    timeout = null;          // * nulls the timeout (GC)
                    fn.apply(context, args); // * calls the original fn
                };

            // (re)set the timer which delays the function call
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
	// -------------
    // Tool buttons
    
	// Embedding dimension increment/decrement callbacks
	$("#dim_increment").tooltip({container:'body', delay:{'show':1000}}).click(dim_increment);
	$("#dim_decrement").tooltip({container:'body', delay:{'show':1000}}).click(dim_decrement);
	$("#dim_reset").tooltip({container:'body', delay:{'show':500}}).click(dim_reset);
	$("#scatter_select_button").tooltip({container:'body', delay:{'show':500}});
	$("#scatter_info_button").tooltip({container:'body', delay:{'show':500}});
	
	// Icicle plot tools
	$("#tree_select_button").tooltip({container:'body', delay:{'show':500}});
	$("#tree_info_button").tooltip({container:'body', delay:{'show':500}});
	$("#tree_treezoom_button").tooltip({container:'body', delay:{'show':500}});
	$("#tree_reset_button").tooltip({container:'body', delay:{'show':500}}).click(ICICLE.reset_zoom);

	// Ellipse plot tools
	$("#graph_select_button").tooltip({container:'body', delay:{'show':500}}).click(ICICLE.reset_zoom);
	$("#graph_info_button").tooltip({container:'body', delay:{'show':500}});
	$("#graph_treezoom_button").tooltip({container:'body', delay:{'show':500}});

	// -------------
	
	// Callback : After icicle initialized, make inital selection
	function makeInitialSelection() {
	    GLOBALS.node_id = GLOBALS.root_node_id;
	    $.publish("/node/click", GLOBALS.node_id);
	}
	
	// Callback : Only subscribe individual vis after JS loaded
	function set_individual_subscriptions() {
        // $.subscribe("/node/hover", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/node/info", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/plot/mouseout", NODE_BASIS_VIS.getBasisDataFromServer);
        $.subscribe("/node/click", NODE_BASIS_VIS.getBasisDataFromServer);
	}
	
	// Callback : Only dataset names should be loaded if there is no valid dataset name passed in URL data= query
    function set_have_dataset_subscriptions() {
        if ($.inArray(GLOBALS.dataset, GLOBALS.dataset_names) >= 0) {
            // Remove lowered opacity when really have dataset
            $('.row').removeAttr('style');
            
            $.subscribe("/data_info/loaded", update_scalar_names_combobox);
            $.subscribe("/data_info/loaded", INDIV.load_individual_vis);
            $.subscribe("/data_info/loaded", UTILITIES.getScalarsFromServer);

            $.subscribe("/embedding/dims_updated", SCATTER.getEmbeddingFromServer);
            $.subscribe("/embedding/updated", SCATTER.updatePoints);

            $.subscribe("/individual_vis/loaded", set_individual_subscriptions);
        
            // NOTE: This is where scales_by_id and ids_by_scale get created
            $.subscribe("/scalars/initialized", ICICLE.init_icicle_view);
            $.subscribe("/icicle/initialized", SCATTER.getEmbeddingFromServer);
            // TODO: Figure out a way to only make initial selection once all are initialized...
            $.subscribe("/scatter/initialized", makeInitialSelection);
            // $.subscribe("/scatter/initialized", makeInitialSelection);
    
            // Normal operation after initializations
            $.subscribe("/scalars/change", UTILITIES.getScalarsFromServer);
            $.subscribe("/scalars/updated", ELPLOT.updateScalarData);
            $.subscribe("/scalars/updated", ICICLE.updateScalarData);
            $.subscribe("/scalars/updated", SCATTER.updateScalarData);
    
            $.subscribe("/node/click", ELPLOT.highlightSelectedEllipse);
            $.subscribe("/node/click", ELPLOT.getContextEllipsesFromServer);
            $.subscribe("/node/click", ICICLE.highlightSelectedRect);
            $.subscribe("/node/click", SCATTER.highlightSelectedPoint);
            $.subscribe("/node/alt_click", ICICLE.zoomIcicleView);
    
            $.subscribe("/ellipses/updated", ELPLOT.updateEllipses);
            $.subscribe("/ellipses/updated", ICICLE.updateActiveNodes);
            $.subscribe("/ellipses/updated", SCATTER.updateActiveNodes);
            
            // window resize
            $.subscribe("/window/resize", ELPLOT.resize);
            $.subscribe("/window/resize", ICICLE.resize);
            $.subscribe("/window/resize", SCATTER.resize);
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
