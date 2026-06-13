# tools/pptx_pdf.py

import os

def pptx_to_pdf(input_path: str, output_path: str, progress_cb=None):
    if progress_cb:
        progress_cb(10, "Starting PPTX to PDF conversion...")
    try:
        import comtypes.client  # Windows only (requires PowerPoint installed)
        if progress_cb:
            progress_cb(30, "Opening PowerPoint...")
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1
        deck = powerpoint.Presentations.Open(os.path.abspath(input_path))
        if progress_cb:
            progress_cb(60, "Exporting to PDF...")
        deck.SaveAs(os.path.abspath(output_path), 32)  # 32 = ppSaveAsPDF
        deck.Close()
        powerpoint.Quit()
        if progress_cb:
            progress_cb(100, "Conversion complete.")
        return output_path
    except Exception as primary_err:
        try:
            if progress_cb:
                progress_cb(40, "Trying LibreOffice fallback...")
            import subprocess
            out_dir = os.path.dirname(os.path.abspath(output_path))
            subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf",
                 "--outdir", out_dir, os.path.abspath(input_path)],
                check=True,
                timeout=120
            )
            # LibreOffice saves as <original_name>.pdf in out_dir
            base_name = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            generated = os.path.join(out_dir, base_name)
            if generated != os.path.abspath(output_path) and os.path.exists(generated):
                os.rename(generated, output_path)
            if progress_cb:
                progress_cb(100, "Conversion complete (LibreOffice).")
            return output_path
        except Exception as fallback_err:
            raise RuntimeError(
                f"PPTX to PDF conversion failed.\n"
                f"Primary error (comtypes/PowerPoint): {primary_err}\n"
                f"Fallback error (LibreOffice): {fallback_err}\n\n"
                f"On Windows: install Microsoft PowerPoint.\n"
                f"On Mac/Linux: install LibreOffice and ensure 'libreoffice' is in your PATH."
            )