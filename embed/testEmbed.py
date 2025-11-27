import os
import json
from tqdm import tqdm
import openai
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# ==== CONFIG ====
INDEX_NAME         = "clinic-faq"
EMBEDDING_MODEL    = "text-embedding-3-small"   # or text-embedding-ada-002
DIMENSION = 1536

openai.api_key = os.getenv('openAIKey')

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("vectorDb"))
index = pc.Index(INDEX_NAME)

#-----------------------------
query = "Is there any parking facilities available in the clinic"
xq = openai.embeddings.create(model=EMBEDDING_MODEL, input=query).data[0].embedding

results = index.query(vector=xq, top_k=3, include_metadata=True)
print(results)
for r in results.matches:
    print(f"{r.score:.3f} → {r.metadata['question']}")
    print(f"     {r.metadata['answer']}\n")

