import asyncio
import os
from .ollama import LlamaService


async def run_demo():
    # Initialize the service
    service = LlamaService()

    # Path to the PDF file to be indexed
    pdf_path = "uploads/pdfs/Back_end_takehome.pdf"  # Update this to the actual path of the PDF file

    print("Parsing PDF and generating embeddings...")
    # Parse PDF, clean text, chunk it, and generate embeddings
    await service.parse_pdf([pdf_path])

    print("Indexing document for querying...")
    # Index the document, which prepares it for efficient querying
    await service.index_document()
    
    # Example chat history for initializing the agent
    chat_history = ["Can you provide an overview of the document?"]

    print("Creating the agent with query tools...")
    # Create the agent with the sample chat history
    await service.create_agent(chat_history)

    # Define a user query to test the agent’s response
    user_query = "Which framework shoud I use ?"
    print(f"Sending query to agent: {user_query}")

    # Query the agent and get a response
    response = await service.agent_query(user_query)
    print("Agent Response:", response)

    """ service = LlamaService()

    # Path to the PDF file to be indexed
    pdf_path = "uploads/pdfs/Back_end_takehome.pdf"  # Replace with your actual PDF path

    # Parse PDF and index document
    parsed_text = await service.parse_pdf(pdf_path)
    
    # Print the entire parsed text for debugging
    print("Parsed PDF Text:", parsed_text)  # Print entire text

    # Index the document text directly as a list of strings
    await service.index_document(parsed_text)
    print("doc indexed")

    # Create agent with sample chat history
    chat_history = ["whhich enpoints I need in app"]
    await service.create_agent(chat_history)
    print("agent crated ")

    # Query the agent
    user_query = "What is this document about?"
    response = await service.agent_query(user_query)
    print("Agent Response:", response)
 """
# Run the demo
if __name__ == "__main__":
    asyncio.run(run_demo())
