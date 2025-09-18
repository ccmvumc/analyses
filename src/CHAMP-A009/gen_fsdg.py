import pandas as pd
import os

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title, activation):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Main\n")
        f.write(f"Variables Age Site Activation\n")
        
        # Write input lines for each subject
        for _, row in df.iterrows():
            subject = row['SUBJECT']
            age = row['Age']
            site = row['site']
            fmri = row[activation]
            f.write(f"Input {subject} Main {age} {site} {fmri}\n")
        

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/dlpfc_fsdg.fsgd', 'dlpfc_fsdg', 'dlpfc')
write_fsgd(covariates_df, '/OUTPUTS/ppc_fsdg.fsdg', 'ppc_fsdg', 'ppc')
