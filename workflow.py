
import os, glob, re
from collections import defaultdict
from gwf import Workflow
from gwf.workflow import collect


# function for easy manipulation of file paths
def modpath(p, parent=None, base=None, suffix=None):     
    par, name = os.path.split(p)
    name_no_suffix, suf = os.path.splitext(name)
    if type(suffix) is str:
        suf = suffix
    if parent is not None:
        par = parent
    if base is not None:
        name_no_suffix = base

    new_path = os.path.join(par, name_no_suffix + suf)
    if type(suffix) is tuple:
        assert len(suffix) == 2
        new_path, nsubs = re.subn(r'{}$'.format(suffix[0]), suffix[1], new_path)
        assert nsubs == 1, nsubs
    return new_path

def workflow(working_dir=os.getcwd(), defaults={}, input_files=[]):

    gwf = Workflow(working_dir=working_dir, defaults=defaults)

    # dict of targets as info for other workflows
    targets = defaultdict(list)

    ###########################################################################
    # codeml 
    ###########################################################################

    # loop over the phylib files
    for phylib_file in input_files:

        # get the gene name from the file name
        gene_name = modpath(phylib_file, suffix='', parent='')

        # the name of the tree file is the same as the phylib file but with a .nw suffix
        tree_file = modpath(phylib_file, suffix='.nw')

        # the output dir for codeml output files
        codeml_output_dir = f'steps/codeml/{gene_name}'
        # codeml_output_dir = f'./steps/codeml/{gene_name}'

        # # make the dir if it does not exist already
        # if not os.path.exists(codeml_output_dir):
        #     os.makedirs(codeml_output_dir)

        # create the name of the codeml output file 
        # same as the the phylib file but we give it a .txt suffix and make its dir the codeml outpur dir
        codeml_output_file = modpath(phylib_file, suffix='_site.txt', parent=codeml_output_dir)
        # tmp_file = modpath(phylib_file, suffix='.tmp', parent=codeml_output_dir)
        tmp_file = modpath(codeml_output_file, suffix='.tmp', parent=codeml_output_dir)

        # almost the same for the control file
        codeml_control_file = modpath(phylib_file, suffix='_site.ctl', parent=codeml_output_dir)

        # # add the codeml output file to the list of all output files
        # targets['codeml'].append(codeml_output_file)

        # make a gwf target (cluster job) to run a codeml analysis
        tag = gene_name.replace('-', '_') + '_site'
        target = gwf.target(name=f'codeml_{tag}',
                inputs=[phylib_file, tree_file], 
                outputs={'output': codeml_output_file, 'control': codeml_control_file}, 
                cores=1,
                walltime='06:00:00', 
                memory='8g') << f"""

        mkdir -p {codeml_output_dir}
        python scripts/codeml_site.py {phylib_file} {tree_file} {tmp_file} {os.path.basename(codeml_control_file)} {codeml_output_dir} && mv {tmp_file} {codeml_output_file}
        sleep 10
        """
        targets['codeml'].append(target)



        codeml_output_file = modpath(phylib_file, suffix='_site_branch.txt', parent=codeml_output_dir)
        # tmp_file = modpath(phylib_file, suffix='.tmp', parent=codeml_output_dir)
        tmp_file = modpath(codeml_output_file, suffix='.tmp', parent=codeml_output_dir)

        # almost the same for the control file
        codeml_control_file = modpath(phylib_file, suffix='_site_branch.ctl', parent=codeml_output_dir)

        # # add the codeml output file to the list of all output files
        # targets['codeml'].append(codeml_output_file)

        # make a gwf target (cluster job) to run a codeml analysis
        tag = gene_name.replace('-', '_') + '_site_branch'
        target = gwf.target(name=f'codeml_{tag}',
                inputs=[phylib_file, tree_file], 
                outputs={'output': codeml_output_file, 'control': codeml_control_file}, 
                cores=1,
                walltime='06:00:00', 
                memory='8g') << f"""

        mkdir -p {codeml_output_dir}
        python scripts/codeml_site_branch.py {phylib_file} {tree_file} {tmp_file} {os.path.basename(codeml_control_file)} {codeml_output_dir} && mv {tmp_file} {codeml_output_file}
        sleep 10
        """
        targets['codeml'].append(target)


    ###########################################################################
    # parse output from codeml analyses
    ###########################################################################

    # the output dir for the summary files produced by parsing codeml output files
    summary_output_dir = 'steps/summary'

    # # make the dir if it does not exist already
    # if not os.path.exists(summary_output_dir):
    #     os.makedirs(summary_output_dir)

    # loop over all the codeml output files
    for target in targets['codeml']:

        codeml_output_file = target.outputs['output']

        # get the gene name from the file name
        gene_name = modpath(codeml_output_file, suffix='', parent='')

        # create the name of the summary output file 
        # same as the the codeml output file but we make its dir the summary outpur dir
        summary_file = modpath(codeml_output_file, suffix='.txt', parent=summary_output_dir)

        # make a gwf target (cluster job) to run a the parse script
        tag = gene_name.replace('-', '_')
        target = gwf.target(name=f'parse_{tag}',
                inputs=[codeml_output_file], 
                outputs={'summary_file': summary_file}, 
                cores=1,
                walltime='00:10:00', 
                memory='8g') << f"""

        mkdir -p {summary_output_dir}
        python scripts/parse_codeml.py {codeml_output_file} {summary_file}
        """
        targets['summary'].append(target)

    # make a gwf target (cluster job) to run a the parse script
    summary_files = collect([t.outputs for t in targets['summary']], ['summary_file'])['summary_files']

    # target = gwf.target(name=f'concat_summaries',
    #         inputs=summary_files, 
    #         outputs=['./results/codeml_tests.txt'], 
    #         cores=1,
    #         walltime='00:10:00', 
    #         memory='8g') << f"""
    # cat steps/summary/*.txt
    # """
    # targets['summary'].append(target)        

    return gwf, targets

####################################################################
# Use code like this to run this as standalone workflow: 
####################################################################

# phylib_files = glob.glob('codeml/steps/cds_data/chrX/*/*.phylib')
# phylib_files = [f for f in phylib_files if modpath(f, parent='', suffix='') in included_genes]
# gwf, codeml_targets  = workflow(defaults={'account': 'xy-drive'}, input_files=phylib_files)

####################################################################
# Use code like this to run this as a submodule workflow: 
####################################################################

# phylib_files = glob.glob('codeml/steps/cds_data/chrX/*/*.phylib')
# phylib_files = [f for f in phylib_files if modpath(f, parent='', suffix='') in included_genes]
# codeml = importlib.import_module('codeml.workflow')
# gwf, codeml_targets  = codeml.workflow(working_dir=working_dir, 
#                                        defaults={'account': 'xy-drive'},
#                                        input_files=phylib_files)
# globals()['codeml'] = gwf
