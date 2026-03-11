#type: ignore[attr-defined]
import pymupdf
from pymupdf import Page, Rect
from io import BytesIO
from app.models.resume_generation import ResumeGenerationPayLoad


def generate_resume_pdf(payload: ResumeGenerationPayLoad, pdf_bytes: bytes) -> BytesIO:

    original_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    new_doc = pymupdf.open()

    modifications = []

    for mod in payload.modifications:

        page_index = mod.segments[0].page - 1

        ys = [seg.y for seg in mod.segments]

        modifications.append({
            "page": page_index,
            "ys": ys,
            "text": mod.newText
        })

    for page_index in range(len(original_doc)):

        old_page: Page = original_doc[page_index]

        new_page: Page = new_doc.new_page(
            width=old_page.rect.width,
            height=old_page.rect.height
        )

        layout = old_page.get_text("dict")

        for block in layout["blocks"]:
            if block["type"] != 0:
                continue

            for line in block["lines"]:

                y = line["bbox"][1]

                replacement = None

                for mod in modifications:
                    if mod["page"] != page_index:
                        continue

                    for mod_y in mod["ys"]:
                        if abs(y - mod_y) < 3:
                            replacement = mod["text"]
                            break

                if replacement:

                    rect = Rect(
                        line["bbox"][0],
                        line["bbox"][1],
                        old_page.rect.width - 20,
                        line["bbox"][3] + 30
                    )

                    new_page.insert_textbox(
                        rect,
                        replacement,
                        fontsize=10,
                        fontname="helv"
                    )

                    continue

                for span in line["spans"]:

                    text = span.get("text")
                    if not text:
                        continue

                    x, y = span["origin"]
                    size = span.get("size", 10)

                    new_page.insert_text(
                        (x, y),
                        text,
                        fontsize=size,
                        fontname="helv"
                    )

    output = BytesIO()

    new_doc.save(output)

    new_doc.close()
    original_doc.close()

    output.seek(0)

    return output