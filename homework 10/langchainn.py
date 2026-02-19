from dotenv import load_dotenv
load_dotenv()
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ---------------------- Gemini --------------------------------
# from langchain_google_genai import ChatGoogleGenerativeAI
# llm=ChatGoogleGenerativeAI(model='gemini-2.5-flash')
# --------------------Azure OpenAI------------------------------
# from langchain_openai import AzureChatOpenAI
# llm=AzureChatOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
#     api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
# )
#  ----------------------------Ollama-------------------------
# from langchain_ollama import ChatOllama
# llm=ChatOllama(model='deepseek-r1:7b')

# -----------------------HuggingFace---------------------------
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
import torch

model_id = "microsoft/Phi-3-mini-4k-instruct"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
)
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    temperature=0.7,
    do_sample=True
)

llm = HuggingFacePipeline(pipeline=pipe)

history = []

while True:
    user_input = input("User: ")
    if user_input.strip() == "/bye":
        break

    history.append(HumanMessage(content=user_input))
    response = llm.invoke(history)
    ans = response.content

    print("Agent:", ans)
    history.append(AIMessage(content=ans))
