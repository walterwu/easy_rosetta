from .utils import *
from enum import Enum
import pickle
import os

yes = ["yes", "y"]
no = ["no", "n"]

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

class Protocols(Enum):
	FRAGMENT_PICKER = 1
	ABINITIO_RELAX = 2
	CALIBUR_CLUSTER = 3
	JD2_SCORE = 4

class EasyRosettaConfig():
	DEFAULT_CONFIG_FILE = os.path.join(path.dirname(__file__), "data/configs/easy_rosetta_configs/default_easy_rosetta_config")
	def __init__(self, rosetta_path, calibur_path):
		self.name = None
		self.ROSETTA3 = rosetta_path
		self.FRAGMENT_PICKER_SCRIPT_PATH = path.join(self.ROSETTA3, "bin/fragment_picker.linuxgccrelease")
		self.ABINITIO_RELAX_SCRIPT_PATH = path.join(self.ROSETTA3, "bin/AbinitioRelax.linuxgccrelease")
		self.SCORE_SCRIPT_PATH = path.join(self.ROSETTA3, "bin/score_jd2.linuxgccrelease")
		self.CLUSTER_SCRIPT_PATH = calibur_path

	def save(self):
		with open(EasyRosettaConfig.DEFAULT_CONFIG_FILE, 'w') as fp:
			pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

	@staticmethod
	def load(config_name=None):
		if config_name == None:
			config_name = EasyRosettaConfig.DEFAULT_CONFIG_FILE
		config = None
		with open(config_name, 'r') as fp:
			config = pickle.load(fp)
		return config

class ProtocolConfig():

	@classmethod
	def default_configs(cls, )

	def __init__(self, easyrosetta_config, protocol=protocol):
		if protocol not in Protocols.__members__:
			raise ValueError("Protocol " + str(protocol) + " is not supported.")
		self.easyrosetta_config = easyrosetta_config
		self.protocol = protocol
		if protocol == Protocols.FRAGMENT_PICKER:
			setup_fragmentpicker_protocol()
		elif protocol == Protocols.ABINITIO_RELAX:
			setup_abinitiorelax_protocol()
		elif protocol == Protocols.CALIBUR_CLUSTER:
			setup_calibur_protocol()
		elif protocol == Protocols.JD2_SCORE:
			setup_jd2score_protocol()

	def generate_command_line(self):
		cmd = self.executable
		for key, value in self.options_dict:
			if value != None:
				if self.protocol == Protocols.CALIBUR_CLUSTER:
					cmd += " " + str(value)
				else:
					cmd += " -" + key + " " + str(value)
		return cmd

	def config_to_file(self, outfile):
		with open(outfile, 'w') as fp:
			for key, value in self.options_dict.items():
				if value != None:
					fp.write(key + str(value) + '\n')

	def set_flag(key, value):
		if key not in self.options_dict:
			raise ValueError("Nonexistent flag: " + key)
		self.options_dict[key] = value

	def setup_fragment_picker_protocol(self):
		self.executable = self.easyrosetta_config.FRAGMENT_PICKER_SCRIPT_PATH
		self.options_dict = {
			"in:file:native":None,
			"in:file:vall":None,
			"in:file:s":None,
			"in:file:xyz":None,
			"in:file:fasta":None,
			"in:file:pssm":None,
			"in:file:checkpoint":None,
			"in:file:talos_phi_psi":None,
			"in:file:torsion_bin_probs":None,
			"in:path:database":None,
			"frags:scoring:config":None,
			"frags:scoring:profile_score":None,
			"frags:ss_pred":None,
			"frags:n_frags":None,
			"frags:n_candidates":None,
			"frags:frag_sizes":None,
			"frags:write_ca_coordinates":None,
			"frags:allowed_pdb":None,
			"frags:denied_pdb":None,
			"frags:describe_fragments":None,
			"frags:keep_all_protocol":None:,
			"frags:bounded_protocol":None,
			"frags:quota_protocol":None,
			"frags:picking:selecting_rule":None,
			"frags:picking:quota_config_file":None,
			"frags:picking:query_pos":None,
			"constraints:cst_file":None,
			"out:file:frag_prefix":None,
		}

	def setup_abinitio_relax_protocol(self):
		self.executable = self.easyrosetta_config.ABINITIO_RELAX_SCRIPT_PATH
		self.options_dict = {
			"-in:file:native":None,
			"-in:file:fasta":None,
			"-in:file:frag3":None,
			"-in:file:frag9":None,
			"-database":None,
			"-abinitio:relax":None,
			"-nstruct":None,
			"-out:file:silent":None,
			"-out:pdb":None,
			"-out:path":None,
			"-use_filters":None,
			"-psipred_ss2":None,
			"-abinitio::increase_cycles":None,
			"-abinitio::rg_reweight":None,
			"-abinitio::rsd_wt_helix":None,
			"-abinitio::rsd_wt_loop":None,
			"-relax::fast":None,
			"-kill_hairpins":None,
			"-constant_seed":None,
			"-jran":None,
			"-seed_offset":None,
		}

	def setup_calibur_protocol(self):
		self.executable = self.easyrosetta_config.CLUSTER_SCRIPT_PATH
		self.options_dict = {
			"pdb_list":None,
			"threshhold":None,
		}

	def setup_jd2score_protocol(self):
		self.executable = self.easyrosetta_config.SCORE_SCRIPT_PATH
		self.options_dict = {
			"-score_app:linmin":None,
			"-rescore:verbose":None,
			"-in:file:native":None,
			"-score:weights":None,
			"-score:patch":None,
			"-out:nooutput":None,
			"-out:output":None,
			"-out:file:score_only":None,
			"-out:file:scorefile":None,
			"-out:file:silent":None,
			"-out:prefix":None,
			"-scorefile_format":None,
		}











