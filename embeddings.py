import os
import uuid

import PyPDF2
import docx
import chromadb
from chromadb.utils import embedding_functions
import openai

import dotenv
dotenv.load_dotenv()

DATABASE_PATH = "./db"
COLLECTION_NAME = "my_embeddings"

chroma_client = chromadb.PersistentClient(path=DATABASE_PATH)
chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
openai_client = openai.OpenAI()


def extract_from_txt(file_name: str) -> str:
    with open(file_name, "r") as f:
        return f.read()


def extract_from_pdf(file_name: str) -> str:
    reader = PyPDF2.PdfReader(file_name)
    text = ""
    for p in reader.pages:
        text += p.extract_text()
    return text


def extract_from_docx(file_name: str) -> str:
    doc = docx.Document(file_name)
    text = ""
    for p in doc.paragraphs:
        text += p.text
        text += "\n"
    return text


def get_file_text(file_name: str):
    arr = file_name.split(".")
    if len(arr) < 2:
        print("Invalid file name")
        return

    extension = arr[1]

    match extension:
        case "txt":
            return extract_from_txt(file_name)
        case "pdf":
            return extract_from_pdf(file_name)
        case "docx":
            return extract_from_docx(file_name)
        case _:
            print(f"file type '{extension}' not yet supported")


def get_default_embeddings(text):
    default_embedder = embedding_functions.DefaultEmbeddingFunction()
    emb = default_embedder([text])
    print(emb)
    return emb


def get_openai_embeddings(text):
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response


def get_asset_id():
    return str(uuid.uuid4())


def get_thread_id():
    return str(uuid.uuid4())


def save_embeddings(file_path):
    id = get_asset_id()
    file_data = get_file_text(file_path)
    chroma_collection.add(
        documents=[file_data],
        embeddings=get_default_embeddings(file_data)[0],
        metadatas=[{"file_path": file_path}],
        ids=[id],
    )
    return id


def get_embeddings(asset_id):
    results = chroma_collection.get(include=['embeddings', 'documents', 'metadatas'], ids=[asset_id])
    if len(results['ids']) == 0:
        return None
    else:
        return results['embeddings'][0]
