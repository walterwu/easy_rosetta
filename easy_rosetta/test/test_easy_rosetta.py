import os
import pytest
import shutil
import sys

#import test_fixtures as fixtures
import test_utils as utils
import defaults as defs
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import core

@pytest.fixture
def setup_test_env():
    shutil.rmtree(defs.TESTING_DIR, ignore_errors=True)
    os.mkdir(defs.TESTING_DIR)
    fasta_file = os.path.join(defs.TESTING_DIR, defs.TEST_PROTEIN_FASTA)
    open(fasta_file, 'w')

def test_setup(setup_test_env):
    config = {
                "name": defs.TEST_PROTEIN_NAME,
                "fasta_file": defs.TEST_PROTEIN_FASTA,
                "working_dir": defs.TESTING_DIR,
                "ignore_config": False,
                "num_cores": 4, 
            }
    core.setup(config, defs.TEST_PROTEIN_FASTA, defs.TEST_PROTEIN_NAME)

    # Checking top level directory structure
    dirs = utils.get_dirs(defs.TESTING_DIR)
    files = utils.get_files(defs.TESTING_DIR)
    expected_files = [os.path.basename(defs.TEST_PROTEIN_FASTA)]
    assert len(files) == len(expected_files), "Found {} instead of {} files"\
                         .format(defs.TESTING_DIR, len(files), len(expected_files))
    for f in expected_files:
        assert f in files, "Expected to find file {} in {}".format(f, defs.TESTING_DIR)
    expected_dirs = ["output", "config"]
    assert len(dirs) == len(expected_dirs),"Found {} instead of {} directories"\
                        .format(defs.TESTING_DIR, len(dirs), len(expected_dirs))
    for d in expected_dirs:
        assert d in dirs, "Expected to find directory {} in {}".format(d, defs.TESTING_DIR)

    # Checking output directory structure
    output_dir = os.path.join(defs.TESTING_DIR, "output")
    dirs = utils.get_dirs(output_dir)
    files = utils.get_files(output_dir)
    assert len(files) == 0, "There should not be any files in {}".format(output_dir)
    expected_dirs = ["worker_0", "worker_1", "worker_2", "worker_3"]
    assert len(dirs) == len(expected_dirs),"Found {} instead of {} directories"\
                        .format(output_dir, len(dirs), len(expected_dirs))
    for d in expected_dirs:
        assert d in dirs, "Expected to find directory {} in {}".format(d, output_dir)

    # Checking config directory structure
    config_dir = os.path.join(defs.TESTING_DIR, "config")
    dirs = utils.get_dirs(output_dir)
    files = utils.get_files(output_dir)
    assert len(files) == 0, "There should not be any files in {}".format(defs.TESTING_DIR)
    expected_dirs = ["worker_0", "worker_1", "worker_2", "worker_3"]
    assert len(dirs) == len(expected_dirs), "Found {} instead of {} directories"\
                        .format(output_dir, len(dirs), len(expected_dirs))
    for d in expected_dirs:
        assert d in dirs, "Expected to find directory {} in {}".format(d, output_dir)






