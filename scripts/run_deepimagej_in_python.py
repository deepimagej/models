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


def run_model_with_deepimagej(fiji_dir: str,
    macro_call: str,
    decimal: int = 4,
) -> dict:

    print("EXECUTING THE FOLLOWING MACRO:")
    print(macro_call)
    ij = imagej.init(os.path.expanduser(fiji_dir) + '/Fiji.app',headless=True)
    ij.getVersion()

    # Check that the example tif exists

    IJ.runMacro (macro_call)


