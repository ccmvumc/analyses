import pandas as pd


def showmem(df):
    print(f'Memory Usage:{df.memory_usage(deep=True).sum() / (1024**2)}')


def apply_names(name):
    if '.' in name:
        atlas, not_atlas = name.split('.', 1)
    else:
        atlas = name
        not_atlas = name

    if atlas in ['Schaefer100', 'Schaefer200']:
        _, hemi, network, region = not_atlas.split('_', 3)
    elif atlas == 'Schaefer400':
        _, _, hemi, network, region = not_atlas.split('_', 4)
    elif atlas == 'DnSeg_lh':
        hemi = 'LH'
        network = not_atlas
        region = not_atlas
    elif atlas == 'DnSeg_rh':
        hemi = 'RH'
        network = not_atlas
        region = not_atlas
    elif atlas == 'HBT_lh':
        hemi = 'LH'
        network = not_atlas
        region = not_atlas
    elif atlas == 'HBT_rh':
        hemi = 'RH'
        network = not_atlas
        region = not_atlas
    elif atlas == 'networks':
        hemi = 'both'
        network, region = not_atlas.split('.', 1)
    elif atlas == 'Hypothal':
        hemi = 'both'
        network = not_atlas
        region = not_atlas
    elif atlas == 'Yeo2011':
        hemi = 'both'
        network = not_atlas
        region = not_atlas
    elif atlas == 'ThalamicNuclei':
        network = atlas
        hemi = 'TBD'
        network = not_atlas
        region = not_atlas
    elif atlas == 'sclimbic':
        network = atlas
        hemi = 'TBD'
        network  = not_atlas
        region = not_atlas

    alias = f'{atlas}.{hemi}.{network}.{region}'
    return pd.Series([atlas, hemi, network, region, alias])

print('loading csv')
df = pd.read_csv('/Users/boydb1/Desktop/zvalues-7.csv')
#showmem(df)
#df = df.head(10000000)
showmem(df)
print(f'Record Count:{len(df)}')

df[['r1atlas', 'r1hemi', 'r1network', 'r1region', 'r1n']] = df['r1name'].apply(apply_names)
df[['r2atlas', 'r2hemi', 'r2network', 'r2region', 'r2n']] = df['r2name'].apply(apply_names)

print('saving')
print(df)
df.to_csv('/Users/boydb1/Desktop/zvalues-7b.csv', index=False)
