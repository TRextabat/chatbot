from PyPDF2 import PdfReader
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, PromptTemplate, SimpleDirectoryReader, Document
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from asgiref.sync import sync_to_async
import tempfile
import shutil
import os
import re
import logging
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


load_dotenv()

logger = logging.getLogger(__name__)

#TODO add doc string


class LlamaService:
    def __init__(
                self, model_version="llama3.1", 
                 request_timeout=120, 
                 base_url=os.environ.get("LLAMA_URL")
                 ) -> None:

        self.llm = Ollama(model=model_version, request_timeout=request_timeout, base_url=base_url)
        self.embed_model = resolve_embed_model("local:BAAI/bge-m3")
        self.query_engine = None
        self.agent = None
        self.context = ""
        self.attempt = 3
        self.temp_dir= tempfile.mkdtemp()
        self.reader = None
        self.text_chunks = []       



    
    async def parse_pdf(self, pdf_path:str, chuck_size=500) -> None:
        try:
            f = open(pdf_path, "rb")
            reader = PdfReader(f)
            text = "".join([page.extract_text() for page in reader.pages])

            cleaned_text = self._clean_text(text)
            self.text_chunks = self._chunk_text(cleaned_text, chuck_size)
           
            

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise # TODO add massage 

    async def index_document(self) -> None:
        
        try:
            documents = [Document(text=chunk) for chunk in self.text_chunks]
            
            index = VectorStoreIndex.from_documents(
                documents=documents,
                embed_model=self.embed_model
                )
            self.query_engine = index.as_query_engine(llm=self.llm)
            logger.info("Successfully created index for parsed documents.")
            return index
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            raise


    async def create_agent(self, chat_history: list):

        if not self.query_engine:
            raise ValueError("Query engine is not initialized")

        tools = [
            QueryEngineTool(
                query_engine=self.query_engine,
                metadata=ToolMetadata(
                    name="document_query",
                    description="Use this tool to query the indexed PDF documents.",
                    
                ),
            )
        ]

        self.agent = await sync_to_async(ReActAgent.from_tools)(
            tools=tools,
            llm=self.llm,
            chat_history=chat_history
        )

    async def agent_query(self, user_query:str) -> str:

        if not self.agent:
            raise ValueError("agenr is not initialized")
        
        #top_chuncks = await self._retrieve_relevant_chunks(user_query, top_k=5)
        #context_text= " ".join(top_chuncks)
        
        #prompt = self._optimize_prompt(user_query, context_text)
        for attempt in range(self.attempt):
            try:
                response = await sync_to_async(self.agent.query)(user_query)
                return response
            except Exception as e :
                print(os.environ.get("LLAMA_URL"))
                logger.error(f"Attempt {attempt + 1}: Error during agent query: {e} ")
            if attempt == self.attempt-1:  # Raise error on final attempt
                raise RuntimeError(f"Agent query failed after {attempt + 1} attempts.")


   
    
    @staticmethod
    def _chunk_text(text: str, chunk_size: int) -> list:
        """Split text into smaller chunks based on specified size."""
        words = text.split()
        return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    @staticmethod
    def _clean_text(text:str) -> str:

        # Remove page numbers, headers, footers, and extra newlines
        clean_text = re.sub(r'\s*\bPage\s+\d+\b', '', text)
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)  
        return clean_text.strip()














'''async def _retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> list:
        """Retrieve the top-k most relevant chunks based on cosine similarity with the query."""
        query_embedding = await sync_to_async(self.embed_model._embed)(query)
        similarities = cosine_similarity([query_embedding], self.embeddings_cache).flatten()
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [self.text_chunks[i] for i in top_indices]


        def _optimize_prompt(self, user_query: str, context_text:str) -> str:
        """
        Customize and optimize the prompt based on the user's query for better context handling.
        """
        logger.debug(f"User query: {user_query}")
        prompt_template = PromptTemplate(template=f"{context_text}\n{user_query.strip()}")
        return prompt_template.template
    
    '''