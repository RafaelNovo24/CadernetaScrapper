""" Module to run the script to compare two pdf files. """
from webscrapper import get_certificate
from pdf_verification import compare_pdf

if __name__ == "__main__":
    get_certificate()
    return compare_pdf("caderneta.pdf")
