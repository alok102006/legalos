import io
import fitz  # PyMuPDF
import docx
from app.shared.exceptions import BadRequestException


def parse_pdf(file_bytes: bytes) -> str:
    """Extracts text from PDF bytes using PyMuPDF (fitz)."""
    text_content = []
    try:
        # Open PDF from stream
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text_content.append(page.get_text())
        return "\n".join(text_content)
    except Exception as e:
        raise BadRequestException(f"Failed to parse PDF document: {str(e)}")


def parse_docx(file_bytes: bytes) -> str:
    """Extracts text from DOCX bytes using python-docx."""
    text_content = []
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            if para.text.strip():
                text_content.append(para.text)
        return "\n".join(text_content)
    except Exception as e:
        raise BadRequestException(f"Failed to parse DOCX document: {str(e)}")


def parse_txt(file_bytes: bytes) -> str:
    """Extracts text from plain text file bytes."""
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        raise BadRequestException(f"Failed to parse TXT document: {str(e)}")


def parse_document(file_bytes: bytes, filename: str) -> str:
    """
    Central document parser. Dispatches to matching parser based on file extension.
    Supported extensions: .pdf, .docx, .txt
    """
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return parse_pdf(file_bytes)
    elif ext == "docx":
        return parse_docx(file_bytes)
    elif ext in ["txt", "md"]:
        return parse_txt(file_bytes)
    else:
        raise BadRequestException(f"Unsupported file type: .{ext}. Supported formats are PDF, DOCX, TXT.")
