from app.extractor import PDFSourceExtractor
from pathlib import Path
import csv
import re

MAX_TOKENS = 200   # safely below the model's 256 limit

"""
Recieves a text box, which is the text from the entire page, splitline splits the page into lines and seperates each line by "\n" as an item,
 not as a giant string with "\n"s. The page number is also passed once, so this function goes through the split page's text box, 
 and starts combining the string items if they don't exceed the chunk size into giant strings with "\n" inside of them, then whenever
 the giant string's size exceeds the chunk size, it stores that string as a list entry string, then starts the next string.
 In the end, it returns a list of strings, which are the page's text, split by "\n"s and chunks 
"""
def split_lines(text: str, count_tokens, max_tokens: int = MAX_TOKENS) -> list[str]:
    """Group whole lines into pieces of at most max_tokens tokens."""
    pieces = []
    current = ""
    footer_pattern = re.compile(r"\d+\s*/\s*\d+")
    title = "Arduino® Mega 2560 Rev3"
    for line in text.splitlines():
        if not line.strip():
            continue
        if footer_pattern.search(line):
            continue
        if title in line:
            continue
        candidate = current + "\n" + line if current else line
        if current and count_tokens(candidate) > max_tokens:
            pieces.append(current)    # adding this line would overflow: save the box
            current = line            # and start a new one
        else:
            current = candidate       # it still fits: keep filling
    if current:
        pieces.append(current)
    return pieces

""" 
Receives entire pages, with page numbers. 
Goes through each page; "content" represents a page with all its dictionary keys. its 'text' key contains the entire page's text.
It passes the page's text into split lines, which returns a list of strings, which are the lines that have been split
"""
def chunk_pdf_pages(pages: list[dict], document: str, count_tokens, max_tokens: int = MAX_TOKENS) -> list[dict]:
    def mostly_chinese(text, threshold=0.2):
        chinese = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
        return chinese / max(len(text), 1) > threshold

    chunks = []
    for content in pages:
        if mostly_chinese(content["text"], threshold=0.05):
            continue
        for piece in split_lines(content["text"], count_tokens, max_tokens):
            chunks.append({
                "document": document,
                "page": content["page"],
                "row": None,
                "text": piece
            })
    return chunks



"""
Opens the csv
does through each row (index = row number), for the content, it goes through the row content, "key" is the title of the column, and "value"
is the value of the item in that row from that column, in this case, the column names are the pin numbers, labels, functions, etc, it inserts 
the keys and their values into the list "row_pairs", then joins them into a string with ";" as the seperator indicator, and appends that string
into the result. It then appends everything into finalResult, in addition to an extra entry called "finalTable", which is a chunk of the entire 
csv table
"""
def chunk_csv_rows(csv_path, document:str, description: str = "") -> list[dict]:
    with open(str(csv_path), mode='r', encoding="utf-8-sig", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        result = {}
        finalTable = {"document":document, "page":None, "row":None, "text":""}
        finalResult = []
        table=[]
        for index, row in enumerate(reader, start=2):
            result["document"]=document
            result["page"]=None
            result["row"]=(index)

            row_pairs = [f"{key}: {value}" for key, value in row.items() if value and value.strip()]
            formatted_row = "; ".join(row_pairs)
            result["text"]=formatted_row
            table.append(formatted_row)
            finalResult.append(result)
            result = {}
        finalTable["text"] = (description + "\n" if description else "") + "\n".join(table)
        finalResult.append(finalTable)
    return(finalResult)



def chunk_pdf_pages_whole(pages: list[dict], document: str) -> list[dict]:
    chunks = []
    for content in pages:
        if not content["text"].strip(): 
            continue
        chunk = {}
        chunk["document"]=document
        chunk["page"]=content["page"]
        chunk["row"]=None
        chunk["text"]=content["text"]
        chunks.append(chunk)
    return chunks


if __name__ == "__main__":

    PROJECT_ROOT = Path(__file__).resolve().parents[2]   # llm.py → app → backend → engiMind
    PDF_PATH = PROJECT_ROOT / "documents" / "sample" / "A000067-datasheet.pdf"

    # --- Usage Example ---

    extractor = PDFSourceExtractor(PDF_PATH)
    extracted_pages = extractor.extract_text_by_page()



    """Rows chunked"""
    # csv_chunks = chunk_csv_rows("../documents/sample/ArduinoMegaPinReference.csv", "ArduinoMegaPinReference.csv")
    # print(csv_chunks[1])
    # print(len(csv_chunks))                              # expect 55
    # print(csv_chunks[0]["text"])                        # one readable line
    # print(type(csv_chunks[-1]["text"]), csv_chunks[-1]["text"].count("\n"))   # <class 'str'> 53
    # print(len(csv_chunks[-1]["text"]))                  # whole-table length



    """Pages chunked"""
    # chunks = chunk_pdf_pages_whole(extracted_pages, "A000067-datasheet.pdf")  
    # print(len(chunks))                                                        # expect 34
    # lengths = [len(c["text"]) for c in chunks]
    # print("chunks:", "shortest:", min(lengths), "| longest:", max(lengths))   # shortest text: 114 characters | longest text:2667 characters
    # print(chunks[0])                                                          # page 1's dictionary

    """Sub-Pages chunked"""
    # chunks = chunk_pdf_pages(extracted_pages, "A000067-datasheet.pdf", count_tokens)
    # print(len(chunks))#, "chunks | max tokens:", max(counts))
    # print(chunks[0])


