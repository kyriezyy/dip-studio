"""Document loader and parser for requirement documents."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Load and parse requirement documents in various formats."""
    
    def __init__(
        self,
        base_path: Path,
        supported_formats: list[str] | None = None
    ) -> None:
        """
        Initialize document loader.
        
        Args:
            base_path: Base directory containing requirement documents
            supported_formats: List of supported file extensions (e.g., [".pdf", ".md"])
        """
        self.base_path = Path(base_path).resolve()
        self.supported_formats = supported_formats or [".pdf", ".md", ".docx", ".txt"]
        
        # Ensure base path exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Cache for document metadata
        self._metadata_cache: dict[str, dict[str, Any]] = {}
        self._content_cache: dict[str, str] = {}
    
    def list_documents(self) -> list[dict[str, Any]]:
        """
        List all available documents in the base path.
        
        Returns:
            List of document metadata dictionaries
        """
        documents = []
        
        if not self.base_path.exists():
            logger.warning(f"Base path does not exist: {self.base_path}")
            return documents
        
        for file_path in self.base_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                doc_id = file_path.stem
                metadata = self._get_file_metadata(file_path)
                documents.append({
                    "id": doc_id,
                    "filename": file_path.name,
                    "path": str(file_path),
                    "format": file_path.suffix.lower(),
                    **metadata
                })
        
        return documents
    
    def load_document(self, doc_id: str) -> str:
        """
        Load and parse a document by ID.
        
        Args:
            doc_id: Document identifier (filename without extension)
        
        Returns:
            Document content as text
        """
        # Check cache first
        if doc_id in self._content_cache:
            return self._content_cache[doc_id]
        
        # Find the document file
        doc_file = self._find_document(doc_id)
        if not doc_file:
            raise FileNotFoundError(f"Document not found: {doc_id}")
        
        # Parse based on file extension
        content = self._parse_document(doc_file)
        
        # Cache the content
        self._content_cache[doc_id] = content
        
        return content
    
    def get_metadata(self, doc_id: str) -> dict[str, Any]:
        """
        Get metadata for a document.
        
        Args:
            doc_id: Document identifier
        
        Returns:
            Document metadata dictionary
        """
        if doc_id in self._metadata_cache:
            return self._metadata_cache[doc_id]
        
        doc_file = self._find_document(doc_id)
        if not doc_file:
            raise FileNotFoundError(f"Document not found: {doc_id}")
        
        metadata = self._get_file_metadata(doc_file)
        self._metadata_cache[doc_id] = metadata
        
        return metadata
    
    def _find_document(self, doc_id: str) -> Path | None:
        """Find document file by ID (trying different extensions)."""
        for ext in self.supported_formats:
            doc_path = self.base_path / f"{doc_id}{ext}"
            if doc_path.exists():
                return doc_path
        
        # Also try exact filename match
        doc_path = self.base_path / doc_id
        if doc_path.exists() and doc_path.is_file():
            return doc_path
        
        return None
    
    def _parse_document(self, file_path: Path) -> str:
        """Parse document based on file extension."""
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".md":
            return self._parse_markdown(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext == ".txt":
            return self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file."""
        try:
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            return "\n\n".join(text_parts)
        except ImportError:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                
                text_parts = []
                with open(file_path, "rb") as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                
                return "\n\n".join(text_parts)
            except ImportError:
                raise ImportError(
                    "PDF parsing requires either pdfplumber or PyPDF2. "
                    "Install with: pip install pdfplumber or pip install PyPDF2"
                )
    
    def _parse_markdown(self, file_path: Path) -> str:
        """Parse Markdown file."""
        return file_path.read_text(encoding="utf-8")
    
    def _parse_docx(self, file_path: Path) -> str:
        """Parse Word document."""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n".join(text_parts)
        except ImportError:
            raise ImportError(
                "Word document parsing requires python-docx. "
                "Install with: pip install python-docx"
            )
    
    def _parse_text(self, file_path: Path) -> str:
        """Parse plain text file."""
        return file_path.read_text(encoding="utf-8")
    
    def _get_file_metadata(self, file_path: Path) -> dict[str, Any]:
        """Get file metadata."""
        stat = file_path.stat()
        return {
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "format": file_path.suffix.lower()
        }
    
    def clear_cache(self) -> None:
        """Clear document caches."""
        self._metadata_cache.clear()
        self._content_cache.clear()
