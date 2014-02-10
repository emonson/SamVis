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
	

	// Initialize icicle view
	// NOTE: This is where scales_by_id and ids_by_scale get created
	ICICLE.init_icicle_view();
	ELPLOT.getContextEllipsesFromServer();
	
	// Do initial scalars retrieval
	UTILITIES.getScalarsFromServer(GLOBALS.scalars_name);

	// TODO: Right now don't have it set up so there's a way to wait for the icicle data
	//   to come back and then highlight an initial selection, which will populate the 
	//   ellipse plot and grab images...
};