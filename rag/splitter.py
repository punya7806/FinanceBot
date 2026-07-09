from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def split_documents(documents, file_type='textual'):
    """
    Split documents based on file type

    Args:
        documents: List of Document objects
        file_type: 'textual' for PDF/DOCX (needs chunking),
                   'tabular' for CSV/XLSX (no chunking needed)

    Returns:
        List of Document chunks
    """

    # For tabular data (CSV/XLSX), don't chunk - keep full rows
    if file_type == 'tabular':
        chunks = []
        for doc in documents:
            chunks.append(
                Document(
                    page_content=doc.page_content,
                    metadata=doc.metadata
                )
            )
        return chunks

    # For textual data (PDF/DOCX), use proper chunking
    elif file_type == 'textual':
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

        chunks = splitter.split_documents(documents)
        return chunks

    else:
        # Default: no chunking
        return documents
