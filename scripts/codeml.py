from Bio.Phylo.PAML import codeml
from Bio.Phylo.PAML.chi2 import cdf_chi2
import argparse
import sys
import os
from pprint import pprint

parser = argparse.ArgumentParser(description='''
Run codeml using biopython's wrapper.

python codeml.py ~/scratch/genes/DYNLT3.phylib ~/scratch/genes/DYNLT3.nw DYNLT3.txt DYNLT3.ctl ~/scratch

''')

parser.add_argument('alignment_file', type=str,
                    help='Alignment file.')
parser.add_argument('tree_file', type=str,
                    help='Tree file.')
parser.add_argument('results_file', type=str,
                    help='Results file.')
parser.add_argument('control_file', type=str,
                    help='Control file to write model options.')
parser.add_argument('working_directory', type=str,
                    help='Working directory for temporary files.')

args = parser.parse_args()

## SITE MODEL.
cml = codeml.Codeml(alignment = args.alignment_file, tree = args.tree_file,
                out_file =  args.results_file, 
                working_dir = args.working_directory)

cml.set_options(verbose=1)
cml.set_options(seqtype=1) # * 1:codon models; 2: amino acid models
#cml.set_options(runmode=0) # 0: user tree; 1: semi-automatic; 2: automatic 3: StepwiseAddition; (4,5):PerturbationNNI
cml.set_options(model=0) #  0:one-w for all branches; 2: w’s for branches
cml.set_options(NSsites=[0, 1, 2, 7, 8]) #  0:one-ratio; 1:neutral; 2:selection; 3:discrete; 7:beta; 8:beta&w

cml.ctl_file = args.control_file
#cml.write_ctl_file() 

cml.run(verbose = True)


