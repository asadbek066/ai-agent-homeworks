from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI


client=OpenAI(base_url='http://localhost:11434/v1',api_key='ollama')

history=[]
while True:
    user_input=input('User: ')
    if user_input.strip()=='/bye':
        break
    history+=[
        {
            'role':'user',
            'content':user_input
        }
    ]
    response=client.chat.completions.create(
        model="ollam_model_version",
        messages=history
    )
    ans=response.choices[0].message.content
    print("Agent:", ans)
    history+=[
        {
            'role':'assistant','content':ans
        }
    ]