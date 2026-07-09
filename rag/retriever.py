



def retrieve_docs(
        vectorstore,
        question
    ):
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k":5
        }
    )
    docs = retriever.invoke(question)
    return docs