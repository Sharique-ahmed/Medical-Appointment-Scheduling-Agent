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

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Created index {INDEX_NAME}")

index = pc.Index(INDEX_NAME)

# Load the JSONL we prepared
vectors_to_upsert = []
batch_size = 100

with open("faq.json", "r", encoding="utf-8") as f:
    faqs = json.load(f)

for item in tqdm(faqs, desc="Embedding & upserting 100 FAQs"):
    # Recommended: embed both question + answer together → much better retrieval
    text_to_embed = f"Question: {item['question']} Answer: {item['answer']}"

    embedding = openai.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text_to_embed
    ).data[0].embedding

    vectors_to_upsert.append({
        "id": item["id"],
        "values": embedding,
        "metadata": {
            "question": item["question"],
            "answer":   item["answer"],
            "category": item.get("category", "")
        }
    })

    # Upsert in batches of 100 (Pinecone limit is actually 1000, but 100 is safe & fast)
    if len(vectors_to_upsert) >= batch_size:
        index.upsert(vectors=vectors_to_upsert)
        vectors_to_upsert = []

# Final batch
if vectors_to_upsert:
    index.upsert(vectors=vectors_to_upsert)

print("Successfully inserted 150 clinic FAQs into Pinecone!")
print(f"Index stats: {index.describe_index_stats()}")

