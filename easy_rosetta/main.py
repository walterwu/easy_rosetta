import argparse
import easy_rosetta

def config():
	parser = argparse.ArgumentParser(description="Configuration info and actions for modeling, analysis and job execution.")
	parser.add_argument("--show", dest="function", action="store_const",
	                    const=easy_rosetta.get_config,
	                   help="Displays current easy_rosetta configurations.")
	parser.add_argument("--edit", dest="function", action="store_const", 
						const=easy_rosetta.edit_config,
						help="Edit easy_rosetta configurations.")
	parser.add_argument("-l", dest="infile", action="store",
						default=None,
						help="Load a config file to be used.")
	args = parser.parse_args()
	if args.function != None:
		if args.function == easy_rosetta.get_config:
			args.function()
		else:
			args.function(infile=args.infile)

def runall():
	parser = argparse.ArgumentParser(description="Generates one candidate decoy using the Rosetta AbinitioRelax protocol")
	parser.add_argument("--ff", dest="fastafile", action="store", required=True,
	                   help="Input fasta file.")
	parser.add_argument("--name", dest="name", action="store", required=True,
						help="Protein name.")
	args = parser.parse_args()
	easy_rosetta.runall(args.fastafile, args.name)

def postprocess():
	parser = argparse.ArgumentParser(description="Processes results of AbinitioRelax, selecting one candidate decoy")
	args = parser.parse_args()
	easy_rosetta.run_abinitio_postprocessing()

def fragment_picker():
	parser = argparse.ArgumentParser(description="Runs the Rosetta fragment picker protocol")
	parser.add_argument("--ff", dest="fastafile", action="store", required=True,
	                   help="Input fasta file.")
	parser.add_argument("--name", dest="name", action="store", required=True,
						help="Protein name.")
	args = parser.parse_args()
	easy_rosetta.run_fragment_picker(args.fastafile, args.name)

def abinitio_relax():
	parser = argparse.ArgumentParser(description="Runs the Rosetta AbinitioRelax protocol")
	parser.add_argument("--ff", dest="fastafile", action="store", required=True,
	                   help="Input fasta file.")
	parser.add_argument("--name", dest="name", action="store", required=True,
						help="Protein name.")
	args = parser.parse_args()
	easy_rosetta.run_abinitio_relax(args.fastafile, args.name)

def score():
	parser = argparse.ArgumentParser(description="Runs the Rosetta jd2 scoring protocol")
	args = parser.parse_args()
	easy_rosetta.run_score_function()

def cluster():
	parser = argparse.ArgumentParser(description="Runs the Calibur clustering protocol")
	args = parser.parse_args()
	easy_rosetta.run_cluster_function()