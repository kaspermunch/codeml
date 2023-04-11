
# Description
The scientific goal of the project is to measure positive selection on spindle-related genes in humans and other primates. A recent report suggests that such genes may be under selection and that they have been exchanged between modern humans and Neanderthals. I will identify all spindle-related genes using information about gene ontology use the PAML software to measure evidence of positive selection on each of these genes. Having identified any genes subject to positive selection, I will investigate these genes represent a characteristic subset of spindle-genes with regard to function or tissue-expression, especially in spermatogenesis or neuronal development. The project may provide evidence that the selection is linked to functions in spermatogenesis suggesting of a role of meiotic drive. The project will run over 14 weeks (~275 hours of work, including the final exam)

# Gene alignments

From [Multi20way](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz20way/) download hg38.20way.commonNames.nh, hg38.20way.nh and hg38.20way.scientificNames.nh

Download [FigTree](https://github.com/rambaut/figtree/releases) and open each file to show the phylogeny. Learn what the species are.

From [Multi20way alignments](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz20way/alignments/) download knownCanonical.exonNuc.fa.gz 

Draft script for producing input files for codeml in phylip format:

    python scripts/assembleCDS.py data/knownCanonical.exonNuc.fa.gz data/knownGene_GENCODE_V39.txt data/hg38.20way.nh results/species_inclusion.csv steps/cds_data steps/cds_data/discarded_genes.txt

See if you can figure out how it works.
    
# codeml analysis

You need to dowload and compile paml from source from [here](http://abacus.gene.ucl.ac.uk/software/)

    conda install -c bioconda paml

You can read about how to call codeml though Python here: https://biopython.org/wiki/PAML.

Generate alignments:

    python scripts/assembleCDS.py data/knownCanonical.exonNuc.fa.gz data/knownGene_GENCODE_V39.txt data/hg38.20way.nh results/species_inclusion.csv results/discarded_aln.txt steps/cds_data

codeml python script:

    python codeml.py ~/scratch/genes/DYNLT3.phylib ~/scratch/genes/DYNLT3.nw DYNLT3.txt DYNLT3.ctl ~/scratch

Workflow:

    gwf status

# Possible extra steps

Realign using macse: 

    macse -prog alignSequences -seq ~/scratch/genes/DYNLT3.fa -out_NT DYNLT3.NT.fa -out_AA DYNLT3.AA.fa

Reciprocal best match using blat

    for ASS in hg38 panTro4 panPan1 gorGor3 ponAbe2 nomLeu3 rheMac3 macFas5 papAnu2 chlSab2 nasLar1 rhiRox1 calJac3 saiBol1 tarSyr2 micMur1 otoGar3 tupBel1 mm10 canFam3; do wget https://hgdownload.soe.ucsc.edu/goldenPath/$ASS/bigZips/$ASS.2bit ; done

All agains hg38:

    blat -t=dna -out=pslx -fine genes/DYNLT3.fa hg38.2bit out.txt

hg38 against each:

    blat -t=dna -out=pslx -fine genes/DYNLT3_hg38only.fa panTro4.2bit DYNLT3_hg38_vs_otoGar3.txt
    ...
    blat -t=dna -out=pslx -fine genes/DYNLT3_hg38only.fa otoGar3.2bit DYNLT3_hg38_vs_otoGar3.txt



