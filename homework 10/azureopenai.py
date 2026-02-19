import os
from openai import AzureOpenAI
from dotenv import load_dotenv
load_dotenv()
client=AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)
history=[
    {
        'role':'user',
        'content':'Hi'
    }
]

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
        model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        messages=history
    )
    ans=response.choices[0].message.content
    print("Agent:", ans)
    history+=[
        {
            'role':'assistant','content':ans
        }
    ]