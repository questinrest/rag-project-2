from pymongo import MongoClient
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
import certifi
import os

load_dotenv()


# MongoDB
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
DATABASE_NAME = "TierRAG"
db = client[DATABASE_NAME]
login_collection = db['devlogins']
document_collection = db['document_collection']
parent_store_collection = db['parent_store']

# JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pinecone
PINECONE_API_KEY : str = os.getenv("PINECONE_API_KEY")
PINECONE_CLOUD : str = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION : str = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME : str = os.getenv("PINECONE_INDEX_NAME", "tierrag")
PINECONE_EMBEDDING_MODEL : str = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
PINECONE_RERANKER_MODEL : str = os.getenv("PINECONE_RERANKER_MODEL", "bge-reranker-v2-m3")
BATCH_SIZE : int = int(os.getenv("BATCH_SIZE", 96))

# Retrieval
TOP_K : int = int(os.getenv("TOP_K", 10))
TOP_N : int = int(os.getenv("TOP_N", 5))


# Chunking Strategy
# choose from : "recursive_character", "parent_child"
CHUNKING_STRATEGY : str = os.getenv("CHUNKING_STRATEGY", "parent_child")

# Parent Child Chunking
PARENT_CHUNK_SIZE : int = int(os.getenv("PARENT_CHUNK_SIZE", 1000))
PARENT_CHUNK_OVERLAP : int = int(os.getenv("PARENT_CHUNK_OVERLAP", 200))
CHILD_CHUNK_SIZE : int = int(os.getenv("CHILD_CHUNK_SIZE", 200))
CHILD_CHUNK_OVERLAP : int = int(os.getenv("CHILD_CHUNK_OVERLAP", 20))


# Recursive Character Chunking
CHUNK_SIZE : int = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP : int = int(os.getenv("CHUNK_OVERLAP", 100))

# LLM (Groq)
GROQ_API_KEY : str = os.getenv("GROQ_API_KEY")
OPENAI_MODEL_GROQ : str = os.getenv("OPENAI_MODEL_GROQ", "llama-3.3-70b-versatile")
TEMPERATURE : float = float(os.getenv("TEMPERATURE", 0.2))
MAX_TOKENS : int = int(os.getenv("MAX_TOKENS", 1024))


# CACHE Settings
SEMANTIC_CACHE_THRESHOLD : float = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.92"))
RETRIEVAL_CACHE_THRESHOLD: float = float(os.getenv("RETRIEVAL_CACHE_THRESHOLD", "0.85"))
