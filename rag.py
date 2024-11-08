import os
import datetime

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_mistralai import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser

from embeddings import chroma_client

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")
os.environ["MISTRAL_API_KEY"] = os.getenv("MISTRAL_API_KEY")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

llm = ChatMistralAI(model="mistral-large-latest")
parser = StrOutputParser()
prompt = hub.pull("rlm/rag-prompt") 

hugging_face_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(client=chroma_client,
                     embedding_function=hugging_face_embeddings,
                     collection_name="my_embeddings"
                     )

chat_history = {}

def respond_to_message(user_message, asset_id, thread_id):
    retriever = vectorstore.as_retriever(
        search_kwargs={
            'filter': {'asset_id': asset_id},
            'k': 1
        }
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    '''
    As we've seen above, the input to prompt is expected to be a dict with keys "context" and "question". So the first element of this chain builds runnables that will calculate both of these from the input question:

    retriever | format_docs passes the question through the retriever, generating Document objects, and then to format_docs to generate strings;
    RunnablePassthrough() passes through the input question unchanged.
    '''

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
    stream = rag_chain.stream(user_message)
    return stream

def get_history(thread_id):
    return chat_history.get(thread_id, None)
    return