from os import path
from .utils import *

DEFAULT_CONFIG_PATH = path.join(path.dirname(__file__), "data/configs/default_config")
SESSIONS_PATH = ath.join(path.dirname(__file__), "data/userdata/sessions")

NUM_CORES = 1
NUM_STRUCTS = 1
NUM_NODES = 1

FRAGMENT_FLAGS_TEMPLATE_PATH = path.join(path.dirname(__file__), "data/templates/fragment_flags_template")
ABINITIO_FLAGS_TEMPLATE_PATH = path.join(path.dirname(__file__), "data/templates/abinitio_flags_template")
SAVIO_JOB_TEMPLATE_PATH = path.join(path.dirname(__file__), "data/templates/savio_job_template")

WORKING_PATH = "/global/scratch/walterwu/"
ROSETTA_PATH = "${ROSETTA3}"
FRAGMENT_PICKER_SCRIPT_PATH = path.join(ROSETTA_PATH, "bin/fragment_picker.linuxgccrelease")
ABINITIO_RELAX_SCRIPT_PATH = path.join(ROSETTA_PATH, "bin/AbinitioRelax.linuxgccrelease")
SCORE_SCRIPT_PATH = path.join(ROSETTA_PATH, "bin/score_jd2.linuxgccrelease")
CLUSTER_SCRIPT_PATH = "/global/scratch/walterwu/calibur/calibur"

def update():
	global NUM_CORES
	global NUM_STRUCTS
	global NUM_NODES
	global WORKING_PATH
	global ROSETTA_PATH
	global FRAGMENT_PICKER_SCRIPT_PATH
	global ABINITIO_RELAX_SCRIPT_PATH
	global SCORE_SCRIPT_PATH
	global CLUSTER_SCRIPT_PATH
	config_dict = read_config()
	NUM_CORES = int(config_dict["NUM_CORES"])
	NUM_STRUCTS = int(config_dict["NUM_STRUCTS"])
	NUM_NODES = int(config_dict["NUM_NODES"])
	WORKING_PATH = pythonify_path(config_dict["WORKING_PATH"])
	ROSETTA_PATH = pythonify_path(config_dict["ROSETTA_PATH"])
	FRAGMENT_PICKER_SCRIPT_PATH = pythonify_path(path.join(ROSETTA_PATH, "bin/fragment_picker.linuxgccrelease"))
	ABINITIO_RELAX_SCRIPT_PATH = pythonify_path(path.join(ROSETTA_PATH, "bin/AbinitioRelax.linuxgccrelease"))
	SCORE_SCRIPT_PATH = pythonify_path(path.join(ROSETTA_PATH, "bin/score_jd2.linuxgccrelease"))
	CLUSTER_SCRIPT_PATH = pythonify_path(config_dict["CLUSTER_SCRIPT_PATH"])

update()