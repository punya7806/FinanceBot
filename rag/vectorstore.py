from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embeddings


def create_vectorstore(chunks):

    embeddings = get_embeddings()


    vectorstore = FAISS.from_documents(
        chunks,
        embeddings
    )


    return vectorstore


def save_vectorstore(vectorstore):

    vectorstore.save_local(

        "faiss_index"

    )


from django.conf import settings
import os
path = os.path.join(settings.BASE_DIR, "faiss_index")


def load_vectorstore():

    embeddings = get_embeddings()


    vectorstore = FAISS.load_local(
        path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore