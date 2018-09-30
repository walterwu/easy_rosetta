import shutil
import subprocess
import os
from constants import SAVIO_JOB_TEMPLATE_PATH, WORKING_PATH
from utils import file_replace

fasta_file = input("Enter fasta file location: ")
protein_name = input("Enter protein name: ")
num_cores = input("Enter number of cores: ")
num_decoys = input("Enter number of decoys to generate: ")
num_hours = input("Enter number of hours to run: ")

savio_job_file = shutil.copy(SAVIO_JOB_TEMPLATE_PATH, WORKING_PATH)
os.rename(savio_job_file, WORKING_DIR + "savio_job_file.sh")
savio_job_file = WORKING_DIR + "savio_job_file.sh"
file_replace("<JOB_NAME>", protein_name, savio_job_file)
file_replace("<NUM_CORES>", num_cores, savio_job_file)
file_replace("<WALL_CLOCK_LIMIT>", num_hours + ":00:00", savio_job_file)
file_replace("<COMMAND_TO_RUN>", "module load python\npython abinitio_prep.py " + fasta_file + " " + protein_name + " " + num_cores + " " + num_decoys, savio_job_file)
p = subprocess.Popen("sbatch " + savio_job_file, shell=True)
p.wait()



