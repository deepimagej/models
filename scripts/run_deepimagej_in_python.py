import imagej
import os
import traceback
from pathlib import Path
from typing import List, Optional, Tuple, Union

import numpy
import numpy as np
import xarray as xr
from marshmallow import ValidationError

from bioimageio.core import __version__ as bioimageio_core_version, load_resource_description
from bioimageio.core.prediction import predict
from bioimageio.core.prediction_pipeline import create_prediction_pipeline
from bioimageio.core.resource_io.nodes import (
    ImplicitOutputShape,
    Model,
    ParametrizedInputShape,
    ResourceDescription,
    URI,
)
from bioimageio.spec import __version__ as bioimageio_spec_version
from bioimageio.spec.model.raw_nodes import WeightsFormat
from bioimageio.spec.shared.raw_nodes import ResourceDescription as RawResourceDescription

from create_dij_macro immport create_dij_macro


def run_model_with_deepimagej(fiji_dir: Path, 
    model_rdf: Union[URI, Path, str],
    weight_format: Optional[WeightsFormat] = None,
    devices: Optional[List[str]] = None,
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
