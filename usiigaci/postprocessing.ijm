// Regular ImageJ macro code to merge the obtained masks

selectWindow("finalMask");

getDimensions(width, height, channels, slices, frames);

for (s=1;s<=slices;s++){
	setSlice(s);
	run("Multiply...", "value="+s+" slice");	
	}
run("Z Project...", "projection=[Max Intensity]");
run("glasbey");
