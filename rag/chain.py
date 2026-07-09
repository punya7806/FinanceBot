from rag.llm import get_llm




def ask_llama(

        docs,

        question

):



    llm = get_llm()



    context = "\n".join(

        [

            doc.page_content

            for doc in docs

        ]

    )




    prompt = f"""



Context:


{context}





Question:


{question}





Answer from context only.



"""




    response = llm.invoke(


        prompt


    )




    return response.content