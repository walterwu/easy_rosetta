from enum import Enum
import json
import os
import utils

yes = ["yes", "y"]
no = ["no", "n"]

class Program(Enum):
	FRAGMENT_PICKER = 1
	ABINITIO_RELAX = 2
	CALIBUR_CLUSTER = 3
	JD2_SCORE = 4
	SAVIO_JOB = 5

def print_dict(d):
	r = json.dumps(d)
	print(r)

def gen_main_config():
	"""
	Generate a default configuration for easy_rosetta
	Returns a dict of the config.
	"""
	config = {}
	config["working_dir"] = defaults.WORKING_DIR
	config["rosetta_path"] = defaults.ROSETTA_PATH
	config["fragment_picker_path"] = defaults.FRAGMENT_PICKER_PATH
	config["abinitio_relax_path"] = defaults.ABINTIO_RELAX_PATH
	config["score_path"] = defaults.SCORE_PATH
	config["cluster_path"] = defaults.CLUSTER_PATH
	config["fragment_picker"] = gen_fragment_picker_config()
	config["abinitio_relax"] = gen_abinitio_relax_config()
	config["savio_job"] = gen_savio_job_config()
	return config

def gen_fragment_picker_config():
	"""
	Generate a default fragment picker flags file in a dictionary representation
	"""
	config = {}
	config["-in::file::vall"] = "${ROSETTA3_TOOLS}/fragment_tools/vall.apr24.2008.extended.gz"
	config["-in::file::fasta"] = None
	config["-frags::bounded_protocol"] = None
	config["-frags::frag_sizes"] = "3 9"
	config["-frags::n_candidates"] = "200"
	config["-frags::n_frags"] = 200
	config["-out::file::frag_prefix"] = None
	config["-frags::describe_fragments"] = None
	return config

def gen_abinitio_relax_config():
	"""
	Generate a default abinitio relax flags file in a dictionary representation
	"""
	config = {}
	config["-in:file:fasta"] = None
	config["-in:file:frag3"] = None
	config["-in:file:frag9"] = None
	config["-abinitio:relax"] = None
	config["-nstruct"] = None
	config["-out:pdb"] = None
	config["-abinitio:increase_cycles"] = None
	config["-abinitio:rg_reweight"] = None
	config["-abinitio::rsd_wt_helix"] = None
	config["-abinitio::rsd_wt_loop"] = None
	config["-relax::fast"] = None
	config["-constant_seed"] = None
	config["-jran"] = None
	config["-out:path"] = None
	return config

def gen_savio_job_config():
	"""
	Generate a default savio job file in a dictionary representation
	"""
	config = {}
	config["--job-name"] = None
	config["--account"] = None
	config["--partition"] = None
	config["--nodes"] = None
	config["--ntasks-per-node"] = None
	config["--cpus-per-task"] = None
	config["--time="] = None
	config["batch_command"] = None
	return config

def gen_main_config_file(config, target):
	with open(target, 'w') as fp:
		data = json.dumps(config)
		fp.write(data)

def gen_config_file(config, program, target):
	"""
	Generate a config file from the specified config dict
		fragment_picker_config: dictionary config file
		program: Enum type of program to generate
		target: location to store flag file
	"""
	if program != Program.SAVIO_JOB:
		with open(target, 'w') as fp:
			for key, value in config.items():
				if not value:
					value = ""
				fp.write("{} {}\n".format(str(key), str(value)))
	else:
		with open(target, 'w') as fp:
			fp.write("#!/bin/bash\n")
			for key, value in config.items():
				if key != "batch_command":
					if not value:
						fp.write("#SBATCH {}\n".format(str(key)))
					else:
						fp.write("#SBATCH {}={}\n".format(str(key), str(value)))
				else:
					fp.write(value)

def parse_config_file(program, target):
	"""
	Parse a config file into a dictionary representation
		program: Enum type of program to parse as
		target: Input config file
	This is really very ugly. Don't look. 
	"""
	config = {}
	if program != Program.SAVIO_JOB:
		# Parse config for non savio job files
		with open(target, 'r') as fp:
			lines = fp.readlines()
			for line in lines:
				if line.isspace() or line.startswith('#'):
					continue
				line = line.strip().replace('\n', '')
				tokens = line.strip(" ", maxsplit=1)
				key = tokens[0]
				value = ""
				if tokens[1]:
					value = tokens[1]
				config[key] = value
	else:
		# Parse config for savio job file
		with open(target, 'r') as fp:
			lines = fp.readlines()
			batch_command = ""
			for line in lines:
				if line.isspace():
					continue
				if line.startswith("#SBATCH "):
					line = line.strip().replace('\n', '')
					line = line.replace("#SBATCH ", '')
					tokens = line.split('=', maxsplit=1)
					key = tokens[0]
					value = ""
					if tokens[1]:
						value = tokens[1]
					config[key] = value
				elif line.startswith("#"):
					continue
				else:
					batch_command += line
		config["batch_command"] = batch_command
	return config

def get_config():
	read_dict = read_config()
	for key, value in read_dict.items():
		print(key + ": " + value)

def edit_config(infile=None):
	if not infile == None:
		print("Loading provided configuration file.")
		copy_to_config(infile)
		print("Config loaded as:")
		get_config()
		print("Settings have been saved.")
	else:
		print(("Welcome to the config editor for easy_rosetta. The next steps ensures thats essential Rosetta,\n"
				"Calibur and working environment paths are set properly and that default Savio\n"
				"preferences are recorded.\n"))
		status = input("Use default ROSETTA3 location? (Y/n) ").lower()
		while status not in yes and status not in no:
			status = input("Please enter (Y/n) ")
		if status in no:
			rosetta_path = input("Enter the Rosetta path: ")
			write_config("ROSETTA_PATH", rosetta_path)
		calibur_path = input("Enter the Calibur executable path: ")
		write_config("CLUSTER_SCRIPT_PATH", calibur_path)
		working_path = input("Enter the location in which you wish to run Rosetta: ")
		write_config("WORKING_PATH", working_path)
		print("Settings for AbinitioRelax protocol")
		num_decoys = input("Enter the default number of decoys to create: ")
		write_config("NUM_STRUCTS", num_decoys)
		print("Settings for Savio Compute Nodes")
		num_nodes = input("Enter the default number of nodes to use: ")
		write_config("NUM_NODES", num_nodes)
		num_cores = input("Enter the default number of cores to use (1-24): ")
		write_config("NUM_CORES", num_cores)
		write_config("SETUP_RUN", "TRUE")
		print("Settings have been saved.")














