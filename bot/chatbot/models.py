import os

from django.db import models, connections

from langchain_anthropic import ChatAnthropic
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, Docx2txtLoader, PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

import logging

from rest_framework.response import Response

connections.close_all()
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG for detailed logs
logger = logging.getLogger(__name__)


class Model:
    def __init__(self, files):
        self.files = files
        self.rag = self.model()

    def model(self):
        api_key = os.getenv("CLAUDE_API_KEY")

        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", api_key=api_key)
        embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        documents = []
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1].lower()
            logger.debug(f"Loading file: {file_path} with extension: {ext}")
            if ext == '.txt':
                loader = TextLoader(file_path)
                documents.extend(loader.load())
            elif ext == '.pdf':
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif ext == '.docx':
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())

        logger.debug(f"Documents loaded: {len(documents)}")

        # Split padel_documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
        processed_texts = []
        for document in documents:
            texts = text_splitter.split_text(document.page_content)
            processed_texts.extend(texts)

        logger.debug(f"Processed texts length: {len(processed_texts)}")

        try:
            chroma = Chroma()

            embeddings = embed_model.embed_documents(processed_texts)
            logger.debug(f"Embeddings length: {len(embeddings)}")

            if len(processed_texts) != len(embeddings):
                logger.error("Mismatch between processed texts and embeddings lengths")
                raise ValueError("Mismatch between processed texts and embeddings lengths")

            documents_for_vectorstore = [
                Document(page_content=text, embedding=embedding) for text, embedding in zip(processed_texts, embeddings)
            ]
            # Create vectorstore
            vectorstore = chroma.from_documents(documents=documents_for_vectorstore, embedding=embed_model)

            logger.info("Vectorstore created successfully")
        except Exception as e:
            logger.error(f"Error creating vectorstore: {e}", exc_info=True)
            raise  # Re-raise the exception to stop execution if vectorstore creation fails

        # Create retriever from vectorstore
        retriever = vectorstore.as_retriever()

        # Load RAG prompt
        prompt = hub.pull("rlm/rag-prompt")

        # Define function to format padel_documents for input
        def format_docs(ddocs):
            return "\n\n".join(doc.page_content for doc in ddocs)

        # Set up RAG chain
        rag_chain = (
                {
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | prompt
                | llm
                | StrOutputParser()
        )
        return rag_chain

    def chat(self, request):
        user_input = request.data.get("message")
        logger.debug(f"User input received: {user_input}")

        while True:
            if user_input.lower() in ['quit', 'exit', 'bye']:
                return Response({"message": "Goodbye!"})

            try:
                response = self.rag.invoke(user_input)
                return Response({"response": response})
            except Exception as e:
                return Response({"error": str(e)})


class User(models.Model):
    user_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.user_id

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email
        }

