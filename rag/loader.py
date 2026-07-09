from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader
)
import pdfplumber
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
def load_document(path):
    path = path.lower()
    if path.endswith(".pdf"):
        loader = PyPDFLoader(path)
    elif path.endswith(".docx"):
        loader = Docx2txtLoader(path)
    elif path.endswith(".csv"):
        loader = CSVLoader(path)
    elif path.endswith(".xlsx"):
        loader = UnstructuredExcelLoader(path)
    else:
        raise ValueError("Unsupported File Type")
    documents = loader.load()
    return documents
def extract_tables(path):
    all_tables=[]
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables=page.extract_tables()
            all_tables.extend(tables)
    return all_tables