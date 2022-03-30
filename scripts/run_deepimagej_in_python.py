import imagej
import os

def test_model(
    model_rdf: Union[URI, Path, str],
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
        return test_resource(model, weight_format=weight_format, devices=devices, decimal=decimal)
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


def run_model_with_deepimagej(fiji_dir: Path, 
    model_rdf: Union[URI, Path, str],
    weight_format: Optional[WeightsFormat] = None,
    devices: Optional[List[str]] = None,
    decimal: int = 4,
) -> dict:

    print(fiji_dir)
    ij = imagej.init(os.path.expanduser(fiji_dir) + '/Fiji.app',headless=True)
    ij.getVersion()



    macrotest = """
        run ("Blobs");
        run ("Gaussian Blur...", "sigma=2");
    """

    IJ.runMacro (macrotest)

def test_resource(
    rdf: Union[RawResourceDescription, ResourceDescription, URI, Path, str],
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

                with create_prediction_pipeline(
                    bioimageio_model=model, devices=devices, weight_format=weight_format
                ) as prediction_pipeline:
                    results = predict(prediction_pipeline, inputs)

                if len(results) != len(expected):
                    error = (error or "") + (
                        f"Number of outputs and number of expected outputs disagree: {len(results)} != {len(expected)}"
                    )
                else:
                    for res, exp in zip(results, expected):
                        try:
                            np.testing.assert_array_almost_equal(res, exp, decimal=decimal)
                        except AssertionError as e:
                            error = (error or "") + f"Output and expected output disagree:\n {e}"
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

