import asyncio
import os
from .ollama import LlamaService


async def run_demo():
    # Initialize the service
    service = LlamaService()

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

# Run the demo
if __name__ == "__main__":
    asyncio.run(run_demo())
