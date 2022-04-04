import imagej
import os
import traceback
from pathlib import Path
from typing import List, Optional, Tuple, Union
import os
import requests

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


def download_deepimagej_model(fiji_dir: Path, rdf: YAML_dict):
    # Create the model folder
    os.makedirs(fiji_dir + "//models")
    model_name = rdf.get("name")
    model_dir = fiji_dir + "//models//" + model_name
    os.mkdir(model_dir)
    # Download the files
    download(rdf.get(""), model_dir)

def download(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_") 
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return None
    else:  # HTTP status code 4XX/5XX
        error = "Download failed: status code {}\n{}".format(r.status_code, r.text)
        print(error)
        return error



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
