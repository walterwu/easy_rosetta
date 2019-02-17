import fileinput
import json
import os
from random import randint
import shutil
import subprocess
import sys
from threading import Thread

import defaults
import utils

def run_all(config):
    """
    Run all protein modeling steps:
    1. Pick fragments and generate fragment files
    2. Run abinitio relax protocol
    3. Choose the best decoy from generated decoys
    """
    run_fragment_picker(config)
    run_abinitio_relax(config)
    run_postprocessing(config)

def run_fragment_picker(config):
    """
    Run fragment picker protocol. This takes in an amino acid
    sequence and generates two fragment files (3, 9) to be 
    used in the abiinito protocol 
    """
    fragment_flags_file = generate_fragment_flags(config)
    print("Running fragment picker protocol")
    command = "{} @{}".format(config["fragment_picker_script"], fragment_flags_file)
    utils.run_cmd(command, cwd=config["working_dir"], display_stdout=False)
    print("Completed fragment picker protocol")

def run_abinitio_relax(config):
    """
    Run the abinito relax protocol. Start off worker threads to
    run the abinitio binary and write results to a directory
    """
    
    worker_threads = []
    for i in range(config["num_cores"]):
        thread = Thread(target=abinitio_worker, args=[config, i], daemon=True)
        worker_threads.append(thread)
    for thread in worker_threads:
        thread.start()
    for thread in worker_threads:
        thread.join()

def run_postprocessing(config):
    """
    Choose the best decoy by scoring the decoys,
    clustering them and choosing the top decoy from
    the clusters
    """
    combine_output(config)
    scores_dict = run_score_function(config)
    top_cluster, num_in_cluster = run_cluster_function(config)
    select_top_decoy(config, scores_dict, top_cluster, num_in_cluster)

def run_score_function(config):
    """
    Run scoring function to score each decoy
    Returns a dictionary of [protein_name: score]
    """
    cwd = os.path.join(config["output_dir"], "all")
    command = "{} -in:file:s *.pdb".format(config["score_script"])
    p = utils.run_cmd(command, cwd=cwd, display_stdout=False)
    scores_dict = process_score_results(os.path.join(cwd, "score.sc"))
    return scores_dict

def run_cluster_function(config):
    """
    Runs clustering algorithm on decoys
    Returns the top cluster and number of decoys in that cluster
    """
    cwd = os.path.join(config["output_dir"], "all")
    # Creates a file, pdb_list, which contains newline separated paths to 
    # all decoys generated
    with open(os.path.join(cwd, "pdb_list"), 'w') as fp:
        for file in os.listdir(cwd):
            fp.write("{}\n".format(file))
    calibur_results_path = os.path.join(config["output_dir"], "calibur_results")
    command = "{} pdb_list >{}".format(config["cluster_script"], calibur_results_path)
    p = utils.run_cmd(command, cwd=cwd, display_stdout=False)
    top_cluster, num_in_cluster = process_calibur_results(calibur_results_path)
    return top_cluster, num_in_cluster

def select_top_decoy(config, score_dict, top_cluster, num_in_cluster):
    """
    Given the top cluster and score_dict, select the top decoy
    by choosing the highest scoring decoy in the top cluster
    """
    min_score = 0
    decoy_name = None
    for decoy in top_cluster:
        if score_dict[decoy] < min_score:
            min_score = score_dict[decoy]
            decoy_name = decoy
    if decoy_name:
        source = os.path.join(config["output_dir"], "all", decoy_name)
        target = os.path.join(config["output_dir"], decoy_name)
        utils.run_cmd("cp {} {}".format(source, target))
        print("The best decoy is {} with a score of {} and and cluster size of {}"\
              .format(decoy_name, min_score, num_in_cluster)) 
    else:
        print("No suitable decoy found")

def abinitio_worker(config, worker_number):
    """
    worker thread which kicks of abinitio relax protocol
    """
    print("Running abinitio relax for worker {}".format(worker_number))
    cwd = os.path.join(config["output_dir"], "worker_{}".format(worker_number))
    abinitio_flags_file = generate_abinitio_flags(config, worker_number)
    command = "{} @{}".format(config["abinitio_relax_script"], abinitio_flags_file)
    utils.run_cmd(command, cwd=True, display_stdout=False)
    print("Completed abinitio relax for worker {}".format(worker_number))

def generate_fragment_flags(config):
    """
    Generate fragment flags file.
    Uses template stored in FRAGMENT_FLAGS_TEMPLATE_PATH,
    replacing necessary fillers
    Copies the flag file to config_dir/protein_name-fragment_flags
    """
    fragment_flags_file = os.path.join(config["config_dir"], "{}-fragment_flags".format(config["name"]))
    print("Generating fragment flags file at {}".format(fragment_flags_file))
    utils.run_cmd("cp {} {}".format(defaults.FRAGMENT_FLAGS_TEMPLATE_PATH, fragment_flags_file), ignore_error=True)
    utils.file_replace("<FASTA_FILE>", config["fasta_file"], fragment_flags_file)
    # output will be stored at: config_dir/protein_name_frags.200.3mers
    # and config_dir/protein_name_frags.200.9mers
    out_frag_prefix = os.path.join(config["config_dir"], "{}_frags".format(config["name"]))
    utils.file_replace("<OUT_FRAG_PREFIX>", out_frag_prefix , fragment_flags_file)
    # out_desc file is not used, but we still provide a prefix
    out_desc_prefix = os.path.join(config["config_dir"], "{}_desc".format(config["name"]))
    utils.file_replace("<OUT_FRAG_DESC_PREFIX>", out_desc_prefix, fragment_flags_file)
    print("Finished generating fragments flag file.")
    return fragment_flags_file

def generate_abinitio_flags(config, worker_number):
    """
    Generate abinitio flags file for worker worker_number.
    Uses template stored in FRAGMENT_FLAGS_TEMPLATE_PATH,
    replacing necessary fillers
    Copies the flag file to config_dir/worker_n/protein_name-abinitio_flags
    """
    # output flags file will be stored at: config_dir/worker_n/protein_name-abinitio_flags
    abinitio_flags_file = os.path.join(config["config_dir"], "worker_{}".format(worker_number),\
                                       "{}-abinitio_flags".format(config["name"]))
    print("Generating abinitio flags file at {}".format(abinitio_flags_file))
    utils.run_cmd("cp {} {}".format(defaults.ABINITIO_FLAGS_TEMPLATE_PATH, abinitio_flags_file), ignore_error=True)
    utils.file_replace("<FASTA_FILE>", config["fasta_file"], abinitio_flags_file)
    frags_3_file = os.path.join(config["config_dir"], "{}_frags.200.3mers".format(config["name"]))
    frags_9_file = os.path.join(config["config_dir"], "{}_frags.200.9mers".format(config["name"]))
    utils.file_replace("<FRAG_3MER_FILE>", frags_3_file, abinitio_flags_file)
    utils.file_replace("<FRAG_9MER_FILE>", frags_9_file, abinitio_flags_file)	
    num_structs = int(config["num_structs"] / config["num_cores"])
    utils.file_replace("<NUM_STRUCTS>", str(num_structs), abinitio_flags_file)
    utils.file_replace("<RNG_SEED>", str(utils.random_with_N_digits(8)), abinitio_flags_file)
    out_path = os.path.join(config["output_dir"], "worker_{}".format(worker_number))
    utils.file_replace("<OUT_PATH>", out_path, abinitio_flags_file)
    print("Finished generating abinitio flags file for worker {}".format(worker_number))
    return abinitio_flags_file

def setup(config):
    """
    Set up the working environment for easy_rosetta
    Returns a config dict
    Layout of working directory:

    working_dir/
    |--	output/
    |	|-- worker_1/
    |	|-- worker_2/
    |	| ...
    |	|-- worker_n/
    |
    |-- config/
    |	|-- config_files
    |	|-- worker_1/
    |	    |-- abinitio_config
    |-- fasta_file.fasta
    """
    name = config["name"]
    fasta_file = config["fasta_file"]
    working_dir = config["working_dir"]
    output_dir = os.path.join(working_dir, "output")
    config_dir = os.path.join(working_dir, "config")
    config_file = os.path.join(config_dir, "easy_rosetta.cfg")
    config["output_dir"] = output_dir
    config["config_dir"] = config_dir
    config["fasta_file"] = os.path.join(config_dir, fasta_file)

    # Load config file and return if ignore_config is not true
    if not config["ignore_config"]:
        print("Checking for existing easy-rosetta config file at {}".format(config_file))
        if os.path.isfile(config_file):
            print("Using existing easy-rosetta config found at working directory {}.".format(working_dir))
            with open(config_file) as fp:
                config = json.load(fp)
            print("Finished loading config.")
            return config

    # Make top level working directory
    print("Running setup. Creating easy_rosetta working directory.")
    utils.run_cmd("mkdir {}".format(working_dir), ignore_error=True)

    # Make output and config dirs
    utils.run_cmd("mkdir {}".format(output_dir), ignore_error=True)
    utils.run_cmd("mkdir {}".format(config_dir), ignore_error=True)

    # Make working directories for each worker process
    for i in range(config["num_cores"]):
        output_worker_dir = os.path.join(output_dir, "worker_{}".format(i))
        config_worker_dir = os.path.join(config_dir, "worker_{}".format(i))
        utils.run_cmd("mkdir {}".format(output_worker_dir), ignore_error=True)
        utils.run_cmd("mkdir {}".format(config_worker_dir), ignore_error=True)
    utils.run_cmd("cp {} {}".format(fasta_file, working_dir), ignore_error=True)
    config_file = os.path.join(config_dir, "easy_rosetta.cfg")
    with open(config_file, 'w') as fp:
        json.dump(config, fp)
    print("Finished writing config to {}.".format(config_file))
    return config

def combine_output(config):
    """
    Combines output pdb files in the separate worker dirs by
    moving them into output_dir/all, then renaming and renumbering
    all of them to S_1.pdb, S_2.pdb, ...S_n.pdb
    Returns total number of decoys
    """
    print("Combining output")
    target_dir = os.path.join(config["output_dir"], "all")
    utils.run_cmd("mkdir {}".format(target_dir), ignore_error=True)
    decoy_counter = 0
    for i in range(config["num_cores"]):
        source_dir = os.path.join(config["output_dir"], "worker_{}".format(i))
        for file in os.listdir(source_dir):
            updated_filename = "S_{}.pdb".format(counter)
            source = os.path.join(source_dir, file)
            target = os.path.join(target_dir, updated_filename)
            utils.run_cmd("mv {} {}".format(source, target))
            decoy_counter += 1
    return decoy_counter
    
def process_score_results(results):
    """
    Takes in a score results file and returns a score_dict 
    of format {[pdb_name: score]}
    """
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
            pdb_name = "{}_{}.pdb".format(tokens[0], tokens[1])
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




