from script_utils import show_output, get_path
import os
import pandas as pd


def make_MiniSeq_sampleSheet(sheet_name="sample_sheet", config={}):
    '''
    load the sample_seq excel
    '''

    
    out_path = config['paths']['output_path']
    
    runs = config['Run'].copy()
    reads = runs['Reads']
    del runs['Reads']
    header_df = pd.DataFrame({"header":runs.values()}, index=runs.keys())
    
    sample_excel = get_path('OverviewSeq_excel', file_type="sequencing overview excel file", config=config)

    excel_sheets = pd.ExcelFile(sample_excel).sheet_names

    for sheet in ['Libraries', 'Status']:
        if not sheet in excel_sheets:
            show_output(f"The required sheet <{sheet}> is not found in {sample_excel}!", color="warning")
            return (None,None)

    status_df = pd.read_excel(sample_excel, sheet_name="Status", skiprows=1).dropna(axis=0, how="all").loc[lambda r:r['SampleInfo'].notna(), :]
    status_df = status_df.loc[lambda x: (x['Sample'].notna()) & (x['SeqStatus'] == 1) & (x['Library'] == 3), ['Sample', 'Library', 'SeqStatus']]
    
    libs_df = pd.read_excel(sample_excel, sheet_name="Libraries", skiprows=1).dropna(axis=0, how="all").loc[lambda r:r['SampleInfo'].notna(), :]
    libs_df = libs_df.loc[lambda x: x['Sample'].notna(), ['Sample', 'i7-Index ID','i7-Index']].merge(status_df)
    libs_df = libs_df.loc[:, ['Sample', 'Sample', 'i7-Index', 'i7-Index ID']]
    libs_df.columns = ['Sample_ID', 'Sample_Name', "Index", "Index_ID"]
    libs_df['Index'] = libs_df['Index'].str.replace(" ", "")
    
    if not len(libs_df):
        show_output("No unsequenced libraries found!", color="success")
        return None, None
    
    # write to file
    with open(os.path.join(out_path, f"{sheet_name}.csv"), 'w') as f:
        #write the header
        f.write('[Header]\n')
        header_df.to_csv(f, header=None)
        
        # write the reads
        f.write('\n[Reads]\n')
        pd.DataFrame(reads).to_csv(f, header=False, index=False)
        
        # write the samples
        f.write('\n[Data]\n')        
        libs_df.to_csv(f, index=False)
        
    return status_df, libs_df
