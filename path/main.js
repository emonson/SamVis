// ===============
// MAIN

window.onload = function() {
	

	$.subscribe("/district/ellipse_click", DISTRICT.visgen);
	$.subscribe("/district/ellipse_hover", DISTRICT.el_hover);
	$.subscribe("/slider/slide", DISTRICT.slide_fcn);
	$.subscribe("/ellipse_type/change", DISTRICT.ellipse_type_change_fcn);
	$.subscribe("/path_color/change", DISTRICT.path_color_change_fcn);
	
	// HACK: initial district to center on
	var district_id = 17;
	
	// Generate initial vis
	DISTRICT.visgen(district_id);
};