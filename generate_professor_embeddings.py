import numpy as np
import os
import openai
import pandas as pd
import time
import traceback
from openai.embeddings_utils import get_embedding
from tqdm import tqdm

"""
To obtain a key, go to `https://beta.openai.com/account/api-keys` and create an API key after making an OpenAI account.
"""

openai.api_key = os.getenv("OPENAI_API_KEY")
CHUNK_SIZE=2000

df = pd.read_csv("mit_professor_data_raw.csv")

df['embedding_school'] = [[] for _ in range(len(df))]
df['embedding_desc'] = [[] for _ in range(len(df))]
df['embedding_combined'] = [[] for _ in range(len(df))]
df['combined'] = "Title: " + df.name.str.strip() + "; Content: " + df.keywords.str.strip()
df.fillna('none', inplace=True) # fill all NaN's in the dataframe

# df_keys = ["course_number","title","hours","cluster","desc","terms","optional","instructors","prereq","embedding_title", "embedding_desc", "embedding_combined"]

pbar = tqdm(total=len(df))
for i in range(int(np.ceil(len(df)/CHUNK_SIZE))):
    start = i * CHUNK_SIZE
    end = start + CHUNK_SIZE
    end = min(end, len(df))
    model_title = openai.Embedding.create(model="text-embedding-ada-002", input=list(df['school_affiliation'][start:end]))
    model_desc = openai.Embedding.create(model="text-embedding-ada-002", input=list(df['keywords'][start:end]))
    model_combined = openai.Embedding.create(model="text-embedding-ada-002", input=list(df['combined'][start:end]))
    for j in range(end-start):
        embedding_title = model_title.data[j]['embedding']
        df.loc[start + j]['embedding_school'] = embedding_title
        embedding_desc = model_desc.data[j]['embedding']
        df.loc[start + j]['embedding_desc'] = embedding_desc
        embedding_combined = model_combined.data[j]['embedding']
        df.loc[start + j]['embedding_combined'] = embedding_combined
        pbar.update()
    
df.to_csv("mit_professors_with_embeddings.csv", index=False)
print("\n\nComplete!")