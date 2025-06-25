import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Set USER_AGENT early
user_agent = os.getenv("USER_AGENT")
if user_agent:
    os.environ["USER_AGENT"] = user_agent
    print("USER_AGENT set to:", user_agent)
else:
    print("USER_AGENT not found in .env")

import getpass
import bs4
from flask import Blueprint, request, jsonify
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
import google.generativeai as genai
from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings

rag_routes = Blueprint("rag_routes", __name__)


# Access values
LANGCHAIN_API_KEY = os.getenv("LANGSMITH_API_KEY")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

if not LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
else:
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY

llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = InMemoryVectorStore(embeddings)

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
# N.B. for non-US LangSmith endpoints, you may need to specify
# api_url="https://api.smith.langchain.com" in hub.pull.
prompt = hub.pull("rlm/rag-prompt")

# RAG State
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}

def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}

# Build and compile graph
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()


@rag_routes.route("/api/ask/rag", methods=["POST"])
def ask_rag():
    data = request.get_json()

    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt"}), 400
    
    query = data["prompt"]

    response = graph.invoke({"question": query})

    return jsonify({"response": response["answer"]})