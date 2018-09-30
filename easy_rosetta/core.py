import os
import sys
import fileinput
import shutil
import subprocess
from random import randint
from threading import Thread
from .constants import *
from .utils import *

BASE_DIR = None
OUTPUT_DIR = None
CONFIG_DIR = None
FASTA_FILE_PATH = None
PROTEIN_NAME = None
SETUP = False
OUTPUT_COMBINED = False

def runall(fasta_file, protein_name):
	run_fragment_picker()
	run_abinitio_relax()
	run_abinitio_postprocessing()

def run_abinitio_postprocessing():
	scores_dict = run_score_function()
	top_cluster, num_in_cluster = run_cluster_function()
	select_top_decoy(scores_dict, top_cluster, num_in_cluster)

def run_fragment_picker(fasta_file, protein_name):
	setup(fasta_file, protein_name)
	fragment_flags_file = generate_fragment_flags()
	command = shellify_path(FRAGMENT_PICKER_SCRIPT_PATH) + " @" + fragment_flags_file
	p = subprocess.Popen(command, shell=True, cwd=BASE_DIR)
	p.wait()

def run_abinitio_relax(fasta_file, protein_name):
	setup(fasta_file, protein_name)
	worker_threads = []
	for i in range(NUM_CORES):
		thread = Thread(target=abinitio_worker, args=[i], daemon=True)
		worker_threads.append(thread)
	for thread in worker_threads:
		thread.start()
	for thread in worker_threads:
		thread.join()

def run_score_function():
	combine_output()
	working_dir = os.path.join(OUTPUT_DIR, "all")
	command = shellify_path(SCORE_SCRIPT_PATH) + " -in:file:s *.pdb"
	p = subprocess.Popen(command, shell=True, cwd=working_dir)
	p.wait()
	scores_dict = process_score_results(os.path.join(working_dir, "score.sc"))
	return scores_dict

def run_cluster_function():
	combine_output()
	cwd = os.path.join(OUTPUT_DIR, "all")
	with open(os.path.join(cwd, "pdb_list", 'w')) as fp:
		for file in os.listdir(os.path.join(OUTPUT_DIR, "all")):
			fp.write(file + '\n')
	calibur_results_path = os.path.join(shellify_path(OUTPUT_DIR), "calibur_results")
	command = shellify_path(CLUSTER_SCRIPT_PATH) + " pdb_list >" + calibur_results_path
	p = subprocess.Popen(command, shell=True, cwd=cwd)
	p.wait()
	top_cluster, num_in_cluster = process_calibur_results(calibur_results_path)
	return top_cluster, num_in_cluster

def select_top_decoy(score_dict, top_cluster, num_in_cluster):
	min_score = 0
	decoy_name = None
	for decoy in top_cluster:
		if score_dict[decoy] < min_score:
			min_score = score_dict[decoy]
			decoy_name = decoy
	if decoy_name:
		shutil.copy(os.path.join(OUTPUT_DIR, "all", decoy_name), os.path.join(OUTPUT_DIR, decoy_name))
		print("The best decoy is " + decoy_name + " with a score of " + str(min_score) + " and cluster size of " + str(num_in_cluster))
	else:
		print("No suitable decoy found")

def abinitio_worker(worker_number):
	working_dir = os.path.join(CONFIG_DIR, "worker" + str(worker_number))
	abinitio_flags_file = generate_abinitio_flags(worker_number)
	command = shellify_path(ABINITIO_RELAX_SCRIPT_PATH) + " @" + abinitio_flags_file
	p = subprocess.Popen(command, shell=True, cwd=working_dir)
	p.wait()

def generate_fragment_flags():
	fragment_flags_file = os.path.join(CONFIG_DIR, PROTEIN_NAME + "-fragment_flags")
	shutil.copy(FRAGMENT_FLAGS_TEMPLATE_PATH, fragment_flags_file)
	file_replace("<FASTA_FILE>", shellify_path(FASTA_FILE_PATH), fragment_flags_file)
	out_frag_prefix = shellify_path(os.path.join(CONFIG_DIR, PROTEIN_NAME + "_frags"))
	file_replace("<OUT_FRAG_PREFIX>", out_frag_prefix , fragment_flags_file)
	out_desc_prefix = shellify_path(os.path.join(CONFIG_DIR, PROTEIN_NAME + "_desc"))
	file_replace("<OUT_FRAG_DESC_PREFIX>", out_desc_prefix, fragment_flags_file)
	return fragment_flags_file

def generate_abinitio_flags(worker_number):
	abinitio_flags_file = os.path.join(CONFIG_DIR, "worker" + str(worker_number), PROTEIN_NAME + "-abinitio_flags")
	shutil.copy(ABINITIO_FLAGS_TEMPLATE_PATH, abinitio_flags_file)
	file_replace("<FASTA_FILE>", FASTA_FILE_PATH, abinitio_flags_file)
	file_replace("<FRAG_3MER_FILE>", CONFIG_DIR + "/" + PROTEIN_NAME + "_frags.200.3mers", abinitio_flags_file)
	file_replace("<FRAG_9MER_FILE>", CONFIG_DIR + "/" + PROTEIN_NAME + "_frags.200.9mers", abinitio_flags_file)	
	file_replace("<NUM_STRUCTS>", str(int(NUM_STRUCTS / NUM_CORES)), abinitio_flags_file)
	file_replace("<RNG_SEED>", str(random_with_N_digits(8)), abinitio_flags_file)
	out_path = os.path.join(shellify_path(OUTPUT_DIR), "worker" + str(worker_number))
	file_replace("<OUT_PATH>", out_path, abinitio_flags_file)
	return abinitio_flags_file

def setup(fasta_file, protein_name):
	
	global SETUP
	global FASTA_FILE_PATH
	global PROTEIN_NAME
	global BASE_DIR 
	global OUTPUT_DIR
	global CONFIG_DIR
	
	if SETUP:
		return

	BASE_DIR = os.path.join(WORKING_PATH, protein_name)
	OUTPUT_DIR = os.path.join(BASE_DIR, "output")
	CONFIG_DIR = os.path.join(BASE_DIR, "config")
	if not os.path.exists(BASE_DIR):
		os.mkdir(BASE_DIR)
	if not os.path.exists(OUTPUT_DIR):
		os.mkdir(OUTPUT_DIR)
	if not os.path.exists(CONFIG_DIR):
		os.mkdir(CONFIG_DIR)
	for i in range(NUM_CORES):
		output_worker_dir = os.path.join(OUTPUT_DIR, "worker" + str(i))
		config_worker_dir = os.path.join(CONFIG_DIR, "worker" + str(i))
		if not os.path.exists(output_worker_dir):
			os.mkdir(output_worker_dir)
		if not os.path.exists(config_worker_dir):
			os.mkdir(config_worker_dir)
	fasta_file = shutil.copy(fasta_file, BASE_DIR)
	FASTA_FILE_PATH = fasta_file
	PROTEIN_NAME = protein_name
	SETUP = True

def combine_output():
	global OUTPUT_COMBINED
	if OUTPUT_COMBINED:
		return

	target_dir = os.path.join(OUTPUT_DIR, "all")
	if not os.path.exists(target_dir):
		os.mkdir(target_dir)
	decoy_counter = 0
	for i in range(NUM_CORES):
		source_dir = os.path.join(OUTPUT_DIR, "worker" + str(i))
		for file in os.listdir(source_dir):
			updated_filename = "S_" + str(counter) + ".pdb"
			source = os.path.join(source_dir, file)
			target = os.path.join(target_dir, updated_filename)
			shutil.move(source, target)
			decoy_counter += 1
	OUTPUT_COMBINED = True
	return decoy_counter
	
def process_score_results(results):
	score_dict = {}
	with open(results) as fp:
		for i in range(2):
			line = fp.readline()
		line = fp.readline()
		while line:
			tokens = line.split()
			score = tokens[1]
			pdb_name = tokens[25]
			tokens = pdb_name.split('_')
			pdb_name = tokens[0] + '_' + tokens[1] + ".pdb"
			score_dict[pdb_name] = float(score)
			line = fp.readline()
	return score_dict

def process_calibur_results(results):
	top_cluster_pdb_list = []
	with open(results) as fp:
		line = fp.readline()
		cluster_found = False
		num_in_cluster = 0
		while line:
			if ":" in line and ".pdb" in line.split()[0]:
				if cluster_found:
					break
				else:
					cluster_found = True
					tokens = line.replace('\n', '').split()
					num_in_cluster = tokens[1]
					top_cluster_pdb_list += tokens[2:]
			elif cluster_found:
				tokens = line.replace('\n', '').split()
				top_cluster_pdb_list += tokens[2:]
			line = fp.readline()
	return top_cluster_pdb_list, num_in_cluster

def test_file_replace():
	file_replace("<FASTA FILE>", "1msi", "/Users/walterwu/Downloads/test_replace")
	file_replace("<OUT_PATH>", "~/out", "/Users/walterwu/Downloads/test_replace")

def test_process_calibur():
	print(process_calibur_results("out.txt"))

def test_process_score():
	print(process_score_results("score.sc"))

def test_select_top_decoy():
	score = process_score_results("score.sc")
	cluster, num = process_calibur_results("out2.txt")
	select_top_decoy(score, cluster, num)

#test_file_replace()
#test_process_calibur()
#test_process_score()
#test_select_top_decoy()




