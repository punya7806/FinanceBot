import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq




def get_llm():



    llm = ChatGroq(
        
        model="llama-3.1-8b-instant",


        api_key=os.getenv(

           "GROQ_API_KEY"

        )

    )


    return llm