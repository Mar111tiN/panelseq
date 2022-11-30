import os
import pandas as pd
from script_utils import show_output

def get_samples(input_folder):
    '''
    screens a folder for mutation files
    '''
    
    trans = {
        "basic.csv":"basic", 
        "filter1.csv": "filter1",
        "filter2.loose.csv":"loose",
        "filter2.moderate.csv":"moderate",
        "filter2.strict.csv": "strict",
        "raw.csv": "raw",
        "filter2.dropped.csv": "dropped"
    }
    sample_df = pd.DataFrame()
    for folder, _, files in os.walk(input_folder):
        for file in files:
            sd = {}
            if '.csv' in file or '.xlsx' in file:
                sample = file.split(".")[0]
                for ext in trans.keys():
                    if file.endswith(ext):
                        sample_df.loc[sample, trans[ext]] = os.path.join(folder, file)
                        break
                else:
                    if file.endswith(".csv") and not "":
                        sample_df.loc[sample, "all"] = os.path.join(folder, file)
                
    return sample_df


def read_mutlist(sample, sample_df, stringency="dropped"):
    '''
    read one sample with of a certain stringency
    '''
    
    try:
        sample_path = sample_df.loc[sample, stringency]
    except KeyError:
        show_output(f"No file for sample {sample} of type {stringency}", color="warning")
        return pd.DataFrame()
    else:
        df = pd.read_csv(sample_path, sep="\t")
        return df


def merge_filter_lists(excel_file="", config={}, merge_raw=False):
    '''
    takes the data folder and gets all the filter lists into one big excel
    '''
    
    
    data_path = config['paths']['data_path']
    sample_df = get_samples(data_path).loc[:, ['raw','all', 'basic', 'filter1', 'loose', 'moderate', 'strict', 'dropped']]
    show_output(f"Reading file list from folder {data_path}")
    base_cols = ['Chr', 'Start', 'End', 'Ref', 'Alt']
    dfs = {}
    for sample in sample_df.index:

        raw_df = read_mutlist(sample, sample_df, stringency="raw")
        cols = base_cols + [col for col in raw_df.columns if "cosmic" in col]
        raw_df = raw_df.loc[:, cols]

        # go through all the existing stringencies
        for t in sample_df.drop("raw", axis=1).loc[sample,:].dropna().index:
            mut_df = read_mutlist(sample, sample_df, stringency=t).drop_duplicates()
            if mut_df.empty:
                continue
            if merge_raw:
                mut_df = mut_df.merge(raw_df).drop_duplicates()
            mut_df['Sample'] = sample
            if not t in dfs:
                dfs[t] = []
            dfs[t].append(mut_df.loc[:, [col for col in ['Sample', 'Chr', 'Start', 'End', 'Ref', 'Alt', 'Func', 'Gene', 'Func_refGene',
           'Gene_refGene', 'GeneDetail_refGene', 'AAChange_refGene',
           'Func_ensGene34', 'Gene_ensGene34', 'GeneDetail_ensGene34',
           'AAChange_ensGene34', 'map30_0', 'map50_0', 'map75_1', 'map100_2',
           'GCratio', 'isCandidate', 'ChipID', 'ChipPub', 'ChipFreq', 'cytoBand',
           'somaticP', 'variantP', 'Tdepth', 'TVAF', 'Ndepth', 'NVAF',
           'FisherScore', 'EBscore', 'PONAltSum', 'PONRatio', 'PONAltNonZeros',
           'TR1', 'TR1+', 'TR2', 'TR2+', 'NR1', 'NR1+', 'NR2', 'NR2+', 'ClinScore',
           'cosmic70_ID', 'cosmic70_type', 'cosmic70_score', 'cosmic95_ID', 'cosmic95_count', 'cosmic95_type', 'icgc29_Affected',
           'clinvar_score', 'CLNALLELEID', 'CLNDN', 'CLNSIG', 'gnomAD_exome_ALL',
           'dbSNP154_ID', 'dbSNP154_AltFreq', 'SIFT_pred', 'Polyphen2_HDIV_pred',
           'Polyphen2_HVAR_pred', 'LRT_pred', 'MutationTaster_pred',
           'MutationAssessor_pred', 'FATHMM_pred', 'PROVEAN_pred', 'MetaSVM_pred',
           'MetaLR_pred', 'TumorHDRcand', 'TumorHDRcount', 'TumorHDRinfo',
           'NormalHDRcand', 'NormalHDRcount', 'NormalHDRinfo', 'fwdPrimer',
           'revPrimer', 'Status', 'Temp', 'AmpliconRange', 'AmpliconSize',
           'InsertRange', 'InsertSize', 'InsertSeq', 'offsetL', 'offsetR',
           ] if col in mut_df.columns]])
            
    # write to file
    if excel_file:
        excel_path = os.path.join(config['paths']['output_path'], excel_file)
        show_output(f"Writing to excel_path {excel_file}")
        with pd.ExcelWriter(excel_path) as writer:
            for t in sample_df.drop("raw", axis=1).loc[sample,:].dropna().index:
                dfs[t] = pd.concat(dfs[t]).sort_values(['Sample', 'Chr', 'Start'])
                dfs[t].to_excel(writer, sheet_name=t, index=False)
        show_output("Finished!", color="success")
    return dfs