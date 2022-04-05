import imagej
import os
import traceback
from pathlib import Path
from typing import List, Optional, Tuple, Union
import os
import requests
from ruamel.yaml import YAML

import numpy
import numpy as np
import xarray as xr
from marshmallow import ValidationError
from ruamel.yaml import YAML


def run_model_with_deepimagej(fiji_dir: Path,
    macro_call: str,
    path_to_image: str,
    decimal: int = 4,
) -> dict:

    print(fiji_dir)
    ij = imagej.init(os.path.expanduser(fiji_dir) + '/Fiji.app',headless=True)
    ij.getVersion()

    # Check that the example tif exists


    macrotest = """
        open("/home/runner/Fiji.app/models/DEFCoN.bioimage.io.model/exampleImage.tif");
        selectWindow("exampleImage.tif");
        run("DeepImageJ Run", "model=[SMLM Density Map Estimation (DEFCoN)] format=Tensorflow preprocessing=[no preprocessing] postprocessing=[no postprocessing] axes=Y,X,C tile=84,84,1 logging=normal models_dir=/home/runner/Fiji.app/models");
        saveAs("PNG", "/home/runner/Fiji.app/models/DEFCoN.bioimage.io.model/test_output.png");
    """

    IJ.runMacro (macrotest)


