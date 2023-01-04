#Remove previous installations of Fiji if they exist
rm -rf $HOME/Fiji.app/
wget https://downloads.imagej.net/fiji/archive/20221201-1017/fiji-linux64.zip
unzip fiji-linux64.zip -d $HOME
# fix FilamentDetector issue (not necessary anymore, non existent file in the last version)
#mv $HOME/Fiji.app/jars/FilamentDetector-1.0.0.jar $HOME/Fiji.app/jars/FilamentDetector-1.0.0.jar.disabled
##$HOME/Fiji.app/ImageJ-linux64 --update add-update-site DeepImageJ https://sites.imagej.net/DeepImageJ/
##$HOME/Fiji.app/ImageJ-linux64 --update update
#rm $HOME/Fiji.app/jars/jna-4*.jar

wget https://github.com/deepimagej/deepimagej-plugin/releases/download/2.1.15/dependencies_2115.zip
unzip dependencies_2115.zip
mv dependencies_2115/dependencies_2.1.15/* $HOME/Fiji.app/jars/

wget https://github.com/deepimagej/deepimagej-plugin/releases/download/2.1.15/DeepImageJ_-2.1.15.jar
#Add the -f mode to deal with the case of non existent diji instalations
rm  -f $HOME/Fiji.app/plugins/DeepImageJ*.jar
mv DeepImageJ_-2.1.15.jar $HOME/Fiji.app/plugins/DeepImageJ_-2.1.15.jar
#python3 -c "import imagej;ij = imagej.init('$HOME/Fiji.app');print('pyimagej initialized.')"
#export DISPLAY=:1
#Xvfb $DISPLAY -screen 0 1024x768x16 &

# Execution of a specific model with headless mode (done in the CI workflows)
#wget  https://zenodo.org/record/4608442/files/SMLM_Density%20Map_Estimation_%28DEFCoN%29.bioimage.io.model.zip
#mkdir -p $HOME/Fiji.app/models/DEFCoN.bioimage.io.model
#unzip 'SMLM_Density Map_Estimation_(DEFCoN).bioimage.io.model.zip' -d $HOME/Fiji.app/models/DEFCoN.bioimage.io.model/
#$HOME/Fiji.app/ImageJ-linux64 --headless --console -macro macroDIJ.ijm
