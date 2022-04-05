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



def download_deepimagej_model(fiji_dir: Path, rdf: YAML_dict):
    # Create the model folder
    os.makedirs(fiji_dir + "//models")
    model_name = rdf.get("name")
    model_dir = fiji_dir + "//models//" + model_name
    os.mkdir(model_dir)
    # Download the files
    model_download = rdf.get("download_url")
    if (model_download not None):
        result = download(model_download, model_dir)
        if (result == None):
            return None
    # If the model was not downloaded with a direct link, download all the needed files
    
    return result + "\n" + download_deepimagej_file_by_file(fiji_dir, rdf)


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


def download_deepimagej_file_by_file(fiji_dir: Path, rdf: YAML_dict):
    error = None
    # Create the model folder
    os.makedirs(fiji_dir + "//models")
    model_name = rdf.get("name")
    model_dir = fiji_dir + "//models//" + model_name
    os.mkdir(model_dir)
    # Download the files
    attachments = rdf.get("attachments")
    if (attachments not None):
        attachments_files =  attachments.get("files")
        if (attachments_files not None):
            for attach in attachments:
                download_result = download(attach, model_dir)
                if (download_result not None):
                    error = (error or "") + "Error downloading attachment " + str(attach) + ".\n"
                    + download_result + "\n"
        else:
            error = (error or "") + "rdf.yaml missing 'attachments>files' field.\n"
    else:
        error = (error or "") + "rdf.yaml missing 'attachments' field.\n"

    rdf_source = rdf.get("rdf_source")
    if (rdf_source not None):
        download_result = download(rdf_source, model_dir)
        if (download_result not None):
            error = (error or "") + "Error downloading rdf_source " + str(rdf_source) + ".\n"
            + download_result + "\n"
    else:
        error = (error or "") + "rdf.yaml missing 'rdf_source' field.\n"

    sample_inputs = rdf.get("sample_inputs")
    if (sample_inputs not None and len(sample_inputs) > 0):
        for ss in sample_inputs:
            download_result = download(ss, model_dir)
            if (download_result not None):
                error = (error or "") + "Error downloading sample_input " + str(ss) + ".\n"
                + download_result + "\n"
    else:
        error = (error or "") + "rdf.yaml missing 'sample_inputs' field.\n"

    sample_outputs = rdf.get("sample_outputs")
    if (sample_outputs not None and len(sample_outputs) > 0):
        for ss in sample_outputs:
            download_result = download(ss, model_dir)
            if (download_result not None):
                error = (error or "") + "Error downloading sample_output " + str(ss) + ".\n"
                + download_result + "\n"
    else:
        error = (error or "") + "rdf.yaml missing 'sample_outputs' field.\n"

    test_inputs = rdf.get("test_inputs")
    if (test_inputs not None and len(test_inputs) > 0):
        for ss in test_inputs:
            download_result = download(ss, model_dir)
            if (download_result not None):
                error = (error or "") + "Error downloading test_input " + str(ss) + ".\n"
                + download_result + "\n"
    else:
        error = (error or "") + "rdf.yaml missing 'test_inputs' field.\n"

    test_outputs = rdf.get("test_outputs")
    if (test_outputs not None and len(test_outputs) > 0):
        for ss in test_outputs:
            download_result = download(ss, model_dir)
            if (download_result not None):
                error = (error or "") + "Error downloading test_output " + str(ss) + ".\n"
                + download_result + "\n"
    else:
        error = (error or "") + "rdf.yaml missing 'test_outputs' field.\n"
    # Download the weights
    weights = rdf.get("weights")
    if (weights not None and type(weights) == dict):
        for kk, vv in weights.items():
            if (type(vv) == dict and vv.get("source") not None):
                download_result = download(vv.get("source"), model_dir)
                if (download_result not None):
                    error = (error or "") + "Error downloading weights " + str(vv.get("source")) + ".\n"
                    + download_result + "\n"
            else:
                error = (error or "") + "error downloading weights.\n"
    else:
        error = (error or "") + "rdf.yaml missing 'weights' field.\n"
    return error