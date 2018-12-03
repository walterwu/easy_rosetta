import os
import utils

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "data/configs/default_config")
SESSIONS_PATH = os.path.join(os.path.dirname(__file__), "data/userdata/sessions")

NUM_CORES = 1
NUM_STRUCTS = 1
NUM_NODES = 1

FRAGMENT_FLAGS_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "data/templates/fragment_flags_template")
ABINITIO_FLAGS_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "data/templates/abinitio_flags_template")
SAVIO_JOB_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "data/templates/savio_job_template")

WORKING_DIR = "/global/scratch/walterwu/"
ROSETTA_PATH = "${ROSETTA3}"
FRAGMENT_PICKER_SCRIPT = os.path.join(ROSETTA_PATH, "bin/fragment_picker.linuxgccrelease")
ABINITIO_RELAX_SCRIPT = os.path.join(ROSETTA_PATH, "bin/AbinitioRelax.linuxgccrelease")
SCORE_SCRIPT = os.path.join(ROSETTA_PATH, "bin/score_jd2.linuxgccrelease")
# FRAGMENT_PICKER_SCRIPT = os.path.join(ROSETTA_PATH, "bin/fragment_picker.macosclangrelease")
# ABINITIO_RELAX_SCRIPT = os.path.join(ROSETTA_PATH, "bin/AbinitioRelax.macosclangrelease")
# SCORE_SCRIPT = os.path.join(ROSETTA_PATH, "bin/score_jd2.macosclangrelease")
CLUSTER_SCRIPT = "/global/scratch/walterwu/calibur/calibur"

