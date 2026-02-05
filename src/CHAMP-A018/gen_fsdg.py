import pandas as pd

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title, activation):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Main\n")
        f.write(f"Variables Age Site Activation\n")
        
        # Write input lines for each subject skipping missing activation values
        if df[activation].isnull().any():
            df = df.dropna(subset=[activation])
        for _, row in df.iterrows():
            subject = row['SUBJECT'].astype(str)
            age = row['Age']
            site = row['site'].astype(str)
            fmri = row[activation]
            f.write(f"Input {subject} Main {age} {site} {fmri}\n")
        

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/sdmt_corr.fsgd', 'sdmt_corr_fsgd', 'diff_sdmt_corr')
write_fsgd(covariates_df, '/OUTPUTS/sdmt_num.fsgd', 'sdmt_num_fsgd', 'diff_sdmt_num')
write_fsgd(covariates_df, '/OUTPUTS/srt_recall_delay.fsgd', 'srt_recall_delay_fsgd', 'diff_srt_recall_delay')


