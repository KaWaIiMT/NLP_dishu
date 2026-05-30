"""Convert HTML preview to PDF using Chromium (Playwright)"""
from playwright.sync_api import sync_playwright
import os

html_path = r"D:\_College\NLP\Research\_论文写作\output\paper_preview.html"
pdf_path = r"D:\_College\NLP\Research\_论文写作\output\paper_preview.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(f"file:///{html_path.replace(os.sep, '/')}")
    page.pdf(
        path=pdf_path,
        format='A4',
        margin={'top': '2cm', 'right': '2cm', 'bottom': '2cm', 'left': '2cm'},
        print_background=True,
    )
    browser.close()

print(f"PDF saved to: {pdf_path}")
print(f"Size: {os.path.getsize(pdf_path) / 1024:.1f} KB")
