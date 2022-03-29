import json
from itertools import product
from pathlib import Path
from typing import Dict, Union

import typer

from test_with_ilastik import write_test_summaries


def iterate_over_gh_matrix(matrix: Union[str, Dict[str, list]]):
    if isinstance(matrix, str):
        matrix = json.loads(matrix)

    assert isinstance(matrix, dict), matrix
    if "exclude" in matrix:
        raise NotImplementedError("matrix:exclude")

    elif "include" in matrix:
        if len(matrix) > 1:
            raise NotImplementedError("matrix:include with other keys")

        yield from matrix["include"]

    else:
        keys = list(matrix)
        for vals in product(*[matrix[k] for k in keys]):
            yield dict(zip(keys, vals))


def main(
    dist: Path,
    pending_matrix: str,
    rdf_dir: Path = Path(__file__).parent / "../bioimageio-gh-pages/rdfs",
    postfix: str = "",
):
    """preliminary ilastik check

    only checks if test outputs are reproduced for Tensorflow 1 or torchscript weights .

    """
    summaries_dir = dist / "test_summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    for matrix in iterate_over_gh_matrix(pending_matrix):
        resource_id = matrix["resource_id"]
        version_id = matrix["version_id"]

        write_test_summaries(rdf_dir, resource_id, version_id, summaries_dir, postfix)


if __name__ == "__main__":
    typer.run(main)
