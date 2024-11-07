import os

import chromadb.utils.embedding_functions
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain.agents import initialize_agent, Tool
from langchain_chroma import Chroma

from langchain_core.output_parsers import StrOutputParser

from embeddings import get_default_embeddings

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")
# model = ChatAnthropic(model="claude-3-5-sonnet-20240620")

model = ChatMistralAI(model="mistral-large-latest")

parser = StrOutputParser()
chain = model | parser

vectorstore = Chroma(persist_directory="./db",
                     embedding_function=chromadb.utils.embedding_functions.DefaultEmbeddingFunction())
retriever = vectorstore.as_retriever()


def respond_to_message(user_message, embs):
    for i in chain.stream():
        retriever.g
        print(i)
