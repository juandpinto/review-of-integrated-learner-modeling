# %%
import pandas as pd
import numpy as np
import re

acm_df = pd.read_csv('database-search/ACM_Run1_168.csv')
ieee_df = pd.read_csv('database-search/IEEE_Run1_565.csv')
scopus_df = pd.read_csv('database-search/Scopus_Run1a_3661.csv')
wos_df = pd.read_csv('database-search/WebOfScience_Run1a_786.csv')
ebsco_df = pd.read_csv('database-search/EBSCO_Run1a_615.csv')
# Keep original EBSCO export (with lots of missing data) since we included it in our triage dataset
ebsco_df_original = pd.read_csv('database-search/EBSCO_Run1_partial.csv')


# %%
# Extract and organize relevant fields (ACM)

# Convert keywords to list
acm_df['Keywords'] = acm_df['Keywords'].fillna('').str.split(', ')

# Combine into single column to replace NaNs
acm_df['Journal'] = acm_df['Journal'].combine_first(acm_df['Proceedings title'])

acm_df = acm_df[['Authors', 'Title', 'Publication year', 'Abstract', 'Keywords', 'Journal']]
acm_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
acm_df['source'] = 'ACM'


# %%
# Extract and organize relevant fields (EBSCO)

# Convert keywords to list
ebsco_df['Keywords'] = ebsco_df['Keywords'].fillna('').str.split('; ')
ebsco_df['Subjects'] = ebsco_df['Subjects'].fillna('').str.split('; ')

# Combine keywords into single column
ebsco_df['keywords'] = ebsco_df['Keywords'] + ebsco_df['Subjects']
# Remove duplicate keywords
ebsco_df['keywords'] = ebsco_df['keywords'].apply(lambda x: pd.Series(x).unique().tolist())
# Remove empty keywords
ebsco_df['keywords'] = ebsco_df['keywords'].apply(lambda x: [i for i in x if i != ''])

# Extract publication year
ebsco_df['Publication Date'] = ebsco_df['Publication Date'].str.findall('20[012][0-9]').apply(lambda x: x[-1])

ebsco_df = ebsco_df[['Author', 'Article Title', 'Publication Date', 'Abstract', 'Keywords', 'Journal Title']]
ebsco_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
ebsco_df['source'] = 'EBSCO'


# %%
# Extract and organize relevant fields (EBSCO-original)

# Convert keywords to list
ebsco_df_original['Keywords'] = ebsco_df_original['Keywords'].fillna('').str.split('; ')

# Combine keywords into single column
ebsco_df_original['keywords'] = ebsco_df_original['Keywords']
# Remove duplicate keywords
ebsco_df_original['keywords'] = ebsco_df_original['keywords'].apply(lambda x: pd.Series(x).unique().tolist())
# Remove empty keywords
ebsco_df_original['keywords'] = ebsco_df_original['keywords'].apply(lambda x: [i for i in x if i != ''])

ebsco_df_original = ebsco_df_original[['Authors', 'Title', 'Publication year', 'Abstract', 'Keywords', 'Journal']]
ebsco_df_original.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
ebsco_df_original['source'] = 'EBSCO'


# %%
# Extract and organize relevant fields (Scopus)

# Convert keywords to list
scopus_df['Index Keywords'] = scopus_df['Index Keywords'].fillna('').str.split('; ')
scopus_df['Author Keywords'] = scopus_df['Author Keywords'].fillna('').str.split('; ')

# Combine keywords into single column
scopus_df['keywords'] = scopus_df['Index Keywords'] + scopus_df['Author Keywords']
# Remove duplicate keywords
scopus_df['keywords'] = scopus_df['keywords'].apply(lambda x: pd.Series(x).unique().tolist())

scopus_df = scopus_df[['Authors', 'Title', 'Year', 'Abstract', 'Index Keywords', 'Source title']]
scopus_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
scopus_df['source'] = 'Scopus'


# %%
# Extract and organize relevant fields (WOS)

# FIXME: all keywords are missing
wos_df = wos_df[['Authors', 'Article Title', 'Publication Year', 'Abstract', 'Author Keywords', 'Source Title']]
wos_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
wos_df['source'] = 'WOS'


# %%
# Extract and organize relevant fields (IEEE)

# Convert keywords to list
ieee_df['Author Keywords'] = ieee_df['Author Keywords'].fillna('').str.replace(', ', ';').str.split(';')

ieee_df = ieee_df[['Authors', 'Document Title', 'Publication Year', 'Abstract', 'Author Keywords', 'Publication Title']]
ieee_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
ieee_df['source'] = 'IEEE'


# %%
# Concatenate all data
df = pd.concat([acm_df, ieee_df, scopus_df, wos_df, ebsco_df, ebsco_df_original])
df = df.reset_index(drop=True)


# %%
# Function for removing duplicates
def remove_duplicates(df):
    df = df.reset_index(drop=True)
    # Get duplicates
    unique_S = df['title'].str.lower() + df['year'].astype('str')

    duplicates_S = pd.Series([unique_S.iloc[i] in unique_S.iloc[:i].values for i in range(len(unique_S))])
    print('duplicates:', duplicates_S.sum())

    # Remove duplicates
    df = df[~duplicates_S].reset_index(drop=True)

    return df


# %%
# Convert missing keywords to empty strings
df['keywords'] = df['keywords'].apply(lambda x: x if type(x)==list else [])
df['keywords'] = df['keywords'].apply(lambda x: [] if x == [''] else x)

# Convert years to int
df['year'] = df['year'].astype(int)


# %%
# df.isna().sum()
df.groupby('source').apply(lambda x: x.isna().sum())


# %%
# Remove cases of missing authors/title/abstract
df = df[~df[['authors', 'title', 'abstract']].isna().any(axis=1)]


# %%
# Run 1
search1 = 'knowledge tracing|learner model\w*|student model\w*'
search2 = 'educat\w*|tutor\w*|instruct\w*|learning system\w*|learning environment\w*'

run = df[
    (
        df['abstract'].str.contains(search1, case=False) |
        df['title'].str.contains(search1, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search1, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search2, case=False) |
        df['title'].str.contains(search2, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search2, i, flags=re.I) for i in x]).any())
    )
]

print(run.shape)
run = remove_duplicates(run)

run.shape


# %%
# Run 2
search1 = 'knowledge tracing|learner model\w*|student model\w*'
search2 = 'educat\w*|tutor\w*|instruct\w*'

run = df[
    (
        df['abstract'].str.contains(search1, case=False) |
        df['title'].str.contains(search1, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search1, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search2, case=False) |
        df['title'].str.contains(search2, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search2, i, flags=re.I) for i in x]).any())
    )
]

print(run.shape)
run = remove_duplicates(run)

run.shape


# %%
# Run 3
search1 = 'knowledge tracing|learner model\w*|student model\w*'
search2 = 'educat\w*|tutor\w*|instruct\w*'
search3 = 'adapt\w*|personaliz\w*|recommend\w*'

run = df[
    (
        df['abstract'].str.contains(search1, case=False) |
        df['title'].str.contains(search1, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search1, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search2, case=False) |
        df['title'].str.contains(search2, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search2, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search3, case=False) |
        df['title'].str.contains(search3, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search3, i, flags=re.I) for i in x]).any())
    )
]

print(run.shape)
run = remove_duplicates(run)

run.shape


# %%
# Run 4
search1 = 'knowledge tracing|learner model\w*|student model\w*'
search2 = 'educat\w*|tutor\w*|instruct\w*'
search3 = 'adapt\w*|personaliz\w*|recommend\w*'
search4 = 'integrat\w*|comprehensive|combin\w*|context-aware|unif\w*|unit\w*|consolidat\w*|amalgamat\w*|join\w*|merg\w*|fus\w*|blend\w*|mesh\w*|coherent|dependency|interdependency|hierarchical|whole learner|holistic|multi-faceted'

run = df[
    (
        df['abstract'].str.contains(search1, case=False) |
        df['title'].str.contains(search1, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search1, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search2, case=False) |
        df['title'].str.contains(search2, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search2, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search3, case=False) |
        df['title'].str.contains(search3, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search3, i, flags=re.I) for i in x]).any())
    ) & (
        df['abstract'].str.contains(search4, case=False) |
        df['title'].str.contains(search4, case=False) |
        df['keywords'].apply(lambda x: pd.Series([re.findall(search4, i, flags=re.I) for i in x]).any())
    )
]

print(run.shape)
run = remove_duplicates(run)

run.shape


# %%
