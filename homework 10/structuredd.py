import os
import asyncio
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
load_dotenv()
class Person(BaseModel):
    name: str = Field(description="Name")
    age: int = Field(description="Age")
    job: str = Field(description="Job")
class People(BaseModel):
    people: List[Person]
async def extract_data():
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )
    parser=PydanticOutputParser(pydantic_object=People)
    prompt=ChatPromptTemplate.from_messages([
        ('system', 'You are a helpful assistant. Extract information strictly.'),
        ('human', "{text}\n{format_instructions}")
    ]).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    r="John Doe is a 40 years old programmer. Adam Smith is 50 years old economist"
    res=await chain.ainvoke({'text': r})
    for person in res.people:
        print(f"Name: {person.name} | Age: {person.age} | Job: {person.job}")
asyncio.run(extract_data())