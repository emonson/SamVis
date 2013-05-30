// ===============
// MAIN

window.onload = function() {

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