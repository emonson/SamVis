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

	
	$.subscribe("/district/ellipse_click", DISTRICT.visgen);
	$.subscribe("/district/ellipse_click", NETWORK.update_node_scalars);
	$.subscribe("/district/ellipse_hover", DISTRICT.el_hover);
	$.subscribe("/time_center_slider/slide", DISTRICT.time_center_slide_fcn);
	$.subscribe("/time_width_slider/slide", DISTRICT.time_width_slide_fcn);
	$.subscribe("/ellipse_type/change", DISTRICT.ellipse_type_change_fcn);
	$.subscribe("/ellipse_color/change", DISTRICT.ellipse_color_change_fcn);
	$.subscribe("/path_color/change", DISTRICT.path_color_change_fcn);
	$.subscribe("/time_center_button/click", DISTRICT.time_center_click_fcn);
	
	$.subscribe("/network/node_click", NETWORK.update_node_scalars);
	$.subscribe("/network/node_click", DISTRICT.visgen);
	
	// HACK: initial district to center on
	var district_id = 22;
	
	// Generate initial vis
	NETWORK.visgen();
	$.publish("/district/ellipse_click", district_id);
};