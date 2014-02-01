// ===============
// MAIN

window.onload = function() {
	
	// Slider creation
	$('#time_center_slider').slider({
		min: 0,
		max: 1000,
		value: 0,
		slide: function( event, ui ) {
					$.publish("/time_center_slider/slide", ui);
				}  
	});
	$('#time_width_slider').slider({
		min: 0,
		max: 1000,
		value: 0,
		slide: function( event, ui ) {
					$.publish("/time_width_slider/slide", ui);
				}  
	});
	$('#transit_time_color_scale_slider').slider({
		min: 0,
		max: 1000,
		value: 0,
		slide: function( event, ui ) {
					$.publish("/transit_time_color_scale_slider/slide", ui);
				}  
	});
	


	// Set combo boxes to default values before setting callback so can change defaults
	// in globals.js rather than in the html
	$("#ellipse_type").val(GLOBALS.ellipse_type);
	$("#ellipse_color").val(GLOBALS.ellipse_color);
	$("#path_color").val(GLOBALS.path_color);
	
	// BUTTON callback
	$("#path_center").on('click', function() {
		$.publish("/time_center_button/click");
	});

	// COMBO Box callback
	$("#ellipse_type").on('change', function(){
		var type = $(this).val();
		$.publish("/ellipse_type/change", type);
	});

	// COMBO Box callback
	$("#ellipse_color").on('change', function(){
		var type = $(this).val();
		$.publish("/ellipse_color/change", type);
	});

	// COMBO Box callback
	$("#path_color").on('change', function(){
		var type = $(this).val();
		$.publish("/path_color/change", type);
	});

	// Routing all district ellipse and node clicks through this routine
	// so district_id and prev_district get recorded properly
	var district_click_pre_actions = function (district_id) {
		// Initialize first time through
		if (GLOBALS.district_id < 0) {
			GLOBALS.district_id = district_id;
		}
		// Store old center for transfer routines
		GLOBALS.prev_district = GLOBALS.district_id;
		GLOBALS.district_id = district_id
		$.publish("/unknown/district_click", district_id);	
	};
	
	// Route all district clicks through prep stage
	$.subscribe("/district/ellipse_click", district_click_pre_actions);
	$.subscribe("/network/node_click", district_click_pre_actions);
	// then respond to clicks by specific vis afterwards
	$.subscribe("/unknown/district_click", NETWORK.update_node_scalars);
	$.subscribe("/unknown/district_click", DISTRICT.visgen);
	$.subscribe("/unknown/district_click", CENTER_IM.getCenterImageFromServer);

	$.subscribe("/district/ellipse_hover", DISTRICT.el_hover);
	
	$.subscribe("/time_center_slider/slide", DISTRICT.time_center_slide_fcn);
	$.subscribe("/time_width_slider/slide", DISTRICT.time_width_slide_fcn);
	$.subscribe("/transit_time_color_scale_slider/slide", NETWORK.transit_time_color_scale_slide_fcn);
	$.subscribe("/ellipse_type/change", DISTRICT.ellipse_type_change_fcn);
	$.subscribe("/ellipse_color/change", DISTRICT.ellipse_color_change_fcn);
	$.subscribe("/path_color/change", DISTRICT.path_color_change_fcn);
	$.subscribe("/time_center_button/click", DISTRICT.time_center_click_fcn);
	
	
	// HACK: initial district to center on
	var district_id = 22;
	
	// Generate initial vis
	NETWORK.visgen();
	$.publish("/district/ellipse_click", district_id);
};