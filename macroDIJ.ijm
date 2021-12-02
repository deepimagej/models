open("Fiji.app/models/DEFCoN.bioimage.io.model/exampleImage.tif");
selectWindow("exampleImage.tif");
run("DeepImageJ Run", "model=[SMLM Density Map Estimation (DEFCoN)] format=Tensorflow preprocessing=[no preprocessing] postprocessing=[no postprocessing] axes=Y,X,C tile=84,84,1 logging=normal models_dir=Fiji.app/models");
saveAs("PNG", "Fiji.app/models/DEFCoN.bioimage.io.model/test_output.png");
