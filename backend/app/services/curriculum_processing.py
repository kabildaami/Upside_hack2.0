"""Deterministic extraction/chunking. No embeddings or LLM calls at this stage."""
from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
import re

@dataclass(frozen=True)
class Chunk:
    index: int
    page_number: int | None
    heading: str | None
    content: str


def extract_pages(data: bytes, extension: str) -> list[tuple[int | None, str]]:
    if extension == '.pdf':
        import pymupdf
        try:
            pdf = pymupdf.open(stream=data, filetype='pdf')
            if pdf.needs_pass:
                raise ValueError('Password-protected PDFs are unsupported.')
            if pdf.page_count > 500:
                raise ValueError('PDF is too long (maximum 500 pages).')
            result = [(i+1, page.get_text(sort=True)) for i, page in enumerate(pdf)]
            pdf.close()
            return result
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError('Unable to parse PDF.') from exc
    if extension == '.docx':
        from docx import Document
        try:
            document = Document(BytesIO(data))
            lines = [p.text.strip() for p in document.paragraphs if p.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    lines.append(' | '.join(cell.text.strip() for cell in row.cells))
            return [(None, '\n'.join(lines))]
        except Exception as exc:
            raise ValueError('Unable to parse DOCX.') from exc
    if extension == '.txt':
        try:
            return [(None, data.decode('utf-8-sig'))]
        except UnicodeError as exc:
            raise ValueError('Text files must be UTF-8 encoded.') from exc
    raise ValueError('Unsupported document type.')


def make_chunks(pages: list[tuple[int | None, str]], target_chars: int=900, overlap_chars: int=120) -> list[Chunk]:
    if not (0 <= overlap_chars < target_chars):
        raise ValueError('Invalid overlap size.')
    chunks = []
    for page_number, raw in pages:
        content = re.sub(r'\r\n?', '\n', raw)
        content = re.sub(r'[ \t]+', ' ', content)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        if not content:
            continue
        # Preserve page provenance; break at paragraph/sentence/space whenever possible.
        start = 0
        while start < len(content):
            end = min(start + target_chars, len(content))
            if end < len(content):
                window = content[start:end]
                candidates = [window.rfind('\n\n'), window.rfind('. '), window.rfind(' ')]
                split = next((i for i in candidates if i > target_chars//2), None)
                if split is not None:
                    end = start + split + (2 if window[split:split+2] in ('. ', '\n\n') else 1)
            piece = content[start:end].strip()
            if piece:
                first = next((x.strip() for x in piece.splitlines() if x.strip()), '')
                heading = first[:160] if len(first) < 120 and len(piece.splitlines()) > 1 else None
                chunks.append(Chunk(len(chunks), page_number, heading, piece))
            if end >= len(content):
                break
            start = max(start+1, end-overlap_chars)
    return chunks
