import fitz
import pytesseract
from PIL import Image
import io
from langchain_core.documents import Document


def process_pdf(file_bytes):
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    all_docs = []

    for page_num, page in enumerate(doc):

        # -------- STEP 1: Raw text --------
        raw_text = page.get_text().strip()

        # -------- STEP 2: Blocks --------
        blocks = page.get_text("blocks")
        blocks = sorted(blocks, key=lambda b: (b[1], b[0]))  # sort top->bottom, left->right

        # -------- STEP 3: Multi-column --------
        if detect_multicolumn(blocks, page):
            blocks = handle_multicolumn(blocks, page)

        page_docs = []

        # -------- STEP 4: Process each block separately --------
        for block_idx, b in enumerate(blocks):
            block_text = b[4].strip()

            if not block_text:
                continue

            page_docs.append(Document(
                page_content=block_text,
                metadata={
                    "page": page_num,
                    "block": block_idx,
                    "type": "text"
                }
            ))

        # -------- STEP 5: Fallback if no blocks --------
        if not page_docs:
            if len(raw_text) > 50:
                page_docs.append(Document(
                    page_content=raw_text,
                    metadata={
                        "page": page_num,
                        "block": 0,
                        "type": "text_raw"
                    }
                ))
            else:
                ocr_text = extract_ocr(page)
                if ocr_text:
                    page_docs.append(Document(
                        page_content=ocr_text,
                        metadata={
                            "page": page_num,
                            "block": 0,
                            "type": "ocr"
                        }
                    ))

        # -------- STEP 6: Image OCR --------
        image_text = extract_images_ocr(doc, page)
        if image_text.strip():
            page_docs.append(Document(
                page_content=image_text,
                metadata={
                    "page": page_num,
                    "block": len(page_docs),
                    "type": "image_ocr"
                }
            ))

        all_docs.extend(page_docs)

    doc.close()
    return all_docs


def detect_multicolumn(blocks, page):
    if not blocks:
        return False

    mid_x = page.rect.width / 2

    left_blocks = [b for b in blocks if b[0] < mid_x]
    right_blocks = [b for b in blocks if b[0] >= mid_x]

    if len(left_blocks) > 2 and len(right_blocks) > 2:
        return True

    return False


def handle_multicolumn(blocks, page):
    mid_x = page.rect.width / 2

    left_blocks = []
    right_blocks = []

    for b in blocks:
        if b[0] < mid_x:
            left_blocks.append(b)
        else:
            right_blocks.append(b)

    left_blocks = sorted(left_blocks, key=lambda b: b[1])
    right_blocks = sorted(right_blocks, key=lambda b: b[1])

    return left_blocks + right_blocks


def extract_table(words):
    if not words:
        return ""

    rows = {}

    for w in words:
        y = round(w[1], -1)

        if y not in rows:
            rows[y] = []

        rows[y].append((w[0], w[4]))

    table_lines = []

    for y in sorted(rows.keys()):
        row = sorted(rows[y], key=lambda x: x[0])
        row_text = " | ".join(word for _, word in row)
        table_lines.append(row_text)

    return "\n".join(table_lines)


def extract_ocr(page):
    try:
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")

        image = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(image)

        return text.strip()

    except Exception:
        return ""


def extract_images_ocr(doc, page):
    image_list = page.get_images(full=True)

    all_text = []

    for img in image_list:
        try:
            xref = img[0]
            base_image = doc.extract_image(xref)

            image_bytes = base_image["image"]

            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)

            if text.strip():
                all_text.append(text.strip())

        except Exception:
            continue

    return "\n".join(all_text)
