from script_utils import show_output, get_path
import os
import pandas as pd



def write_sample_sheet(libs_df, run_config={}, csv_out=""):
    '''
    the sample sheet writer combining a library_df and info from config into a valid MiniSeq sample sheet
    '''

    # get the info from the config file
    reads_df = pd.DataFrame(run_config['Reads'])
    del run_config['Reads']
    header_df = pd.DataFrame({"header":run_config.values()}, index=run_config.keys())


    # write to file
    with open(csv_out, 'w') as f:
        #write the header
        f.write('[Header]\n')
        header_df.to_csv(f, header=None)
        
        # write the reads
        f.write('\n[Reads]\n')
        reads_df.to_csv(f, header=False, index=False)
        
        # write the samples
        f.write('\n[Data]\n')        
        libs_df.to_csv(f, index=False)
    show_output(f"Sample sheet written to {csv_out}", color="success")


def read_pool(sample_excel=""):
    '''
    autodetects the sheet and lines for samples and barcodes from pooling sheet
    '''
    # detect the sheet that has pooling in the name
    excel_sheets = pd.ExcelFile(sample_excel).sheet_names
    pool_sheets = [sheet for sheet in excel_sheets if "Pool" in sheet]
    
    if not len(pool_sheets):
        show_output(f"There is no Pooling sheet ('Pool' in sheet name) in {sample_excel}!", color="warning")
        return
    
    pool_sheet = pool_sheets[0]
    # load sheet into df
    pool_df = pd.read_excel(sample_excel, sheet_name=pool_sheet).iloc[:,:6]
    
    # get the row with "Sample" in first column
    header_row = pool_df[pool_df.iloc[:,0] == "Sample"].iloc[0]
    #apply header names to pool_df
    pool_df.columns = header_row
    
    # remove unneeded rows
    pool_df = pool_df.iloc[int(header_row.name)+1:, :].dropna(subset="Sample")
    # fillup with Ns
    pool_df.loc[pool_df['type'] == "Agilent", ["i5-Index", "i5-barcodes"]] = ["UMI", "N"*10]
    i5_cycles = int(pool_df['i5-barcodes'].str.len().max())
    pool_df['i5-barcodes'] = pool_df['i5-barcodes'].str.pad(i5_cycles, side="right", fillchar="N")
    pool_df = pool_df.loc[:, ['Sample', 'Sample', 'i7-barcodes', 'i7-Index', 'i5-barcodes', 'i5-Index']]
    pool_df.columns = ['Sample_ID', 'Sample_Name', "Index", "Index_ID", "Index2", "Index2_ID"]
    for col in ['Index', 'Index2']:
        pool_df[col] = pool_df[col].str.replace(" ", "")
    return pool_df


def read_agilent(sample_excel=""):
    '''
    autodetects the sheet and lines for samples and barcodes from SequencingExcel
    '''
    excel_sheets = pd.ExcelFile(sample_excel).sheet_names
    for sheet in ['Libraries', 'Status']:
        
        if not sheet in excel_sheets:
            show_output(f"The required sheet <{sheet}> is not found in {sample_excel}!", color="warning")
            return (None,None)

    status_df = pd.read_excel(sample_excel, sheet_name="Status", skiprows=1).dropna(axis=0, how="all").loc[lambda r:r['SampleInfo'].notna(), :]
    status_df = status_df.loc[lambda x: (x['Sample'].notna()) & (x['SeqStatus'] == 1) & (x['Library'] > 2), ['Sample', 'Library', 'SeqStatus']]
    libs_df = pd.read_excel(sample_excel, sheet_name="Libraries", skiprows=1).dropna(axis=0, how="all").loc[lambda r:r['SampleInfo'].notna(), :]
    libs_df = libs_df.loc[lambda x: x['Sample'].notna(), ['Sample', 'i7-Index ID','i7-Index']].merge(status_df)
    libs_df = libs_df.loc[:, ['Sample', 'Sample', 'i7-Index', 'i7-Index ID']]
    libs_df.columns = ['Sample_ID', 'Sample_Name', "Index", "Index_ID"]
    libs_df['Index'] = libs_df['Index'].str.replace(" ", "")    
    return libs_df.dropna(subset='Index')
    

def make_MiniSeq_sampleSheet(sample_sheet_name="sample_sheet", config={}, usePoolingList=False):
    '''
    load the sample_seq excel
    '''
    
    out_path = config['paths']['output_path']

    
    sample_excel = get_path('OverviewSeq_excel', file_type="sequencing overview excel file", config=config)

    if usePoolingList:
        lib_df = read_pool(sample_excel)

    else:
        lib_df = read_agilent(sample_excel)
    
    if not len(lib_df):
        show_output("No unsequenced libraries found!", color="success")
        return None, None
    
    sample_sheet_path = os.path.join(out_path, f"{sample_sheet_name}.csv")
    check_cols = [col for col in lib_df.columns if "Index" in col and not "ID" in col]

    if (len(dup_samples := lib_df.loc[lib_df.duplicated(check_cols,keep=False), "Sample_ID"])):
        show_output(f'Identical barcodes detected in samples {" and ".join(list(dup_samples))}! Please check!', color="warning")

    write_sample_sheet(lib_df, run_config=config['Run'].copy(), csv_out=sample_sheet_path)
        
    return lib_df