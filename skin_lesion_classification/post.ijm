rows = 3;
cName = "C1";
maxPos = 1;
maxi = -9999;
for ( i = 0; i < rows; i ++){
	val = getResult("C1", i);
	if (val > maxi){
		maxi = val;
		maxPos = i + 1;
	}
}

IJ.log("The skin lesion corresponds to:");
if (maxPos == 1){
	IJ.log("benign nevus");
} else if (maxPos == 2){
	IJ.log("malignant melanoma");
} else if (maxPos == 3){
	IJ.log("seborrheic keratosis");
}
