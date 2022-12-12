# Create a Miniseq-samplesheet from the Sequencing-Excel 
used for running Miniseq/MiSeq-sequencing runs. The generated sample sheet has to be loaded into the Miniseq prior to sequencing in order for demultiplexing to work. This tool is python-based and runs from a jupyter notebook without any coding knowledge.

## Setup
+ first, go to the desired folder and download the code from github:
    `$ git clone https://github.com/Mar111tiN/panelseq.git && cd panelseq`
+ guidance for setting up a jupyter notebook can be received from Samira, Sarah or Lena
+ the recommended way is via miniconda/mambaforge installation followed by creating the proper environment
+ you can create a jupyter notebook environment via conda from the `py-env.yml` in the env-folder
+ alternatively, run `$ conda create -n <your-env-name> pandas jupyter openpyxl pyyaml`
    +   then, you activate that environment `conda activate <your-env-name>`
    +   next, run `jupyter notebook` from the git repo folder and browse to the `makeMiniseq-SampleSheet`notebook
    +   adjust the paths in your config file to match this repos location on your drive and set the Reads you are running

### The MiniSeq sample sheet is easily generated from the `OverviewSamplesSequencing.xls` and a config file specifying additional info for the data sheet
+ there are two modi:
    * #### `usePoolingList = False`
        + only samples with unsequenced status will be included in the sample shee+ only samples with unsequenced status will be included in the sample sheet
        + only Agilent sample sheet will be generated from Samples and Libraries sheets
    * #### `usePoolingList = True`
        + takes manual list from the LibraryPooling sheet and creates i7 and i5 barcodes
+ all the necessary info (path to `OverviewSamplesSequencing.xls` and sequencing Meta data should be stored in the config file that you load via load_config from a yaml file
+ run the test example from the jupytre