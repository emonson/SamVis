// ===============
// MAIN

window.onload = function() {

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
	
	// Do initial scalars retrieval
	UTILITIES.getScalarsFromServer(globals.scalars_name);

	// Initialize icicle view
	// NOTE: This is where scales_by_id and ids_by_scale get created
	ICICLE.init_icicle_view();

	ICICLE.highlightSelectedRect(17);

	ELPLOT.highlightSelectedEllipse(17);
	BASIS_IMS.getBasisImagesFromServer(17);
	ELPLOT.getContextEllipsesFromServer();

};