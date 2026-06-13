

import os
import threading
import traceback

import customtkinter as ctk
from tkinter import filedialog

from tools.dialogs import show_error, show_success
from tools.word_pdf import word_to_pdf, pdf_to_word


ctk.set_appearance_mode("dark")        # "dark" or "light"
ctk.set_default_color_theme("blue")    # base theme; sidebar uses custom colors


SIDEBAR_TOOLS = [
    ("📄 Word → PDF", "word_to_pdf"),
    ("📝 PDF → Word", "pdf_to_word"),
    ("🖼️ PDF → PPTX", "pdf_to_pptx"),
    ("📊 PPTX → PDF", "pptx_to_pdf"),
    ("📋 Word → PPTX", "word_to_pptx"),
    ("📑 PPTX → Word", "pptx_to_word"),
    ("🔍 OCR: Image → Text", "ocr_image_text"),
    ("✨ Text Enhancer", "text_enhancer"),
    ("🗜️ File Compressor", "file_compressor"),
    ("🖼️ Image Compressor", "image_compressor"),
]


class BaseToolFrame(ctk.CTkFrame):

    def __init__(self, master, app, title, description):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title_label = ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=30, pady=(30, 5))

        desc_label = ctk.CTkLabel(
            self, text=description, font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=30, pady=(0, 20))

        # Container for tool-specific widgets
        self.content = ctk.CTkFrame(self, corner_radius=15)
        self.content.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.content.grid_columnconfigure(0, weight=1)



class ComingSoonFrame(BaseToolFrame):
   

    def __init__(self, master, app, title):
        super().__init__(
            master, app, title,
            "This feature is under development by another team member."
        )

        self.content.grid_rowconfigure(0, weight=1)

        wrapper = ctk.CTkFrame(self.content, fg_color="transparent")
        wrapper.grid(row=0, column=0)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            wrapper, text="🚧", font=ctk.CTkFont(size=60)
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            wrapper, text="Feature Coming Soon",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack()

        ctk.CTkLabel(
            wrapper, text="Under Development — check back after the next sprint!",
            font=ctk.CTkFont(size=13), text_color=("gray30", "gray70")
        ).pack(pady=(5, 0))



class WordToPdfFrame(BaseToolFrame):
    

    def __init__(self, master, app):
        super().__init__(
            master, app, "Word to PDF Converter",
            "Convert .docx Word documents into PDF files instantly."
        )

        self.input_path = None
        self.output_path = None

        self.content.grid_rowconfigure(4, weight=1)

        # --- Input file selection ---
        ctk.CTkLabel(
            self.content, text="1. Select Word Document (.docx)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        input_row = ctk.CTkFrame(self.content, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=20)
        input_row.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_row, placeholder_text="No file selected...", state="readonly"
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            input_row, text="Browse", width=100, command=self.browse_input
        ).grid(row=0, column=1)

     
        ctk.CTkLabel(
            self.content, text="2. Choose Output Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        output_row = ctk.CTkFrame(self.content, fg_color="transparent")
        output_row.grid(row=3, column=0, sticky="ew", padx=20)
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            output_row, placeholder_text="Output PDF path...", state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            output_row, text="Browse", width=100, command=self.browse_output
        ).grid(row=0, column=1)

        
        action_area = ctk.CTkFrame(self.content, fg_color="transparent")
        action_area.grid(row=4, column=0, sticky="sew", padx=20, pady=20)
        action_area.grid_columnconfigure(0, weight=1)

        self.convert_btn = ctk.CTkButton(
            action_area, text="Convert to PDF", height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_conversion
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(action_area, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            action_area, text="Ready.", font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        self.status_label.grid(row=2, column=0, sticky="w")

   
    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Select Word Document",
            filetypes=[("Word Documents", "*.docx"), ("All Files", "*.*")]
        )
        if path:
            self.input_path = path
            self._set_entry(self.input_entry, path)

           
            base, _ = os.path.splitext(path)
            self.output_path = base + ".pdf"
            self._set_entry(self.output_entry, self.output_path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if path:
            self.output_path = path
            self._set_entry(self.output_entry, path)

    def _set_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="readonly")

    
    def start_conversion(self):
        if not self.input_path or not os.path.exists(self.input_path):
            show_error(self.app, "Missing Input", "Please select a valid .docx file first.")
            return
        if not self.output_path:
            show_error(self.app, "Missing Output", "Please choose where to save the PDF.")
            return

        self._set_busy(True, "Converting... please wait.")

        thread = threading.Thread(target=self._run_conversion, daemon=True)
        thread.start()

    def _run_conversion(self):
        try:
            def progress_cb(pct, msg):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            word_to_pdf(self.input_path, self.output_path, progress_cb=progress_cb)

            self.app.after(0, self._on_success)
        except Exception:
            err_text = traceback.format_exc(limit=3)
            self.app.after(0, lambda: self._on_failure(err_text))

    def _on_success(self):
        self._set_busy(False, "Done!")
        show_success(self.app, "Success", f"PDF saved to:\n{self.output_path}")

    def _on_failure(self, err_text):
        self._set_busy(False, "Failed.")
        show_error(self.app, "Conversion Failed", err_text)

    def _set_busy(self, busy, status_text):
        if busy:
            self.convert_btn.configure(state="disabled", text="Converting...")
            self.progress_bar.start()
        else:
            self.convert_btn.configure(state="normal", text="Convert to PDF")
            self.progress_bar.stop()
            self.progress_bar.set(0)
        self.status_label.configure(text=status_text)



class PdfToWordFrame(BaseToolFrame):
    """Fully implemented: convert a .pdf file to an editable .docx file."""

    def __init__(self, master, app):
        super().__init__(
            master, app, "PDF to Word Converter",
            "Convert PDF files into fully editable Word (.docx) documents."
        )

        self.input_path = None
        self.output_path = None

        self.content.grid_rowconfigure(4, weight=1)

        
        ctk.CTkLabel(
            self.content, text="1. Select PDF File (.pdf)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        input_row = ctk.CTkFrame(self.content, fg_color="transparent")
        input_row.grid(row=1, column=0, sticky="ew", padx=20)
        input_row.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            input_row, placeholder_text="No file selected...", state="readonly"
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            input_row, text="Browse", width=100, command=self.browse_input
        ).grid(row=0, column=1)

        
        ctk.CTkLabel(
            self.content, text="2. Choose Output Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        output_row = ctk.CTkFrame(self.content, fg_color="transparent")
        output_row.grid(row=3, column=0, sticky="ew", padx=20)
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            output_row, placeholder_text="Output DOCX path...", state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            output_row, text="Browse", width=100, command=self.browse_output
        ).grid(row=0, column=1)

        
        action_area = ctk.CTkFrame(self.content, fg_color="transparent")
        action_area.grid(row=4, column=0, sticky="sew", padx=20, pady=20)
        action_area.grid_columnconfigure(0, weight=1)

        self.convert_btn = ctk.CTkButton(
            action_area, text="Convert to Word", height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_conversion
        )
        self.convert_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(action_area, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            action_area, text="Ready.", font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        self.status_label.grid(row=2, column=0, sticky="w")

    
    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if path:
            self.input_path = path
            self._set_entry(self.input_entry, path)

            base, _ = os.path.splitext(path)
            self.output_path = base + ".docx"
            self._set_entry(self.output_entry, self.output_path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save Word Document As",
            defaultextension=".docx",
            filetypes=[("Word Documents", "*.docx")]
        )
        if path:
            self.output_path = path
            self._set_entry(self.output_entry, path)

    def _set_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="readonly")

    
    def start_conversion(self):
        if not self.input_path or not os.path.exists(self.input_path):
            show_error(self.app, "Missing Input", "Please select a valid .pdf file first.")
            return
        if not self.output_path:
            show_error(self.app, "Missing Output", "Please choose where to save the Word document.")
            return

        self._set_busy(True, "Converting... this may take a moment for larger PDFs.")

        thread = threading.Thread(target=self._run_conversion, daemon=True)
        thread.start()

    def _run_conversion(self):
        try:
            def progress_cb(pct, msg):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            pdf_to_word(self.input_path, self.output_path, progress_cb=progress_cb)

            self.app.after(0, self._on_success)
        except Exception:
            err_text = traceback.format_exc(limit=3)
            self.app.after(0, lambda: self._on_failure(err_text))

    def _on_success(self):
        self._set_busy(False, "Done!")
        show_success(self.app, "Success", f"Word document saved to:\n{self.output_path}")

    def _on_failure(self, err_text):
        self._set_busy(False, "Failed.")
        show_error(self.app, "Conversion Failed", err_text)

    def _set_busy(self, busy, status_text):
        if busy:
            self.convert_btn.configure(state="disabled", text="Converting...")
            self.progress_bar.start()
        else:
            self.convert_btn.configure(state="normal", text="Convert to Word")
            self.progress_bar.stop()
            self.progress_bar.set(0)
        self.status_label.configure(text=status_text)



class PdfToPptxFrame(ComingSoonFrame):
    """
    # TODO: Team Member B — implement PDF to PPTX here.
    Suggested libraries: PyMuPDF (fitz) + python-pptx
    Approach: render each PDF page as a high-res image, then insert each
    image as a full-slide picture into a new PPTX file.
    Logic should live in: tools/pdf_pptx.py -> def pdf_to_pptx(input_path, output_path, progress_cb=None)
    """
    def __init__(self, master, app):
        super().__init__(master, app, "PDF to PPTX Converter")


class PptxToPdfFrame(ComingSoonFrame):
    """
    # TODO: Team Member C — implement PPTX to PDF here.
    Suggested libraries: python-pptx + reportlab or PyMuPDF for rendering.
    Logic should live in: tools/pptx_pdf.py -> def pptx_to_pdf(input_path, output_path, progress_cb=None)
    """
    def __init__(self, master, app):
        super().__init__(master, app, "PPTX to PDF Converter")


class WordToPptxFrame(ComingSoonFrame):
    """
    # TODO: Team Member D — implement Word to PPTX here.
    Suggested libraries: python-docx (extract text/headings) + python-pptx
    (build slides from extracted structure).
    Logic should live in: tools/word_pptx.py -> def word_to_pptx(input_path, output_path, progress_cb=None)
    """
    def __init__(self, master, app):
        super().__init__(master, app, "Word to PPTX Converter")


class PptxToWordFrame(ComingSoonFrame):
    """
    # TODO: Team Member E — implement PPTX to Word here.
    Suggested libraries: python-pptx (extract slide text/notes) + python-docx
    (append extracted content as headings/paragraphs).
    Logic should live in: tools/pptx_word.py -> def pptx_to_word(input_path, output_path, progress_cb=None)
    """
    def __init__(self, master, app):
        super().__init__(master, app, "PPTX to Word Converter")


class OcrImageTextFrame(ComingSoonFrame):
    """
    # TODO: Team Member F — implement OCR Text Extractor here.
    Suggested libraries: easyocr (preferred, zero system setup) or pytesseract.
    Logic should live in: tools/ocr.py -> def extract_text_from_image(image_path, progress_cb=None) -> str
    UI should display extracted text in a CTkTextbox with a "Copy" / "Save as .txt" button.
    """
    def __init__(self, master, app):
        super().__init__(master, app, "OCR: Text Extractor from Image")


class TextEnhancerFrame(ComingSoonFrame):
    """
    # TODO: Team Member G — implement Text Visualization Enhancer here.
    This is a pure-GUI feature (no heavy library needed):
    - A CTkTextbox for text input/preview.
    - Controls for font size, contrast/highlight color, bold/italic toggles.
    - Optional: load text from a .txt file and save the formatted result.
    """
    def __init__(self, master, app):
        super().__init__(master, app, "Text Visualization Enhancer")


class FileCompressorFrame(ComingSoonFrame):
    """
    # TODO: Team Member H — implement File Compressor here.
    Suggested libraries: zipfile, zlib (both in Python standard library).
    Logic should live in: tools/file_compressor.py
        -> def compress_files(file_paths: list[str], output_zip_path: str, progress_cb=None)
    UI should allow selecting MULTIPLE files (filedialog.askopenfilenames)
    and bundling them into a single .zip archive.
    """
    def __init__(self, master, app):
        super().__init__(master, app, "File Compressor")


class ImageCompressorFrame(ComingSoonFrame):
    """
    # TODO: Team Member I — implement Image Compressor here.
    Suggested library: Pillow (PIL) — use Image.save() with `quality=` and/or
    `Image.resize()` for downscaling, and `optimize=True` for memory savings.
    Logic should live in: tools/image_compressor.py
        -> def compress_image(input_path, output_path, quality=70, max_dimension=None, progress_cb=None)
    UI should include a quality slider (CTkSlider) and optional resize inputs.
    """
    def __init__(self, master, app):
        super().__init__(master, app, "Image Compressor")



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DocuVerse: The Ultimate Document Toolkit")
        self.geometry("1100x680")
        self.minsize(900, 600)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(len(SIDEBAR_TOOLS) + 2, weight=1)

        logo_label = ctk.CTkLabel(
            self.sidebar, text="📚 DocuVerse",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(25, 5), sticky="w")

        subtitle_label = ctk.CTkLabel(
            self.sidebar, text="Ultimate Document Toolkit",
            font=ctk.CTkFont(size=12), text_color=("gray30", "gray70")
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.nav_buttons = {}
        for i, (label, key) in enumerate(SIDEBAR_TOOLS, start=2):
            btn = ctk.CTkButton(
                self.sidebar, text=label, anchor="w", height=40,
                fg_color="transparent", text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray25"),
                font=ctk.CTkFont(size=14),
                command=lambda k=key: self.show_frame(k)
            )
            btn.grid(row=i, column=0, padx=15, pady=4, sticky="ew")
            self.nav_buttons[key] = btn

        # Appearance mode switch at the bottom of the sidebar
        appearance_row = len(SIDEBAR_TOOLS) + 3
        self.appearance_switch = ctk.CTkSegmentedButton(
            self.sidebar, values=["Light", "Dark"],
            command=self._on_appearance_change
        )
        self.appearance_switch.set("Dark")
        self.appearance_switch.grid(row=appearance_row, column=0, padx=15, pady=20, sticky="ew")

        
        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "gray10"))
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

       
        self.frames = {}

        frame_classes = {
            "word_to_pdf": WordToPdfFrame,
            "pdf_to_word": PdfToWordFrame,
            "pdf_to_pptx": PdfToPptxFrame,
            "pptx_to_pdf": PptxToPdfFrame,
            "word_to_pptx": WordToPptxFrame,
            "pptx_to_word": PptxToWordFrame,
            "ocr_image_text": OcrImageTextFrame,
            "text_enhancer": TextEnhancerFrame,
            "file_compressor": FileCompressorFrame,
            "image_compressor": ImageCompressorFrame,
        }

        for key, frame_cls in frame_classes.items():
            frame = frame_cls(self.main_area, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[key] = frame

        # Show the first tool by default
        self.show_frame("word_to_pdf")

    
    def show_frame(self, key):
        """Raise the requested tool frame and highlight its nav button."""
        frame = self.frames.get(key)
        if frame is None:
            return
        frame.tkraise()

        # Highlight active sidebar button
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(fg_color=("gray75", "gray30"))
            else:
                btn.configure(fg_color="transparent")

    def _on_appearance_change(self, value):
        ctk.set_appearance_mode(value.lower())



if __name__ == "__main__":
    app = App()
    app.mainloop()
