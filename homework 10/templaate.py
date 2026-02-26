import asyncio
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
async def translate_text(text: str, source_lang: str, target_lang: str):
    prompt = ChatPromptTemplate.from_messages([
        ('system', 'You are a professional {from_lang} to {to_lang} translator.'),
        ('human', "Translate the following text: '{text}'")
    ])
    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
    parser = StrOutputParser()
    chain = prompt | llm | parser
    inputs = {
        "text": text, 
        "from_lang": source_lang, 
        "to_lang": target_lang
    }
    result = await chain.ainvoke(inputs)
    print(f"Result: {result}")
asyncio.run(translate_text("Good morning", "English", "French"))