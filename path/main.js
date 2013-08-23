// ===============
// MAIN

window.onload = function() {
	

$(function(){

	// Slider
	$('#slider').dragslider({
		animate: true,
		range: true,
		rangeDrag: true,
		values: [30, 70],
		slide: function( event, ui ) {
					$( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
				}  
	});
});

	$.subscribe("/district/ellipse_click", DISTRICT.visgen);
	$.subscribe("/district/ellipse_hover", DISTRICT.el_hover);
	
	// HACK: initial district to center on
	var district_id = 162;
	
	// Generate initial vis
	DISTRICT.visgen(district_id);
};