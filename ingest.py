import os
import hashlib
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
def get_file_hash(file_path):
    """Compute MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

try:
    # Verify PDF file exists
    # pdf_path = "django_documentation/django-readthedocs-io-en-5.2.x.pdf"
    pdf_path = "django_documentation/django-readthedocs-io-en-5.2.x.pdf"
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")

    # Initialize lightweight embedding model
    embedding_model = HuggingFaceEmbeddings(
    model_name='sentence-transformers/all-MiniLM-L6-v2'
)

    # Check if FAISS index exists and matches PDF
    faiss_index_path = "faiss_index"
    hash_file_path = "faiss_index/pdf_hash.txt"
    pdf_hash = get_file_hash(pdf_path)
    index_exists = os.path.exists(faiss_index_path)

    if index_exists:
        # Check if PDF hash matches stored hash
        stored_hash = None
        if os.path.exists(hash_file_path):
            with open(hash_file_path, "r") as f:
                stored_hash = f.read().strip()

        if stored_hash == pdf_hash:
            print(f"📂 Found valid FAISS index at {faiss_index_path}")
            vectorstore = FAISS.load_local(
                faiss_index_path,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            print("✅ Loaded existing FAISS index successfully")
        else:
            print(f"📂 Index exists but PDF has changed. Recreating index...")
            index_exists = False  # Force recreation
    else:
        print(f"📂 No FAISS index found at {faiss_index_path}. Creating new index...")

    if not index_exists:
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        print(f"Length of raw Docs 📁: {len(docs)}")  # Expected: 2888

        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
        split_docs = text_splitter.split_documents(docs)
        print(f"🔧 Split into {len(split_docs)} chunks")  # Expected: 9880

        # Create and save FAISS index
        vectorstore = FAISS.from_documents(split_docs, embedding_model)
        vectorstore.save_local(faiss_index_path)
        # Save PDF hash
        os.makedirs(faiss_index_path, exist_ok=True)
        with open(hash_file_path, "w") as f:
            f.write(pdf_hash)
        print("✅ FAISS index and PDF hash saved successfully")

except Exception as e:
    print(f"❌ Error: {str(e)}")