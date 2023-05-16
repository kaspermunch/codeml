from Bio.Phylo.PAML import codeml
from Bio.Phylo.PAML.chi2 import cdf_chi2
import argparse
import sys
import os
from pprint import pprint


# def _get_LRT(lnLNull,lnLAlt,df):
#    statistic = 2*(lnLAlt - lnLNull)
#    pval=cdf_chi2(df, 2*(lnLAlt - lnLNull))
#    return pval

from scipy.stats import chi2

def get_LRT(lnLNull,lnLAlt,df):
    pval = 1-chi2.cdf(2*(lnLAlt - lnLNull), df)
    return pval


parser = argparse.ArgumentParser(description='''
Parse codeml output using biopython's wrapper.

''')

parser.add_argument('codeml_output_file', type=str,
                    help='Output file from codeml')
parser.add_argument('output_file', type=str,
                    help='Parsed output file')


args = parser.parse_args()

results = codeml.read(args.codeml_output_file)

p_values = {}

if results['model'] = 0:

    model = 'site'

    lnL1 = results["NSsites"][1]["lnL"]
    lnL2 = results["NSsites"][2]["lnL"]
    lnL7 = results["NSsites"][7]["lnL"]
    lnL8 = results["NSsites"][8]["lnL"]

    if lnL1 < lnL2:    
        p_values[2] = get_LRT(lnL1,lnL2,2)
    else:
        p_values[2] = 1

    if lnL7 < lnL8:
        p_values[8] = get_LRT(lnL7,lnL8,2)
    else:
        p_values[8] = 1

elif results['model'] = 2:

    model = 'site-branch'

    pass

else:
    assert 0


gene_name = os.path.splitext(os.path.basename(args.codeml_output_file))[0]

with open(args.output_file, 'w') as f:
    for k, v in p_values.items():
        #omega = 'nan'
        #if v <= 0.05 / 2:
        site = max(results["NSsites"][k]["parameters"]["site classes"].keys())
        omega = results["NSsites"][k]["parameters"]["site classes"][site]["omega"]
        print(gene_name, model, k, v, omega, file=f, sep=',')


