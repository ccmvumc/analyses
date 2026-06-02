import pandas as pd

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Inverted\nClass Heterozygous\nClass Direct\n")
        f.write(f"Variables Age Site\n")
        
        # Write input lines for each subject skipping missing activation values
        for _, row in df.iterrows():
            subject = str(row['SUBJECT'])
            age = row['Age']
            site = str(row['site'])
            #assign group based on the value in Genotype column
            group = row['Genotype']
            f.write(f"Input {subject} {group} {age} {site}\n")
        

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/chrfam7.fsgd', 'chrfam7_fsgd')


