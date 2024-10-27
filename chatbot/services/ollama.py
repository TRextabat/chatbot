from PyPDF2 import PdfReader
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, PromptTemplate, SimpleDirectoryReader
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
        self.check_model_ready(self)



    
    async def parse_pdf(self, pdf_path:str) -> str:
        try:
            f = open(pdf_path, "rb")
            reader = PdfReader(f)
            text = "".join([page.extract_text() for page in reader.pages])

            cleaned_text = self._clean_text(text)
            with tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False, suffix=".txt") as temp_file:
                temp_file.write(cleaned_text.encode('utf-8'))
            return self._clean_text(text)

        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise # TODO add massage 

    async def index_document(self, documents:str) -> VectorStoreIndex:
        
        try:
            self.reader = SimpleDirectoryReader(input_dir=self.temp_dir)
            documents = self.reader.load_data()

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
        
        prompt = self._optimize_prompt(user_query)
        for attempt in range(self.attempt):
            try:
                response = await sync_to_async(self.agent.query)(prompt)
                return response
            except Exception as e :
                print(os.environ.get("LLAMA_URL"))
                logger.error(f"Attempt {attempt + 1}: Error during agent query: {e} ")
            if attempt == self.attempt-1:  # Raise error on final attempt
                raise RuntimeError(f"Agent query failed after {attempt + 1} attempts.")

    def _optimize_prompt(self, user_query: str) -> str:
        """
        Customize and optimize the prompt based on the user's query for better context handling.
        """
        logger.debug(f"User query: {user_query}")
        if "summary" in user_query.lower():
            prompt_template = PromptTemplate(template=f"{self.context}\nSummarize this content:")
        else:
            prompt_template = PromptTemplate(template=f"{self.context}\nAnswer the following based on the document: {user_query.strip()}")

        prompt = prompt_template.format(context=self.context, query=user_query.strip())
        logger.debug(f"Final prompt: {prompt}")
        return prompt
    
    @staticmethod
    def check_model_ready(self):
        try:
            response = self.llm.query("Are you ready?")
            if "ready" in response.lower():
                return True
        except Exception as e:
            logger.error(f"Error checking model readiness: {e}")
        return False
    @staticmethod
    def _clean_text(text:str) -> str:

        # Remove page numbers, headers, footers, and extra newlines
        clean_text = re.sub(r'\s*\bPage\s+\d+\b', '', text)
        clean_text = re.sub(r'\n\s*\n', '\n', clean_text)  
        return clean_text.strip()
