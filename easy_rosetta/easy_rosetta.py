import argparse
import defaults
import config
import core

def config(args):
	print("Running config")

def run_all(args):
	print("Running all")
	_check_modeling_inputs(args)
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_all(config)

def fragment_picker(args):
	print("Running fragment picker")
	_check_modeling_inputs(args)
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_fragment_picker(config)

def abinitio_relax(args):
	print("Running abinitio relax")
	_check_modeling_inputs(args)
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_abinitio_relax(config)

def score(args):
	print("Running score")
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_score_function(config)

def cluster(args):
	print("Running cluster")
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_cluster_function(config)

def postprocess(args):
	print("Running postprocess")
	_check_modeling_inputs(args)
	config = gen_config(args)
	config = core.setup(config, args.fasta_file, args.name)
	core.run_postprocessing(config)
	
def _check_modeling_inputs(args):
	pass

def gen_config(args):
	"""
	Generate a default configuration for easy_rosetta
	Returns a dict of the config.
	"""
	config = {}
	config["protein_name"] = args.name
	config["working_dir"] = args.working_dir
	config["rosetta_path"] = defaults.ROSETTA_PATH
	config["fragment_picker_script"] = defaults.FRAGMENT_PICKER_SCRIPT
	config["abinitio_relax_script"] = defaults.ABINITIO_RELAX_SCRIPT
	config["score_script"] = defaults.SCORE_SCRIPT
	config["cluster_script"] = args.cluster_script
	config["num_cores"] = int(args.num_cores)
	config["num_structs"] = int(args.num_decoys)
	config["num_nodes"] = defaults.NUM_NODES
	config["ignore_config"] = args.ignore_config
	return config

def setup(args):
	config = gen_config(args)
	core.setup(config, args.fasta_file, args.name)


def get_normalize_args():
	"""
	Gather command line arguments and normalize them
	"""
	parser = argparse.ArgumentParser(description='easy-rosetta CLI')
	parser.add_argument("--config", action="store_true", default=False, help="Configure easy-rosetta")
	parser.add_argument("--run-all", action="store_true", default=False, help="Generate and choose the top decoy candidate using Rosetta")
	parser.add_argument("--fragment-picker", action="store_true", default=False, help="Run the fragment picker protocol")
	parser.add_argument("--abinitio-relax", action="store_true", default=False, help="Run the abinitio relax protocol")
	parser.add_argument("--postprocess", action="store_true", default=False, help="Process and choose a top candidate from generated decoys")
	parser.add_argument("--score", action="store_true", default=False, help="Score the generate decoys")
	parser.add_argument("--cluster", action="store_true", default=False, help="Run the clustering protocol")
	parser.add_argument("--pick", action="store_true", default=False, help="Choose a top candidate from generated decoys")
	parser.add_argument("--fasta-file", default=None, help="Input fasta file.")
	parser.add_argument("--name", default=None, help="Protein name")
	parser.add_argument("--num-cores", default=defaults.NUM_CORES,\
						 help="Number of decoys to generate for AbinitioRelax")
	parser.add_argument("--num-decoys", default=defaults.NUM_STRUCTS,\
						 help="Number of decoys to generate for AbinitioRelax")
	parser.add_argument("--cluster-script", default=defaults.CLUSTER_SCRIPT,\
						 help="Location of the clustering binary")
	parser.add_argument("--working-dir", default=defaults.WORKING_DIR,\
						 help="Specify the working directory of easy-rosetta")
	parser.add_argument("--setup-only", action="store_true", default=False,\
						 help="Run easy-rosetta setup for specified protein only")
	parser.add_argument("--ignore-config", action="store_true",default=False,\
						 help="Do not check for or use existing easy-rosetta config file for the protein")

	return parser.parse_args()

def main():
	args = get_normalize_args()
	if args.config:
		config(args)
	if args.run_all:
		run_all(args)
	if args.fragment_picker:
		fragment_picker(args)
	if args.abinitio_relax:
		abinitio_relax(args)
	if args.postprocess:
		postprocess(args)
	if args.score:
		score(args)
	if args.cluster:
		cluster(args)
	if args.pick:
		pick(args)
	if args.setup_only:
		setup(args)

if __name__ == "__main__":
	main()



