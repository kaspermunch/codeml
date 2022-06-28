
python scripts/assembleCDS.py data/knownCanonical.exonNuc.fa.gz data/knownGene_GENCODE_V39.txt data/hg38.20way.nh results/species_inclusion.csv steps/cds_data


# Tessa Vadsholt PiB 10 ECTS

## Original description from on contract
The scientific goal of the project is to measure positive selection on spindle-related genes in humans and other primates. A recent report suggests that such genes may be under selection and that they have been exchanged between modern humans and Neanderthals. I will identify all spindle-related genes using information about gene ontology use the PAML software to measure evidence of positive selection on each of these genes. Having identified any genes subject to positive selection, I will investigate these genes represent a characteristic subset of spindle-genes with regard to function or tissue-expression, especially in spermatogenesis or neuronal development. The project may provide evidence that the selection is linked to functions in spermatogenesis suggesting of a role of meiotic drive. The project will run over 14 weeks (~275 hours of work, including the final exam)


## Modified goal
Differential gene analysis on a joint dataset of orthologous genes between human, chimp and macaque to identify genes that are specific to spermatocytes.

Gene propoerties All genes expressed in spermatids and spermatozoa
- Subset of differentially expressed (Differential gene analysis on a joint dataset of orthologous genes between human, chimp and macaque to identify genes that are specific to spermatocytes.)
- Spindle genes (spindle/microtubuli/filament genes)
- Apoptosis
- X sweeps
- PAML selection

- Get all spindle/microtubuli/filament genes




- Meritxell provides a list of X/Y differentially expressed genes in human spermatogenesis (~100)
- Generate / extract CDS alignments
- Run codeml on those
- See if any of the ones under selection overlaps sweeps on X.
- See if there is an enrichment of genes that are under selection AND overlap sweeps AND and are spindle or apoptosis genes





## Differentially expressed genes 
Yes, sorry for not sending this earlier. This is the differentially expressed genes between X and Y spermatids: non-filtered (mast_output.tsv) and filtered with stringent filters (q < 0.01 and fold-change > 2; DEG_XY…), more relaxed filtering could be done on the fold-change, but it might be good to start with these


## Gene alignments

From [Multi20way](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz20way/) download hg38.20way.commonNames.nh, hg38.20way.nh and hg38.20way.scientificNames.nh

Download [FigTree](https://github.com/rambaut/figtree/releases) and open each file to show the phylogeny. Learn what the species are.

From [Multi20way alignments](https://hgdownload.soe.ucsc.edu/goldenPath/hg38/multiz20way/alignments/) download knownCanonical.exonNuc.fa.gz 

Draft script for producing input files for codeml in phylip format:

    python assembleCDS.py knownCanonical.exonNuc.fa.gz knownGene_GENCODE_V39.txt hg38.20way.nh species_inclusion.csv ~/scratch/genes

See if you can figure out how it works.
    
## codeml analysis

You need to install paml:

    conda install -c bioconda paml

You can read about how to call codeml though Python here: https://biopython.org/wiki/PAML. It is done more or less like this:


    from Bio.Phylo.PAML import codeml
    input_file_name = 'phylip/DYNLT3.phylib'
    output_file_name = 'DYNLT3.out'
    cml = codeml.Codeml(alignment = input_file_name, 
                    tree = 'hg38.20way.nh',
                    out_file = output_file_name, 
                    working_dir = '.')

    cml.set_options(verbose=1)
    cml.set_options(seqtype=1)
    cml.set_options(model=0)
    cml.set_options(NSsites=[0, 1, 2, 7, 8])

    cml.run(verbose = True)

    results = codeml.read(output_file_name)

    from ppprint import pprint
    pprint(results)

Codeml python script:

    python codeml.py ~/scratch/genes/DYNLT3.phylib ~/scratch/genes/DYNLT3.nw DYNLT3.txt DYNLT3.ctl ~/scratc



# Project outline:

1. Generate CDS alignments and trees
2. Learn codeml
3. Write a script to run it
4. Test it on a 10 genes
5. Parse the output
6. Make a jupyter notebook and read in the data
7. Plan what questions to address and what analyses to do:
   1. Get differential expression data from Meritxell
   2. Get expression data for each gene from new single-cell paper (to know which are expressed when and how much)
   3. Overlap to my sweeps
   4. Annotate genes with GO terms
   5. Identify GO and pathway enrichments and investigate genes
8. Run the entire set of differentially expressed genes
9.  


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



