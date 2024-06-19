import re
import fitz  #PDF_Reader
import requests #URL_Reader
from markdownify import markdownify as md
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma
from langchain.llms import HuggingFaceHub
from langchain.docstore.document import Document  # Import Document class
from transformers import pipeline

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_content):
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = text.lower()
    return text

# Helper function to extract text from URL
def extract_text_from_url(url):
    response = requests.get(url)
    text = md(response.text)  
    return text

# Helper function for dynamic chunking
def split_text_into_chunks(text, chunk_size, overlap):
    chunks = []
    start = 0
    end = chunk_size
    while start < len(text):
        chunks.append(text[start:end])
        start = end - overlap
        end = start + chunk_size
    return chunks

class ChatBot:
    def __init__(self, vectordb=None, document_chunks=None):
        self.vectordb = vectordb
        self.document_chunks = document_chunks
        self.chat_history = []  # Initialize an empty chat history
        self.initialize_chatbot()

    def initialize_chatbot(self):
        # Fine-tune language model with domain-specific data
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        if self.document_chunks:
            # Convert document_chunks into Document objects
            documents = [Document(page_content=chunk) for chunk in self.document_chunks]
            self.vectordb = Chroma.from_documents(documents, embeddings, persist_directory="database")

        llm = HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
                             model_kwargs={"temperature": 0.5, "max_length": 512}, 
                             huggingfacehub_api_token="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")
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=self.vectordb.as_retriever(search_kwargs={"k": 3})
        )

    def process_question(self, question):
        response = self.conversation_chain({"question": question, "chat_history": self.chat_history})
        answer = response.get("answer", None)
        helpful_answer = self.extract_helpful_answer(answer)
        # Update chat history
        self.chat_history.append((question, helpful_answer))  
        return helpful_answer

    def extract_helpful_answer(self, answer):
        if answer:
            helpful_answer_start = answer.find("\nHelpful Answer:")
            if helpful_answer_start != -1:
                return answer[helpful_answer_start + len("\nHelpful Answer:"):].strip()
        return answer.strip()

