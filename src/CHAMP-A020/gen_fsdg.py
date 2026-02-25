import pandas as pd

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title, activation):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Main\n")
        f.write(f"Variables Age Activation\n")
        
        # Write input lines for each subject skipping missing activation values
        if df[activation].isnull().any():
            df = df.dropna(subset=[activation])
        for _, row in df.iterrows():
            subject = row['SUBJECT'].astype(str)
            age = row['Age']
            fmri = row[activation]
            f.write(f"Input {subject} Main {age} {fmri}\n")
        

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/p3_pz_mem_amp.fsgd', 'p3_pz_mem_amp_fsgd', 'p3_pz_memdiff_amp')


