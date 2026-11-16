---
name: pdf-ops
description: "Does the work a PDF editor subscription would: merge, split, reorder, rotate, redact, compress, watermark, extract text and tables, fill forms and build new PDFs. Use whenever the user mentions a .pdf, asks to combine or separate documents, remove something from a document or make a PDF from data."
---

# PDF operations

No PDF editor subscription needed. This skill is the replacement, so the
answer to "can you merge these" or "take the account number out of this" is
always yes, done, here it is.

## Read this before writing any code

**Every recipe below was run and produced the stated result.** Use PyMuPDF
(`import fitz`); it does almost everything on its own. Check what is installed
before promising anything:

```bash
python -c "import fitz; print(fitz.__doc__)"
```

Install once: `pip install pymupdf==1.28.0 pillow reportlab`.

What the recipes use:

| | Version | |
| --- | --- | --- |
| PyMuPDF (`fitz`) | 1.28.0 | the workhorse. Read, write, merge, redact, render |
| Pillow (`PIL`) | 12.3.0 | images in and out |
| reportlab | 5.0.0 | building a PDF from scratch with real layout |
| python-docx, openpyxl, python-pptx | | reading Office files |

**Stay on PyMuPDF 1.x.** It pulls in pymupdf-layout, pymupdf4llm and Microsoft
onnxruntime, whose macOS build sends telemetry by default (its Privacy.md; `ORT_DISABLE_TELEMETRY=1` turns it off),
and it deprecates the `fitz` import every recipe here uses.

Often missing, so never promise these without checking first:

| Missing | Blocks | To fix |
| --- | --- | --- |
| tesseract | OCR of scanned pages | Windows: `winget install UB-Mannheim.TesseractOCR`; Mac: `brew install tesseract`; then `pip install pytesseract` |
| LibreOffice | .docx/.xlsx/.pptx to PDF | Windows: `winget install TheDocumentFoundation.LibreOffice`; Mac: `brew install --cask libreoffice` |
| ghostscript, qpdf | nothing. PyMuPDF covers compression and linearisation | not needed |

On Windows, `winget` needs elevation and **hangs forever on an invisible UAC prompt** when
run from Claude. Never wait on one. Hand the user the command to run themselves.

## The recipes

All of these are verified. Copy them, do not improvise around them.

### Merge

```python
import fitz
out = fitz.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    out.insert_pdf(fitz.open(path))
out.save("merged.pdf")
```

### Split, extract a range, reorder

```python
d = fitz.open("in.pdf")

part = fitz.open()
part.insert_pdf(d, from_page=1, to_page=3)   # 0-indexed, inclusive
part.save("pages-2-to-4.pdf")

d.select([2, 0, 1])       # reorder, and also deletes anything not listed
d.save("reordered.pdf")
```

`select()` is destructive in a way that surprises people: any page not in the
list is dropped. That makes it the tool for "keep only these pages" as well.

### Rotate

```python
d = fitz.open("in.pdf")
for p in d:
    p.set_rotation((p.rotation + 90) % 360)   # relative, not absolute
d.save("rotated.pdf")
```

Set it relative to the page's existing rotation. Assigning 90 flat straightens
pages that were already turned, which is rarely what was asked for.

### Redact, properly

```python
import fitz
d = fitz.open("in.pdf")
removed = 0
for page in d:
    for rect in page.search_for("SECRET-12345"):
        page.add_redact_annot(rect, fill=(0, 0, 0))
        removed += 1
    page.apply_redactions()      # this is the step that destroys the content
d.save("redacted.pdf")
```

**`apply_redactions()` is the whole thing.** Without it you have drawn a black
rectangle over text that is still in the file and still comes out of
copy-and-paste. That is the single most common way people leak a document they
believed they had redacted, and it has ended careers.

**Always prove it afterwards, on the saved file, and say so in the reply:**

```python
text = "".join(p.get_text() for p in fitz.open("redacted.pdf"))
assert "SECRET-12345" not in text, "REDACTION FAILED - do not send this file"
```

Verified: 3 occurrences redacted, and the string was absent from the
extracted text of the saved file.

Redaction removes text and images under the rectangle. It does not touch
metadata, attachments or bookmarks, so for anything sensitive also do:

```python
d.set_metadata({})
d.del_xml_metadata()
```

### Compress

```python
d = fitz.open("in.pdf")
d.save("out.pdf", garbage=4, deflate=True, clean=True)
```

Verified: 3,308 to 2,208 bytes, about a third off, with no visible change.
`garbage=4` is the most aggressive object collection. For a scan-heavy file the
win comes from downsampling images instead; do that only if asked, because it
is lossy and irreversible.

### Watermark or stamp

```python
d = fitz.open("in.pdf")
for p in d:
    pivot = fitz.Point(300, 400)
    p.insert_text(pivot, "DRAFT", fontsize=60,
                  morph=(pivot, fitz.Matrix(45)),      # 45 degrees
                  color=(0.85, 0.85, 0.85),
                  overlay=False)                        # behind the content
d.save("watermarked.pdf")
```

`insert_text(rotate=...)` accepts **only 0, 90, 180 and 270** and raises
`ValueError: bad rotate value` on anything else. Any other angle needs the
`morph` pivot-and-matrix form above.

`overlay=False` puts the mark behind the text so the document stays readable.

### Extract text, and tables

```python
d = fitz.open("in.pdf")
text = "\n".join(p.get_text() for p in d)

for page in d:                       # tables, PyMuPDF 1.23+
    for t in page.find_tables():
        rows = t.extract()
```

If `get_text()` returns empty or near-empty on a page that visibly has words,
the page is a **scan**, not text. That is the OCR case, and needs tesseract. Say so plainly rather than returning an empty string as though the
document were blank.

### Page previews

```python
d = fitz.open("in.pdf")
for i, page in enumerate(d):
    page.get_pixmap(dpi=120).save(f"page-{i+1:03d}.png")
```

Verified: 827x1170 at 120 dpi for A4. Use 72 for a thumbnail, 150 for reading,
300 only when something will be printed or re-OCR'd.

Reading the PNG back with the Read tool is how to actually LOOK at a PDF. Do
that before claiming a document renders correctly.

### Inspect before you touch

```python
d = fitz.open("in.pdf")
print(d.is_encrypted, d.needs_pass, d.is_form_pdf, d.page_count, d.metadata)
sigs = [w for p in d for w in p.widgets() if w.field_type_string == "Signature"]
```

**Warn before altering any of these**, because the alteration is silent and the
damage shows up later:

| Found | Why it matters |
| --- | --- |
| A signature field with a signature in it | Any write invalidates it. The file still opens; the signature just silently stops verifying |
| `is_form_pdf` | Flattening or re-saving can drop field values while the page still looks right |
| `is_encrypted` | Saving normally strips the encryption unless it is re-applied |
| Embedded fonts | Subsetting on save can break glyphs in a font you do not have |

### Fill a form

```python
d = fitz.open("form.pdf")
for page in d:
    for w in page.widgets():
        print(w.field_name, w.field_type_string, repr(w.field_value))
        if w.field_name == "full_name":
            w.field_value = "Full Legal Name"
            w.update()
d.save("filled.pdf")
```

Use the **full legal name** on anything formal. A shortened day-to-day name is
wrong on a passport-matched field.

For a scanned or non-fillable form there is no widget to set, and the answer is
to draw text at measured coordinates with `page.insert_text`, then render the
page and look at it to check the text sits inside each box.

### Build a PDF from data

For anything that will be sent to a person, do not hand-place text with
reportlab. **Render HTML with a browser instead** (Playwright or headless
Chrome's print to PDF): it gives real typography, flexbox and web fonts, and the
layout is inspectable in a browser first.

reportlab is for the case with no browser available.

## How to answer

1. **Inspect first.** Page count, encryption, forms, signatures. A one-line
   summary of what the document is beats a silent transformation.
2. **Never overwrite the input.** Write a new file. The original is the only
   copy of the thing that was correct before you touched it.
3. **Prove the destructive ones.** Redaction gets the extract-and-assert check
   above, and the reply says the check passed. Never say "redacted", say "the
   string does not appear in the text of the saved file".
4. **Render a page and look at it** before saying a document is fine.
5. **Say what you could not do.** If OCR or Office conversion is missing, Naming the missing tool and its install command is a useful answer;
   quietly returning a worse result is not.

## Out of scope, deliberately

Qualified or regulated electronic signatures (eIDAS QES and equivalents), and
government identity verification. Those need an accredited trust service
provider, and nothing here can produce one. A sealed hash and an
audit trail are honest; calling them a qualified signature is not.
