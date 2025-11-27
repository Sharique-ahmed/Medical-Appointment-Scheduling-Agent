import os
from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("openAIKey")
print(OPENAI_API_KEY)
if OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
    raise RuntimeError("Missing OPENAI_API_KEY. Please set environment variable `openAIKey`")

PINECONE_API_KEY = os.getenv("vectorDb")
if PINECONE_API_KEY == "YOUR_PINECONE_API_KEY":
    raise RuntimeError("Missing PINECONE_API_KEY. Please set environment variable `vectorDb`")

CALENDLY_TOKEN = os.getenv("calendlyKey")
if CALENDLY_TOKEN == "YOUR_CALENDLY_API_KEY":
    raise RuntimeError("Missing CALENDLY_TOKEN. Please set environment variable `calendlyKey`")

PINECONE_INDEX = os.getenv("dbIndex")
EMBEDDING_MODEL = os.getenv("embeddingModel")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" or "anthropic"
CALENDLY_TOKEN = os.getenv("calendlyKey")

BASE_CALENDLY_URL = "https://api.calendly.com"

# Setting up a openAI client
gptClient = OpenAI(api_key=OPENAI_API_KEY)

# Setting up a Pinecone Client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)