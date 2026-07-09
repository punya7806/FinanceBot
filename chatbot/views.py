from django.shortcuts import render
from django.conf import settings
from .forms import UploadForm
from django.http import JsonResponse

from rag.loader import load_document
from rag.splitter import split_documents
from rag.vectorstore import create_vectorstore, save_vectorstore, load_vectorstore
from rag.retriever import retrieve_docs
from .agents import (
    finance_agent,
    general_agent,
    classify_agent
)
import os


def home(request):

    form = UploadForm()
    message = ""
    answer = ""
    question=""

    if request.method == "POST":

        # =========================
        # CHAT REQUEST
        # =========================
        if request.POST.get("chat") == "true":

            question = request.POST.get("question")
            print(question)

            if question:

                vectorstore = load_vectorstore()

                docs = retrieve_docs(vectorstore, question)

                answer = "\n\n".join([doc.page_content for doc in docs])

        # =========================
        # FILE UPLOAD REQUEST
        # =========================
        elif "file" in request.FILES:

            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():

                file = request.FILES['file']

                upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
                os.makedirs(upload_dir, exist_ok=True)

                path = os.path.join(upload_dir, file.name)

                # Detect file type
                file_ext = file.name.lower().split('.')[-1]

                if file_ext in ['pdf', 'docx']:
                    file_type = 'textual'
                elif file_ext in ['csv', 'xlsx']:
                    file_type = 'tabular'
                else:
                    file_type = 'unknown'

                # Store file metadata in session
                request.session['file_path'] = path
                request.session['file_type'] = file_type
                request.session['file_name'] = file.name

                with open(path, "wb+") as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # Index based on file type
                if file_type == 'textual':
                    # Use RAG indexing for text documents
                    docs = load_document(path)
                    chunks = split_documents(docs, file_type='textual')
                    vectorstore = create_vectorstore(chunks)
                    save_vectorstore(vectorstore)
                    message = f"✅ Upload Successful - {file.name} (Text Document - RAG Mode)"

                elif file_type == 'tabular':
                    # For tabular data, still create vectorstore but also note it's tabular
                    docs = load_document(path)
                    chunks = split_documents(docs, file_type='tabular')
                    vectorstore = create_vectorstore(chunks)
                    save_vectorstore(vectorstore)
                    message = f"✅ Upload Successful - {file.name} (Tabular Data - Pandas Mode)"

                else:
                    message = "❌ Unsupported file type. Please upload CSV, XLSX, PDF, or DOCX files."

    return render(request, "index.html", {
    "form": form,
    "message": message,
    "answer": answer,
    "question": question
})


def ask_question(request):

    if request.method == "POST":

        question = request.POST.get("question", "")
        path = request.session.get("file_path")
        file_type = request.session.get("file_type", "textual")  # Default to textual

        # Check if file is uploaded
        if not path:
            return JsonResponse({
                "question": question,
                "answer": "⚠️ Please upload a financial document first before asking questions."
            })

        intent = classify_agent(question)
        print("Intent:", intent)
        print("File type:", file_type)

        if intent == "finance":
            answer = finance_agent(question, path, file_type)
        else:
            answer = general_agent(question)

        return JsonResponse({
            "question": question,
            "answer": answer
        })

    return JsonResponse({
        "error": "Invalid request"
    })