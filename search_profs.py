import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity

def search_profs(df, search_query, n):
    embedding = get_embedding(
        search_query,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, embedding))
    results = (df.sort_values("similarity", ascending=False).head(n).combined.str.replace("Title: ", "").str.replace("; Content:", ": "))
    professors = df.sort_values("similarity", ascending=False).head(n).name
    return professors