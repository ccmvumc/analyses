import pandas as pd
import os

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Main\n")
        f.write(f"Variables Age Site\n")
        
        # Write input lines for each subject
        for _, row in df.iterrows():
            subject = row['subject']
            age = row['Age']
            site = row['Site']
            f.write(f"Input {subject} Main {age} {site}\n")
        
        # Write summary lines
        f.write(f"\nNclasses = 1\n")
        f.write(f"Nvariables = 2\n")

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/g1v2.fsgd', 'G1V2')
