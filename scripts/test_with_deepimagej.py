import traceback
from pathlib import Path
from typing import Optional

import typer

from bioimageio.core.resource_tests import test_model
from bioimageio.spec.shared import yaml


def write_summary(
    p: Path, *, name: str, status: str, error: Optional[str] = None, reason: Optional[str] = None, **other
):
    p.parent.mkdir(parents=True, exist_ok=True)
    if status == "failed":
        reason = "error"
        assert error is not None
    elif status != "passed":
        assert reason is not None

    yaml.dump(dict(name=name, status=status, error=error, reason=reason, **other), p)


def write_test_summaries(rdf_dir: Path, resource_id: str, version_id: str, 
    summaries_dir: Path, fiji_path: Path, postfix: str):
    for rdf_path in rdf_dir.glob(f"{resource_id}/{version_id}/rdf.yaml"):
        test_name = "reproduce test outputs with deepimagej <todo version> (draft)"
        error = None
        status = None
        reason = None
        try:
            rdf = yaml.load(rdf_path)
        except Exception as e:
            error = f"Unable to load rdf: {e}"
            status = "failed"
            rdf = {}

        rd_id = rdf.get("id")
        if rd_id is None or not isinstance(rd_id, str):
            print(
                f"::warning file=scripts/test_with_deepimagej.py,line=37,endline=41,title=Invalid RDF::"
                f"Missing/invalid 'id' in rdf {str(rdf_path.relative_to(rdf_dir).parent)}"
            )
            continue

        if rdf.get("type") != "model":
            status = "skipped"
            reason = "not a model RDF"

        weight_formats = list(rdf.get("weights", []))
        if not isinstance(weight_formats, list) or not weight_formats:
            status = "failed"
            error = f"Missing/invalid weight formats for {rd_id}"

        if status:
            # write single test summary
            write_summary(
                summaries_dir / rd_id / f"test_summary_{postfix}.yaml", name=test_name, status=status, error=error, reason=reason
            )
            continue

        # write test summary for each weight format
        for weight_format in weight_formats:
            try:
                summary = test_model(rdf_path, fiji_path, weight_format=weight_format)
            except Exception as e:
                summary = dict(error=str(e), traceback=traceback.format_tb(e.__traceback__))

            summary["name"] = f"{test_name} using {weight_format} weights"
            write_summary(summaries_dir / rd_id / f"test_summary_{weight_format}_{postfix}.yaml", **summary)


def main(
    dist: Path,
    resource_id: str,
    version_id: str = "**",
    rdf_dir: Path = Path(__file__).parent / "../bioimageio-gh-pages/rdfs",
    postfix: str = ""
):
    """ preliminary deepimagej check

    only checks if test outputs are reproduced for Tensorflow 1 or torchscript.

    """
    summaries_dir = dist / "test_summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)
    write_test_summaries(rdf_dir, resource_id, version_id, summaries_dir, postfix)


if __name__ == "__main__":
    typer.run(main)
