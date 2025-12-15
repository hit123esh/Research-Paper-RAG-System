"""
Document processing module for PDF extraction and chunking.
"""
import re
from typing import List, Dict, Any
import PyPDF2
import pdfplumber


class DocumentProcessor:
    """Handles PDF extraction and text chunking."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """
        Initialize document processor.

        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
        """
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # ------------------------------------------------------------------
    # PDF EXTRACTION
    # ------------------------------------------------------------------
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF with page-level metadata.
        """
        text_parts = []
        pages = []

        try:
            # Prefer pdfplumber (better layout handling)
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        clean_page = page_text.strip()
                        pages.append({
                            "page_number": page_num,
                            "text": clean_page
                        })
                        text_parts.append(
                            f"--- Page {page_num} ---\n{clean_page}"
                        )
        except Exception as e:
            print(f"[PDF] pdfplumber failed, falling back to PyPDF2: {e}")
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if page_text:
                        clean_page = page_text.strip()
                        pages.append({
                            "page_number": page_num,
                            "text": clean_page
                        })
                        text_parts.append(
                            f"--- Page {page_num} ---\n{clean_page}"
                        )

        full_text = "\n\n".join(text_parts)

        return {
            "text": full_text,
            "pages": pages,
            "total_pages": len(pages)
        }

    # ------------------------------------------------------------------
    # TEXT CLEANING
    # ------------------------------------------------------------------
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        """
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)\[\]\/]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    # ------------------------------------------------------------------
    # SECTION SPLITTING
    # ------------------------------------------------------------------
    def split_into_sections(self, text: str) -> List[str]:
        """
        Split text into sections based on common academic structure.
        """
        section_patterns = [
            r"\n\s*(Abstract|Introduction|Background|Related Work|Methodology|Methods|Method|Approach)",
            r"\n\s*(Results|Findings|Experiments|Evaluation|Analysis)",
            r"\n\s*(Discussion|Conclusion|Future Work|Limitations|References)",
            r"\n\s*\d+\.\s+[A-Z]",
            r"\n\s*[A-Z][A-Z\s]+\n",
        ]

        sections = []
        current = []

        for line in text.split("\n"):
            is_header = any(
                re.match(pattern, "\n" + line, re.IGNORECASE)
                for pattern in section_patterns
            )

            if is_header and current:
                sections.append("\n".join(current))
                current = [line]
            else:
                current.append(line)

        if current:
            sections.append("\n".join(current))

        return sections if sections else [text]

    # ------------------------------------------------------------------
    # SAFE CHUNKING (NO INFINITE LOOPS)
    # ------------------------------------------------------------------
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks safely.
        """
        import json
        text = self.clean_text(text)
        words = text.split()
        chunks = []

        if not words:
            return chunks

        # Approximate word-based chunk sizing
        words_per_chunk = int(self.chunk_size / 1.3)
        words_overlap = int(self.chunk_overlap / 1.3)

        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:137","message":"Chunking started","data":{"total_words":len(words),"words_per_chunk":words_per_chunk,"words_overlap":words_overlap,"chunk_size":self.chunk_size,"chunk_overlap":self.chunk_overlap},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion

        if words_overlap >= words_per_chunk:
            # #region agent log
            try:
                with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                    f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:142","message":"Overlap validation failed","data":{"words_overlap":words_overlap,"words_per_chunk":words_per_chunk},"timestamp":int(__import__('time').time()*1000)}) + '\n')
            except: pass
            # #endregion
            raise ValueError("Overlap too large — causes infinite loop")

        start_idx = 0
        chunk_id = 0
        total_words = len(words)
        max_iterations = (total_words // max(1, words_per_chunk - words_overlap)) + 10  # Safety limit
        iteration_count = 0

        while start_idx < total_words:
            iteration_count += 1
            # #region agent log
            if iteration_count % 10 == 0:  # Log every 10th iteration to avoid spam
                try:
                    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:155","message":"Chunking iteration","data":{"iteration":iteration_count,"start_idx":start_idx,"total_words":total_words,"chunks_created":len(chunks)},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
            # #endregion
            
            # Safety check: prevent infinite loops
            if iteration_count > max_iterations:
                # #region agent log
                try:
                    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:162","message":"Max iterations exceeded - breaking","data":{"iteration_count":iteration_count,"max_iterations":max_iterations,"start_idx":start_idx,"total_words":total_words},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                print(f"[WARNING] Chunking reached max iterations ({max_iterations}), breaking to prevent infinite loop")
                break

            end_idx = min(start_idx + words_per_chunk, total_words)
            chunk_words = words[start_idx:end_idx]
            chunk_text = " ".join(chunk_words)

            if chunk_text.strip():
                chunk_meta = {
                    **(metadata or {}),
                    "chunk_id": chunk_id,
                    "chunk_index": chunk_id,
                    "start_word": start_idx,
                    "end_word": end_idx
                }
                chunks.append({
                    "text": chunk_text,
                    "metadata": chunk_meta
                })
                chunk_id += 1

            # 🚨 CRITICAL: ensure forward progress
            next_start = end_idx - words_overlap
            if next_start <= start_idx:
                # #region agent log
                try:
                    with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                        f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:189","message":"No forward progress - breaking","data":{"next_start":next_start,"start_idx":start_idx,"end_idx":end_idx,"words_overlap":words_overlap},"timestamp":int(__import__('time').time()*1000)}) + '\n')
                except: pass
                # #endregion
                break

            start_idx = next_start

        # #region agent log
        try:
            with open('/Users/hiteshumesh/Desktop/Research_Paper/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"chunking","hypothesisId":"M","location":"document_processor.py:197","message":"Chunking completed","data":{"total_chunks":len(chunks),"iterations":iteration_count,"total_words":total_words},"timestamp":int(__import__('time').time()*1000)}) + '\n')
        except: pass
        # #endregion

        return chunks

    # ------------------------------------------------------------------
    # FULL PIPELINE
    # ------------------------------------------------------------------
    def process_pdf(self, pdf_path: str, paper_name: str) -> List[Dict[str, Any]]:
        """
        Full PDF → sections → chunks pipeline.
        """
        print(f"[PDF Processing] Starting extraction for: {paper_name}")
        extracted = self.extract_text_from_pdf(pdf_path)

        full_text = extracted["text"]
        pages = extracted["pages"]

        print(
            f"[PDF Processing] Extraction complete: "
            f"{len(pages)} pages, {len(full_text)} characters"
        )

        print("[PDF Processing] Starting section splitting...")
        sections = self.split_into_sections(full_text)
        print(f"[PDF Processing] Section splitting complete: {len(sections)} sections")

        print("[PDF Processing] Starting chunking...")
        all_chunks = []

        for section_idx, section_text in enumerate(sections):
            section_lines = section_text.split("\n")
            section_name = (
                section_lines[0][:50]
                if section_lines and len(section_lines[0]) < 100
                else "Unknown"
            )

            # Rough page estimation
            page_num = 1
            if pages:
                pos = full_text.find(section_text)
                if pos != -1:
                    page_num = min(
                        len(pages),
                        max(1, int((pos / len(full_text)) * len(pages)) + 1)
                    )

            base_metadata = {
                "paper_name": paper_name,
                "section": section_name,
                "section_index": section_idx,
                "page_number": page_num
            }

            section_chunks = self.chunk_text(section_text, base_metadata)
            all_chunks.extend(section_chunks)

        print(f"[PDF Processing] Chunking complete: {len(all_chunks)} chunks generated")
        return all_chunks
