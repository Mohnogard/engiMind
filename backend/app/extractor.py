from pypdf import PdfReader


class PDFSourceExtractor:

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)

    def get_num_pages(self) -> int:
        return len(self.reader.pages)

    def extract_text_by_page(self) -> list[dict]:
        """Extracts text page by page with metadata for citation."""
        extracted_data = []

        for index, page in enumerate(self.reader.pages):
            page_text = page.extract_text()
            extracted_data.append(
                {
                    "page": index + 1,  # 1-indexed for human citations
                    "text": page_text.strip() if page_text else "",
                }
            )

        return extracted_data
    
 