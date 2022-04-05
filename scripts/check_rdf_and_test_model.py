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

from run_deepimagej_in_python import run_model_with_deepimagej, download_deepimagej_model
from create_deepimagej_macro import create_dij_macro

def test_model(
    model_rdf: Union[URI, Path, str], 
    fiji_path: Path,
    weight_format: Optional[WeightsFormat] = None,
    devices: Optional[List[str]] = None,
    decimal: int = 4,
) -> dict:
    """Test whether the test output(s) of a model can be reproduced.
    Returns: summary dict with keys: name, status, error, traceback, bioimageio_spec_version, bioimageio_core_version
    """
    # todo: reuse more of 'test_resource'
    tb = None
    try:
        model = load_resource_description(
            model_rdf, weights_priority_order=None if weight_format is None else [weight_format]
        )
    except Exception as e:
        model = None
        error = str(e)
        tb = traceback.format_tb(e.__traceback__)
    else:
        error = None

    if isinstance(model, Model):
        return test_resource(model, fiji_path, weight_format=weight_format, devices=devices, decimal=decimal)
    else:
        error = error or f"Expected RDF type Model, got {type(model)} instead."

    return dict(
        name="reproduced test outputs from test inputs",
        status="failed",
        error=error,
        traceback=tb,
        bioimageio_spec_version=bioimageio_spec_version,
        bioimageio_core_version=bioimageio_core_version,
    )

def test_resource(
    rdf: Union[RawResourceDescription, ResourceDescription, URI, Path, str], fiji_path: Path,
    *,
    weight_format: Optional[WeightsFormat] = None,
    devices: Optional[List[str]] = None,
    decimal: int = 4,
):
    """Test RDF dynamically
    Returns: summary dict with keys: name, status, error, traceback, bioimageio_spec_version, bioimageio_core_version
    """
    error: Optional[str] = None
    tb: Optional = None
    test_name: str = "load resource description"

    try:
        rd = load_resource_description(rdf, weights_priority_order=None if weight_format is None else [weight_format])
    except Exception as e:
        error = str(e)
        tb = traceback.format_tb(e.__traceback__)
    else:
        if isinstance(rd, Model):
            test_name = "reproduced test outputs from test inputs"
            model = rd
            try:
                inputs = [np.load(str(in_path)) for in_path in model.test_inputs]
                expected = [np.load(str(out_path)) for out_path in model.test_outputs]

                assert len(inputs) == len(model.inputs)  # should be checked by validation
                input_shapes = {}
                for idx, (ipt, ipt_spec) in enumerate(zip(inputs, model.inputs)):
                    if not _validate_input_shape(tuple(ipt.shape), ipt_spec.shape):
                        raise ValidationError(
                            f"Shape {tuple(ipt.shape)} of test input {idx} '{ipt_spec.name}' does not match "
                            f"input shape description: {ipt_spec.shape}."
                        )
                    input_shapes[ipt_spec.name] = ipt.shape

                assert len(expected) == len(model.outputs)  # should be checked by validation
                for idx, (out, out_spec) in enumerate(zip(expected, model.outputs)):
                    if not _validate_output_shape(tuple(out.shape), out_spec.shape, input_shapes):
                        error = (error or "") + (
                            f"Shape {tuple(out.shape)} of test output {idx} '{out_spec.name}' does not match "
                            f"output shape description: {out_spec.shape}."
                        )
                
                download_log = download_deepimagej_model(fiji_path, rdf)
                error = (error or "") + download_log
                
                try:
                    run_model_with_deepimagej()
                    create_dij_macro(yaml_url, fiji_path)
                except Exception as e:
                    error = (error or "") + f"Error running the model in DeepImageJ:\n {e}"

            except Exception as e:
                error = str(e)
                tb = traceback.format_tb(e.__traceback__)

    # todo: add tests for non-model resources

    return dict(
        name=test_name,
        status="passed" if error is None else "failed",
        error=error,
        traceback=tb,
        bioimageio_spec_version=bioimageio_spec_version,
        bioimageio_core_version=bioimageio_core_version,
    )

