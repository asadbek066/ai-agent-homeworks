import os
from dotenv import load_dotenv
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField, SearchableField, ComplexField, SearchFieldDataType,
    CorsOptions, SearchIndex, ScoringProfile)

load_dotenv()
SERVICE_ENDPOINT = os.environ["AZURE_SEARCH_SERVICE_ENDPOINT"]
INDEX_NAME = os.environ["AZURE_SEARCH_INDEX_NAME"]
SEARCH_API_KEY = os.environ["AZURE_SEARCH_API_KEY"]
INDEX_API_KEY = os.environ["KEYY"]

search_client = SearchClient(SERVICE_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_API_KEY))
index_client = SearchIndexClient(SERVICE_ENDPOINT, AzureKeyCredential(INDEX_API_KEY))

def search_documents(search_text: str):
    results = search_client.search(search_text=search_text)
    for result in results:
        print(f"Title: {result.get('title', 'N/A')}\nContent: {result.get('chunk', 'N/A')}\n\n")

search_documents("best place")

def create_index(index_name: str):
    fields = [
        SimpleField(name="hotelId", type=SearchFieldDataType.String, key=True),
        SimpleField(name="baseRate", type=SearchFieldDataType.Double),
        SearchableField(name="description", type=SearchFieldDataType.String),
        ComplexField(
            name="address",
            fields=[
                SimpleField(name="streetAddress", type=SearchFieldDataType.String),
                SimpleField(name="city", type=SearchFieldDataType.String),
            ],
            collection=True
        ),
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles: List[ScoringProfile] = []
    index = SearchIndex(
        name=index_name,
        fields=fields,
        scoring_profiles=scoring_profiles,
        cors_options=cors_options
    )
    return index_client.create_index(index)

def upload_document(index_name: str, document: dict):
    client = SearchClient(SERVICE_ENDPOINT, index_name, AzureKeyCredential(INDEX_API_KEY))
    result = client.upload_documents(documents=[document])
    print(f"Upload of new document succeeded: {result[0].succeeded}")

DOCUMENT = {
    "hotelId": "1000",
    "baseRate": 4.0,
    "address": [{
        "streetAddress": "Sample street address",
        "city": "London"
    }],
    "description": "Azure Inn"
}

upload_document("hotels", DOCUMENT)