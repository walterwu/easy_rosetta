# easy_rosetta

## Overview
The purpose of the easy_rosetta CLI tool is to provide an ease-of-use wrapper around the Rosetta3 software suite, specifically targeted at the AbinitioRelax protocol. With easy_rosetta, it is easy to generate an AbintioRelax protein model simply by inputting the name and amino acid sequence, or a fasta file containing the protein data. The user may also pass in configuration files for the various Rosetta3 protocols in order to exercise the same level of control Rosetta3 provides.

## Installation
The usage of easy_rosetta depends on Python3, as well as functional installations of Rosetta3 and the Calibur clustering protocol.</br>
Link to Rosetta3: https://www.rosettacommons.org/demos/latest/tutorials/install_build/install_build<br />
Link to Calibur: https://sourceforge.net/projects/calibur/<br />
Be sure to set the `ROSETTA3`, `ROSETTA3_DB`, and `ROSETTA3_TOOLS` environment variables.<br />

To install easy_rosetta, simply clone the repo:<br />
```
git clone https://github.com/walterwu/easy_rosetta.git
```
That's it! Once you have cloned the repo, you can run easy_rosetta by invoking the `easy_rosetta.py` script:<br />
```
python3 easy_rosetta/easy_rosetta.py --help
```
The help message will provide enough usage instruction to get started.
  
## Usage
### Basic Usage
The interface to easy_rosetta is the `easy_rosetta.py` file, located at easy_rosetta/easy_rosetta.py. If you are extensively using this CLI, it is a good idea to set an alias to `easy_rosetta.py`. To get started with using easy_rosetta, run:<br />
```
python3 easy_rosetta/easy_rosetta.py --help
```
The help message will list the extensive options available to configure and use easy_rosetta.<br />
The easiest way to use easy_rosetta is to use the `--run-all` flag:<br />
```
python3 easy_rosetta/easy_rosetta.py --run-all --name PROTEIN_NAME --fasta-file FASTA_FILE --working-dir WORKING_DIR
```
If you are looking for an easy way to model a protein, similar to Swiss Model website, then this is it. All you need to specify is the protein name, fasta file, and working directory. The output pdb file will be located in the specified working directory, at `WORKING_DIR/outpur_dir/output.pdb`. 
Note: You may also need to specify the location of the Calibur script, using the `--score-script` option.
### Advanced Usage
If you wish to further leverage the power of easy_rosetta and by extension, Rosetta3, it is necessary to know a little more about the inner workings of easy_rosetta. easy_rosetta works in three steps:<br />
1. Fragment picking: generation of fragments for use in AbinitioRelax, using the Rosetta3 fragment picker protocol<br />
2. Decoy generation: generation of many decoys using the Rosetta3 AbinitioRelax protocol<br />
3. Post-processing: choosing one candidate from the of decoys generated, using clustering and energy scoring<br />
Each can be triggered by the following flags: `--fragment-picker`, `--abinitio-relax`, and `--postprocess`. It is important to note that step 2, running AbinitioRelax, is an extremely compute intensive step. In many cases, the execution of this step may be prematurely cancelled due to the prohibitive length of time it takes to run. However, easy_rosetta is setup to be tolerant of such disruptions. Let's take a closer look at how this happens.
#### AbinitioRelax
Unless you compiled Rosetta3 with MPI, which may not be possible on all machines, each Rosetta3 process will be single threaded. This means that the execution of vanilla Rosetta3 AbinitioRelax will waste the majority of the system's compute power. easy_rosetta allows you to sepcify the number of cores you have availible to you, with the `--num-cores` option. For each core, easy_rosetta will kick off a separate AbinitioRelax job, allowing you to optimize your compute usage. To allow for mid execution cancellations, easy_rosetta stores the output of AbinitioRelax in .pdb format, in the output directory located at `WORKING_DIR/outpur_dir/output.pdb/`. This means that even if AbinitioRelax is cancelled, the post processing step can still work will the decoys generated. 
#### Post-processing
easy_rosetta takes a very naive approach to choosing the best decoy generated. First, it scores the decoys with Rosetta3's scoring protocol. Then, it uses the Calibur program to cluster the decoys. Finally, it takes the top cluster and chooses the top scoring decoy from that cluster. The top scoring decoy is choosen as the output, and is located at `WORKING_DIR/outpur_dir/output.pdb`


