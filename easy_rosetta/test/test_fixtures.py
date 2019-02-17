import pytest
import os

import defaults as defs

@pytest.fixture
def setup_test_env():
    os.rmdir(defs.TESTING_DIR)
    os.mkdir(defs.TESTING_DIR, exist_ok=True)
    fasta_file = os.path.join(defs.TESTING_DIR, defs.TEST_PROTEIN_FASTA)
    open(fasta_file)



