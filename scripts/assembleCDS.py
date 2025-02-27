
import sys
import os
import gzip
import copy # for testsing / debugging ... remove later
import pandas as pd
from collections import defaultdict
from contextlib import redirect_stdout
from Bio import SeqIO
import re
from ete3 import Tree

excluded_species = ['tupBel1', 'mm10', 'canFam3']

def write_phylip(seqs, output_file):

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(output_file, 'w') as dest, redirect_stdout(dest):

        lengths = [len(x) for x in seqs.values()]
        assert(all(lengths[0] == l for l in lengths))
        seq_length = lengths[0]

        for name in seqs:
            seqs[name] = seqs[name].replace('-', '?')

        print(f"{len(seqs)} {seq_length}")
        for name in sorted(seqs.keys(), key=lambda x: x != 'hg38'):
            print(f"{name:<10}{seqs[name]}")

def write_fasta(seqs, output_file):

    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    with open(output_file, 'w') as dest, redirect_stdout(dest):

        lengths = [len(x) for x in seqs.values()]
        assert(all(lengths[0] == l for l in lengths))
        seq_length = lengths[0]

        for name in seqs:
            seqs[name] = seqs[name].replace('?', '-')

        for name in sorted(seqs.keys(), key=lambda x: x != 'hg38'):
            print(f">{name}\n{seqs[name]}")            

def print_aln(gene_name, seqs, f):

    with redirect_stdout(f):

        lengths = [len(x) for x in seqs.values()]
        assert(all(lengths[0] == l for l in lengths))
        seq_length = lengths[0]

        for name in sorted(seqs.keys(), key=lambda x: x != 'hg38'):
            print(f"{gene_name:<10} {name:<7} {seqs[name]}")  
        print()
        print()

# command line arguments
_, fasta_file, id_table_file, tree_file, aln_stat_file, output_dir, discarded_aln_file = sys.argv

# read id table
id_table = pd.read_csv(id_table_file, sep='\t').drop_duplicates('name2')
id_table['ucsc_gene_base'] = [x.rsplit('.', 1)[0] for x in id_table['name2']]
id_table.set_index('ucsc_gene_base', inplace=True)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

skipped = 0

# read tree
tree = Tree(tree_file, format=1)
# get all names of species in the tree
all_species = [t.name for t in tree.get_leaves()]
# unroot the tree (codeml uses unrooted trees)
tree.unroot()

# dictionary to keep track of which species are included in the produced alignment for the species
species_included = {}

# read fasta from gziped (compressed file)
with gzip.open(fasta_file, 'rt') as f, open(discarded_aln_file, 'w') as f_discarded:

    # keep track of what the last ucsc id we have seen is
    prev_ucsc_id = None

    # dictionary with lists as default values (for filling in the exons we read for each species)
    exons = defaultdict(list)
    # iterate over all the fasta entries in the fasta file (each entry is an exon of a cds)
    for entry in SeqIO.parse(f, "fasta"):

        # split the name attribute (fasta header line) to get info for the gene
        ucsc_id, assembly, exon_nr, exon_total = entry.name.rsplit('_', 4)

        # if exon we are looking at belongs to the next gene, write the previous gene
        # and start with the next gene
        if prev_ucsc_id is not None and ucsc_id != prev_ucsc_id:
            try:
                # try to extract the ucsc gene name from the ucsc gene id
                name, version = prev_ucsc_id.rsplit('.', 1)
                gene_name = id_table.loc[name, 'geneName']
                chrom = id_table.loc[name, '#chrom']

                is_coding = id_table.loc[name, 'transcriptClass'] == 'coding' and 'pseudo' not in id_table.loc[name, 'transcriptType']

            except KeyError:
                # if that is not possible, we skip the gene
                skipped += 1
            else: 
                # if it was possible, we go on

                # make a dictionary with the concatenated exons (CDS) for each gene
                cds_alignment = {}
                for species in exons:
                    if species not in excluded_species:
                        cds_alignment[species] = ''.join(exons[species]).upper()

                ##################                            
                # For testing... keep original
                test_cds_alignment = copy.deepcopy(cds_alignment)
                ##################                            

                # # regular expression for selecting only those with an aligned start and top codon and no inframe stop codons:
                regex = re.compile(r'ATG(?:(?!TAA|TAG|TGA)...)*(?:TAA|TAG|TGA)$')
                # This version also tests that all indels are multiples of inframe triplets (discards a lot of candidate genes...)
                # regex = re.compile(r'ATG(?:(?!TAA|TAG|TGA|[TAGC][TAGC]-|-[TAGC][TAGC]|[TAGC]-[TAGC]|[TAGC]--|--[TAGC]|-[TAGC]-)...)*(?:TAA|TAG|TGA)$')

                # use the regular expression on each sequence
                for species in list(cds_alignment.keys()):
                    orf_ok = regex.match(cds_alignment[species])

                    # test if all indels are multiples of triplets, not necesarrily inframe
                    no_frame_shifting_indels = not any(x % 3 for x in map(len, re.findall(r'-+', cds_alignment[species])))

                    if orf_ok and no_frame_shifting_indels:
                        # remove the stop codon found (becuase codeml does not want it in there)
                        start, end = orf_ok.span()
                        cds_alignment[species] = cds_alignment[species][:end-3] + '?' * (len(cds_alignment[species]) - end + 3)
                    else:
                        # delete the species and their sequences if the regular expression does not match
                        del cds_alignment[species]                                             

                # keep the alignmnets with human and at least two other species
                if is_coding and 'hg38' in cds_alignment and len(cds_alignment) >= 4:
                    
                    # record which species are in the alignment
                    species_included[gene_name] = list(cds_alignment.keys())

                    # write phylip file
                    output_path = os.path.join(output_dir, chrom, gene_name, gene_name + '.phylib')
                    write_phylip(cds_alignment, output_path)                  

                    # write fasta file (in case you need it)
                    output_path = os.path.join(output_dir, chrom, gene_name, gene_name + '.fa')
                    write_fasta(cds_alignment, output_path)                  

                    # remove the species from the tree that were removed from the alignment
                    alignment_tree = tree.copy("newick")
                    alignment_tree.prune(list(cds_alignment.keys()))

                    # write the tree for the alignment
                    output_path = os.path.join(output_dir, chrom, gene_name, gene_name + '.nw')
                    alignment_tree.write(format=1, outfile=output_path)                    

                    print(gene_name)

                    pass

                else:
                    ###################
                    print('SKIPPED', chrom, gene_name, file=f_discarded)
                    print_aln(gene_name, test_cds_alignment, f_discarded)
                    ##################                            

                    # grep SKIPPED steps/discarded_genes.txt | cut -f 3 -d ' ' | xargs -I GENE find steps/ -name 'GENE.*' -exec rm -f {} \;

                    skipped += 1

                # empty the exon dictionary 
                exons = defaultdict(list)

        # add an exon sequence to the list for the species (assembly e.g. hg38)
        exons[assembly].append(str(entry.seq))

        # make our current id the previous one
        prev_ucsc_id = ucsc_id


print(f'Skipped {skipped} genes')

records = []
for gene, aligned_species in species_included.items():
    row = [gene] + [species in aligned_species for species in all_species]
    records.append(row)
df = pd.DataFrame().from_records(records, columns=['gene'] + all_species)
df.to_csv(aln_stat_file, index=False)
