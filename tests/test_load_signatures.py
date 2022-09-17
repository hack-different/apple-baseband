import pathlib
import os
import pytest
import apple_baseband.qualcomm_signature

SIGNATURES_FOLDER = pathlib.Path(os.path.dirname(__file__)).joinpath('fixtures/signatures')

SIGNATURES = [pytest.param(test_file) for test_file in SIGNATURES_FOLDER.glob('*.b01')]


@pytest.mark.parametrize("test_file", SIGNATURES)
def test_load_signature(test_file: pathlib.Path):
    print(test_file)
    signature = apple_baseband.qualcomm_signature.QualcommSignature(test_file.read_bytes())
    assert(signature)
