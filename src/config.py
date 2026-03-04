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
DATABASE_NAME = "devRAG"
db = client[DATABASE_NAME]
login_collection = db['devlogins']
document_collection = db['document_collection']

# JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY", "b0954062d03562f160495c9263993d2f425c84e627a1c20a33ff18a602f56bdc")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Pinecone
PINECONE_API_KEY : str = os.getenv("PINECONE_API_KEY")
PINECONE_CLOUD : str = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION : str = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME : str = os.getenv("PINECONE_INDEX_NAME", "devrag")
PINECONE_EMBEDDING_MODEL : str = os.getenv("PINECONE_EMBEDDING_MODEL", "llama-text-embed-v2")
PINECONE_RERANKER_MODEL : str = os.getenv("PINECONE_RERANKER_MODEL", "bge-reranker-v2-m3")
BATCH_SIZE : int = int(os.getenv("BATCH_SIZE", 96))

# Retrieval
TOP_K : int = int(os.getenv("TOP_K", 10))
TOP_N : int = int(os.getenv("TOP_N", 5))


# Chunking
PARENT_CHUNK_SIZE : int = int(os.getenv("PARENT_CHUNK_SIZE", 1000))
PARENT_CHUNK_OVERLAP : int = int(os.getenv("PARENT_CHUNK_OVERLAP", 200))
CHILD_CHUNK_SIZE : int = int(os.getenv("CHILD_CHUNK_SIZE", 200))
CHILD_CHUNK_OVERLAP : int = int(os.getenv("CHILD_CHUNK_OVERLAP", 20))

# LLM (Groq)
GROQ_API_KEY : str = os.getenv("GROQ_API_KEY")
OPENAI_MODEL_GROQ : str = os.getenv("OPENAI_MODEL_GROQ", "llama-3.3-70b-versatile")
TEMPERATURE : float = float(os.getenv("TEMPERATURE", 0.2))
MAX_TOKENS : int = int(os.getenv("MAX_TOKENS", 1024))
