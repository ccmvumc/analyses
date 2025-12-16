import pandas as pd

covariates_df = pd.read_csv('/INPUTS/covariates.csv')

#generate an additional fsdg just for age and site only (no activation)
with open('/OUTPUTS/age_site_only.fsgd', 'w') as f:
    f.write(f"GroupDescriptorFile 1\n")
    f.write(f"Title age_site_only\n")
    f.write(f"Class Main\n")
    f.write(f"Variables Age Site\n")
    for _, row in covariates_df.iterrows():
        subject = row['SUBJECT'].astype(str)
        age = row['Age']
        site = row['site'].astype(str)
        f.write(f"Input {subject} Main {age} {site}\n")


