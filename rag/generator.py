from rag.llm import get_llm


def generate_answer(

        docs,

        question

):

    llm = get_llm()


    context = "\n\n".join(

        [

            doc.page_content

            for doc in docs

        ]

    )


    prompt = f"""

You are a financial assistant.


Answer ONLY using context.


Context:


{context}



Question:


{question}



Answer:


"""


    response = llm.invoke(

        prompt

    )


    return response.content