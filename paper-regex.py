# %%
import pandas as pd
import numpy as np

acm_df = pd.read_csv('database-search/ACM_Run1_168.csv')
ebsco_df = pd.read_csv('database-search/EBSCO_Run1_partial.csv')
scopus_df = pd.read_csv('database-search/Scopus_Run1a_3661.csv')
wos_df = pd.read_csv('database-search/WebOfScience_Run1a_786.csv')
ieee_df = pd.read_csv('database-search/IEEE_Run1_565.csv')


# %%
# Extract and organize relevant fields (ACM)

# Combine into single column to replace NaNs
acm_df['Journal'] = acm_df['Journal'].combine_first(acm_df['Proceedings title'])

acm_df = acm_df[['Authors', 'Title', 'Publication year', 'Abstract', 'Keywords', 'Journal']]
acm_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
acm_df['source'] = 'ACM'


# %%
# Extract and organize relevant fields (EBSCO)

ebsco_df = ebsco_df[['Authors', 'Title', 'Publication year', 'Abstract', 'Keywords', 'Journal']]
ebsco_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
ebsco_df['source'] = 'EBSCO'


# %%
# Extract and organize relevant fields (Scopus)

scopus_df = scopus_df[['Authors', 'Title', 'Year', 'Abstract', 'Index Keywords', 'Source title']]
scopus_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
scopus_df['source'] = 'Scopus'


# %%
# Extract and organize relevant fields (WOS)

# FIXME: is there a better field here than 'Author Keywords'?
wos_df = wos_df[['Authors', 'Article Title', 'Publication Year', 'Abstract', 'Author Keywords', 'Source Title']]
wos_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
wos_df['source'] = 'WOS'


# %%
# Extract and organize relevant fields (IEEE)

ieee_df = ieee_df[['Authors', 'Document Title', 'Publication Year', 'Abstract', 'Author Keywords', 'Publication Title']]
ieee_df.columns = ['authors', 'title', 'year', 'abstract', 'keywords', 'publication']
ieee_df['source'] = 'IEEE'


# %%
# Concatenate all data
df = pd.concat([acm_df, ebsco_df, scopus_df, wos_df, ieee_df])
df = df.reset_index(drop=True)


# %%
# Get duplicates
unique_S = df['title'].str.lower() + df['year'].astype('str')

duplicates_S = pd.Series([unique_S.iloc[i] in unique_S.iloc[:i].values for i in range(len(unique_S))])
print('duplicates:', duplicates_S.sum())

# Remove duplicates
df = df[~duplicates_S].reset_index(drop=True)


# %%
df[
    (
        df['abstract'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['title'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['keywords'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False)
    )
]


# %%
# Run 1

df[
    (
        df['abstract'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['title'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['keywords'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False)
    ) & (
        df['abstract'].str.contains('educat\w*|tutor\w*|instruct\w*|learning system\w*|learning environment\w*', case=False) |
        df['title'].str.contains('educat\w*|tutor\w*|instruct\w*|learning system\w*|learning environment\w*', case=False) |
        df['keywords'].str.contains('educat\w*|tutor\w*|instruct\w*|learning system\w*|learning environment\w*', case=False)
    )
]


# %%
# Run 2

df[
    (
        df['abstract'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['title'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False) |
        df['keywords'].str.contains('knowledge tracing|learner model\w*|student model\w*', case=False)
    ) & (
        df['abstract'].str.contains('educat\w*|tutor\w*|instruct\w*', case=False) |
        df['title'].str.contains('educat\w*|tutor\w*|instruct\w*', case=False) |
        df['keywords'].str.contains('educat\w*|tutor\w*|instruct\w*', case=False)
    )
]


# %%
df.isna().sum()

# FIXME: Lots of missing data!


# %%
for i in [acm_df, ebsco_df, scopus_df, wos_df]:
    print(i['source'].iloc[0])
    print('======')
    print(i.isna().sum())
    print()

# Looks like all the missing titles and most of the other missing data is coming from EBSCO


# %%
