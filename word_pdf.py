
import os


def word_to_pdf(input_path: str, output_path: str, progress_cb=None):
    
    if progress_cb:
        progress_cb(10, "Starting Word to PDF conversion...")

    try:
        from docx2pdf import convert
        if progress_cb:
            progress_cb(40, "Converting with docx2pdf...")
        convert(input_path, output_path)
        if progress_cb:
            progress_cb(100, "Conversion complete.")
        return output_path
    except Exception as primary_err:
        
        try:
            if progress_cb:
                progress_cb(50, "Falling back to pypandoc...")
            import pypandoc
            pypandoc.convert_file(input_path, "pdf", outputfile=output_path)
            if progress_cb:
                progress_cb(100, "Conversion complete (pypandoc).")
            return output_path
        except Exception as fallback_err:
            raise RuntimeError(
                f"Word to PDF conversion failed.\n"
                f"Primary error (docx2pdf): {primary_err}\n"
                f"Fallback error (pypandoc): {fallback_err}\n\n"
                f"docx2pdf requires MS Word (Windows/Mac). "
                f"pypandoc requires Pandoc + a PDF engine (e.g. wkhtmltopdf) installed on your system."
            )


def pdf_to_word(input_path: str, output_path: str, progress_cb=None):
    """Convert a PDF file to an editable .docx file using pdf2docx."""
    from pdf2docx import Converter

    if progress_cb:
        progress_cb(5, "Opening PDF...")

    cv = Converter(input_path)
    try:
        total_pages = len(cv.fitz_doc)

        def _cb(page_idx):
            if progress_cb and total_pages:
                pct = 10 + int(((page_idx + 1) / total_pages) * 85)
                progress_cb(min(pct, 95), f"Processing page {page_idx + 1}/{total_pages}...")

        if progress_cb:
            progress_cb(10, "Converting pages...")

        # pdf2docx doesn't natively support per-page callbacks in convert(),
        # so we approximate progress before/after the bulk operation.
        cv.convert(output_path, start=0, end=None)

        if progress_cb:
            progress_cb(100, "Conversion complete.")
    finally:
        cv.close()

    if not os.path.exists(output_path):
        raise RuntimeError("PDF to Word conversion did not produce an output file.")

    return output_path
