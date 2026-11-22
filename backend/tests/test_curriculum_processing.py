from io import BytesIO
from backend.app.services.curriculum_processing import extract_pages, make_chunks

def test_txt_page_and_chunk_provenance():
    pages = extract_pages(('Lesson 1\nMultiplication by three.\n' + 'Example: 3 x 4 = 12.\n' * 90).encode(), '.txt')
    chunks = make_chunks(pages)
    assert len(chunks) > 1
    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert all(c.page_number is None for c in chunks)
    assert all(c.content for c in chunks)

def test_pdf_page_tracking():
    import pymupdf
    pdf = pymupdf.open()
    p=pdf.new_page();p.insert_text((50,50),'Third grade fractions')
    chunks=make_chunks(extract_pages(pdf.tobytes(),'.pdf'))
    assert len(chunks)==1 and chunks[0].page_number==1
    assert 'fractions' in chunks[0].content

def test_docx_extraction():
    from docx import Document
    d=Document();d.add_heading('Unit 3',level=1);d.add_paragraph('Shapes and angles')
    stream=BytesIO();d.save(stream)
    pages=extract_pages(stream.getvalue(),'.docx')
    assert 'Shapes and angles' in pages[0][1]

def test_invalid_txt_encoding():
    import pytest
    with pytest.raises(ValueError):
        extract_pages(b'\xff\xfe\xff','.txt')
