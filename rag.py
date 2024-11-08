import os

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

hugging_face_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Chroma(client=chroma_client,
                     embedding_function=hugging_face_embeddings,
                     collection_name="my_embeddings"
                     )

def respond_to_message(user_message, asset_id):
    retriever = vectorstore.as_retriever(
        search_kwargs={
            'filter' : {'asset_id' : asset_id}
            }
        )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | parser
    )
    return rag_chain.stream(user_message)
