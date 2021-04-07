imageName = getTitle();
imageNameNoExtension = substring(imageName, 0, lastIndexOf(imageName, "."));
// Set the path where all the masks are stored
// path = "/home/user/Desktop/fiji-linux64/Fiji.app/models/skin_lessions_pytorch/mask" + File.separator + imageNameNoExtension + ".png"; 

// Choose a directory to store all the results
workingDir = getDirectory("Select the skin lesions model directory at ImageJ/models/ or Fiji/models/");
// path = workingDir + File.separator + imageNameNoExtension + ".png"; 
path = workingDir + File.separator + imageNameNoExtension + "_mask.png"
// Open the mask to use it as reference
open(path);
selectWindow(imageNameNoExtension + "_mask.png");
h = getHeight();
w = getWidth();
topMost = 0;
leftMost = 0;
bottomMost = h;
rightMost = w;

cont = 1;
// Find the leftmost non-zero pixel

i = 1;
j = 1;
while (cont == 1 && i < w) {
	j = 1;
	while (cont == 1 && j < h) {
		pixel = getPixel(i, j);
		if (pixel != 0){
			cont = 0;
			leftMost = i;
		}
		j += 1;
	}
	i += 1;
}

// Find the topmost non-zero pixel
cont = true;
i = leftMost;
j = 1;
while (cont && j < h){
	i = leftMost;
	while (cont && i < w){
		pixel = getPixel(i, j);
		if (pixel != 0){
			cont = false;
			topMost = j;
		}
		i += 1;
	}
	j += 1;
}

// Find the rightmost non-zero pixel
cont = true;
i = w;
j = h;
while (cont && i > leftMost){
	j = h;
	while (cont && j > topMost){
		pixel = getPixel(i, j);
		if (pixel != 0){
			cont = false;
			rightMost = i;
		}
		j -= 1;
	}
	i -= 1;
}


// Find the bottommost non-zero pixel
cont = true;
i = rightMost;
j = h;
while (cont && j > topMost){
	i = rightMost;
	while (cont && i > leftMost){
		pixel = getPixel(i, j);
		if (pixel != 0){
			cont = false;
			bottomMost = j;
		}
		i -= 1;
	}
	j -= 1;
}

close(imageNameNoExtension + ".png");

selectWindow(imageName);

leftMost = leftMost - 15;
if (leftMost < 0){
	leftMost = 0;
}
topMost = topMost - 15;
if (topMost < 0){
	topMost = 0;
}
rightMost = rightMost + 15;
if (rightMost > w){
	rightMost = w;
}
bottomMost = bottomMost + 15;
if (bottomMost > h){
	bottomMost = h;
}

// Crop to a rectangle containing only the mask and 15 pixels extra per side
makeRectangle(leftMost, topMost, rightMost - leftMost, bottomMost - topMost);
run("Crop");

// Rescale to rectangle whose smaller side is minSide in our case 256)
minSide = 256;
randSide = 224;
h = bottomMost - topMost;
w = rightMost - leftMost;
if (h > w){
	new_h = minSide * h / w;
	new_w = minSide
	rand_h = floor(random * (new_h - randSide * h / w));
	rand_w = floor(random * (new_w - randSide));
	hRandSide = randSide * h / w;
	wRandSide = randSide;
} else if (h < w){
	new_w = minSide * w / h;
	new_h = minSide;
	rand_w = floor(random * (new_w - randSide * w / h));
	rand_h = floor(random * (new_h - randSide));
	hRandSide = randSide;
	wRandSide = randSide * w / h;
} else if (h == w) {
	new_h = minSide;
	new_w = minSide;
	rand_h = floor(random * (new_h - randSide));
	rand_w = floor(random * (new_w - randSide));
	hRandSide = randSide;
	wRandSide = randSide;
}
// Scale
run("Scale...", "x=- y=- width=" + new_w +" height=" + new_h + " interpolation=Bilinear average create");
newName = getTitle();
close(imageName);
selectWindow(newName);
rename(imageName);



// Do a random crop to obtain an image whose smaller side is randSide (in our case 224)
makeRectangle(rand_w, rand_h, wRandSide, hRandSide);
run("Crop");

// Convert the RGB image into RGB stack and Normalize 
//run("RGB Stack");
run("Split Channels");
run("Merge Channels...", "c1=[C1-"+imageName+"] c2=[C2-"+imageName+"] c3=[C3-"+imageName+"] create");

bitD = bitDepth();
if (bitD == 8){
	factor = 255;
} else if (bitD == 16){
	factor = 65535;
} else if (bitD == 32){
	getMinAndMax(min, max);
	factor =  max;
}
// First divive all the values by the maximum possible value
run("32-bit");
run("Divide...", "value=" + factor + " stack");

setSlice(1);
run("Subtract...", "value=0.485 slice");
run("Divide...", "value=0.229 slice");
setSlice(2);
run("Subtract...", "value=0.456 slice");
run("Divide...", "value=0.224 slice");
setSlice(3);
run("Subtract...", "value=0.406 slice");
run("Divide...", "value=0.225 slice");
