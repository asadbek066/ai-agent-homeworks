import asyncio
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
async def main():
    prompt = ChatPromptTemplate.from_messages([
        ('system', 'You are a professional storyteller'),
        ('human', "Tell me a story about '{topic}'")
    ])

    llm = ChatOllama(model='gemma3', temperature=0.8)
    parser = StrOutputParser()

    chain = prompt | llm | parser

    async for token in chain.astream({'topic': 'Pumpkin'}):
        print(token, end='', flush=True)
asyncio.run(main())