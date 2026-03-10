""" Module to open PDF and check for pending signatures. """
import pypdfium2 as pdfium


def compare_pdf(pdf_path: str) -> bool:
    """ Compare the PDF file with the expected content. """
    text = "\n".join(
        p.get_textpage().get_text_range()
        for p in pdfium.PdfDocument(pdf_path)
    )
    return "Não existem registos pendentes." in text
