""" Module to open PDF and check for pending signatures. """
import pypdfium2 as pdfium


def compare_pdf(pdf_path: str) -> bool:
    """ Compare the PDF file with the expected content. """
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        text = ""
        for page in pdf:
            text = page.get_textpage().get_text_range()

        return "Não existem registos pendentes." in text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False

if __name__ == "__main__":
    if compare_pdf("out/caderneta_pen.pdf"):
        print("Caderneta has no pending records.")
    else:
        print("The PDF content does not match the expected text or there was an error reading the file.")