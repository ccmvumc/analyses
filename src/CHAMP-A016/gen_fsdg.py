import pandas as pd

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

def write_fsgd(df, output_file, title):
    with open(output_file, 'w') as f:
        # Write header
        f.write(f"GroupDescriptorFile 1\n")
        f.write(f"Title {title}\n")
        f.write(f"Class Group 1\n Group 2\n")
        f.write(f"Variables Age Site Activation\n")
        
        # Write input lines for each subject skipping missing activation values
        for _, row in df.iterrows():
            subject = row['SUBJECT'].astype(str)
            age = row['Age']
            site = row['site'].astype(str)
            #if value in group is 0 write group 1 if value is 1 write group 2
            group = "Group 1" if row['Group'] == 0 else "Group 2"
            f.write(f"Input {subject} {group} {age} {site}\n")
        

# Generate the FSGD file
write_fsgd(covariates_df, '/OUTPUTS/apoe.fsgd', 'apoe_fsgd')


