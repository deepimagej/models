// For non-squared images run the following command. 
name = getTitle();
run("Copy");
newImage("squared_im", "16-bit black", 1024, 1024, 1);
selectWindow("squared_im");
run("Paste");
close(name);

// Regular ImageJ macro code to convert the image into RGB
name = getTitle();
//run("32-bit");
run("Merge Channels...", "c1=" + name + " c2=" + name + " c3=" + name + " create");
