from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings

from langchain_core.documents import Document
# from langchain_community.document_loaders import PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "shop_handbook.md"
text = DATA_PATH.read_text(encoding="utf-8")

doc = Document(page_content=text, metadata={"source": "data/shop_handbook.md"})
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)

chunks = text_splitter.split_documents(documents=[doc])


