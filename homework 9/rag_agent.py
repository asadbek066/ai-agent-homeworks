import os
from google.genai import Client,types
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
load_dotenv()



service_endpoint,index_name = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"], os.environ["AZURE_SEARCH_INDEX_NAME"]
key = os.environ["AZURE_SEARCH_API_KEY"]

search_client = SearchClient(service_endpoint, index_name, AzureKeyCredential(key))

def az_ai_retrieve(query: str):
    """
    Use this tool to retrieve travel related documents based on `query` parameter.
    """
    results = search_client.search(search_text=query)

    text = ''
    for result in results:
        text += f"Source: {result['title']} \n Content: {result['chunk']}\n\n"
    
    return text

client = Client()

config = types.GenerateContentConfig(
    tools=[az_ai_retrieve],
    system_instruction="""
    You are a RAG assistant.
    You MUST always call the provided tool to answer the user's question.
    When answering, give references to the sources by the tool.
"""
)

response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents="""What the the best place to travel?""",
    config=config
)

print(response.text)