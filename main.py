

import os
import threading
import traceback

import customtkinter as ctk
from tkinter import filedialog, colorchooser    
import tkinter as tk             

from tools.dialogs import show_error, show_success, show_info
from tools.word_pdf import word_to_pdf, pdf_to_word
from tools.pdf_pptx import pdf_to_pptx
from tools.word_pptx import word_to_pptx
from tools.pptx_word import pptx_to_word
from tools.ocr import extract_text_from_image, get_supported_languages

ctk.set_appearance_mode("dark")        
ctk.set_default_color_theme("blue")    


SIDEBAR_TOOLS = [
    ("📄 Word → PDF", "word_to_pdf"),
    ("📝 PDF → Word", "pdf_to_word"),
    ("📊 PDF → PPTX", "pdf_to_pptx"),
    ("📊 PPTX → PDF", "pptx_to_pdf"),
    ("📋 Word → PPTX", "word_to_pptx"),
    ("📑 PPTX → Word", "pptx_to_word"),
    ("🔍 OCR: Image → Text", "ocr_image_text"),
    ("✨ Text Editor", "text_editor"),
    ("🗜️ File Compressor", "file_compressor"),
    ("🖼️ Image Compressor", "image_compressor"),
]


class BaseToolFrame(ctk.CTkFrame):

    def __init__(self, master, app, title, description):
        super().__init__(master, fg_color="transparent")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header bar to house both the back navigation and the title frame safely
        header_bar = ctk.CTkFrame(self, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="w", padx=30, pady=(30, 5))
        
        back_btn = ctk.CTkButton(
            header_bar, text="⬅ Back to Dashboard", width=140, height=30,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("gray75", "gray25"), hover_color=("gray65", "gray35"),
            command=lambda: self.app.show_frame("home")
        )
        back_btn.pack(side="left", padx=(0, 15))

        title_label = ctk.CTkLabel(
            header_bar, text=title, font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.pack(side="left")

        desc_label = ctk.CTkLabel(
            self, text=description, font=ctk.CTkFont(size=14),
            text_color=("gray30", "gray70")
        )
        desc_label.grid(row=1, column=0, sticky="w", padx=30, pady=(0, 20))

        self.content = ctk.CTkFrame(self, corner_radius=15)
        self.content.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.content.grid_columnconfigure(0, weight=1)



class HomeDashboardFrame(ctk.CTkFrame):
    """Landing screen showing all tools as clickable cards."""

    TOOL_CARDS = [
        ("📄", "Word → PDF",       "Convert Word documents\nto PDF format.",          "word_to_pdf"),
        ("📝", "PDF → Word",       "Convert PDF files into\neditable Word documents.", "pdf_to_word"),
        ("📊", "PDF → PPTX",       "Turn PDF pages into\nPowerPoint slides.",          "pdf_to_pptx"),
        ("📊", "PPTX → PDF",       "Export presentations\nas PDF files.",              "pptx_to_pdf"),
        ("📋", "Word → PPTX",      "Convert Word documents\nto presentations.",         "word_to_pptx"),
        ("📑", "PPTX → Word",      "Extract content from\nslides into Word.",           "pptx_to_word"),
        ("🔍", "OCR: Image→Text",  "Extract text from any\nimage using AI-OCR.",       "ocr_image_text"),
        ("✨", "Text Editor",       "Edit and style text\nwith live formatting.",        "text_editor"),
        ("🗜️", "File Compressor",  "Compress multiple files\ninto a .zip archive.",     "file_compressor"),
        ("🖼️", "Image Compressor", "Reduce image file size\nwith quality control.",    "image_compressor"),
    ]

    def __init__(self, master, app):
        super().__init__(master, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(35, 20))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        ctk.CTkLabel(
            title_frame, text="📚 DocuVerse",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame, text="Select a tool to get started",
            font=ctk.CTkFont(size=15),
            text_color=("gray40", "gray60")
        ).pack(anchor="w", pady=(4, 0))

        appearance_switch = ctk.CTkSegmentedButton(
            header, values=["Light", "Dark"],
            command=self.app._on_appearance_change
        )
        appearance_switch.set(ctk.get_appearance_mode().capitalize())
        appearance_switch.pack(side="right", anchor="n", pady=5)

        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))

        cols = 4
        for i, (icon, name, desc, key) in enumerate(self.TOOL_CARDS):
            row, col = divmod(i, cols)
            card = ctk.CTkFrame(scroll, corner_radius=14, border_width=1,
                                border_color=("gray80", "gray28"))
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            scroll.grid_columnconfigure(col, weight=1)

            # Icon
            ctk.CTkLabel(
                card, text=icon, font=ctk.CTkFont(size=36)
            ).pack(pady=(18, 6))

            # Tool name
            ctk.CTkLabel(
                card, text=name,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack()

            # Description
            ctk.CTkLabel(
                card, text=desc,
                font=ctk.CTkFont(size=12),
                text_color=("gray40", "gray60"),
                justify="center"
            ).pack(pady=(4, 10))


            ctk.CTkButton(
                card, text="Open Tool", height=32,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=8,
                command=lambda k=key: self.app.show_frame(k)
            ).pack(pady=(0, 16))



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



class PdfToPptxFrame(BaseToolFrame):
    def __init__(self, master, app):
        super().__init__(
            master, 
            app, 
            "PDF to PPTX Converter", 
            "Convert your PDF presentations into editable PowerPoint slideshows (.pptx)."
        )
        self.selected_file = None

        
        self.content_container = ctk.CTkFrame(self, fg_color=("gray90", "gray16"), border_width=1, border_color=("gray80", "gray25"))
        self.content_container.grid(row=2, column=0, padx=40, pady=20, sticky="ew")
        self.content_container.grid_columnconfigure(0, weight=1)

        
        self.file_label = ctk.CTkLabel(
            self.content_container, 
            text="No file selected", 
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="gray50"
        )
        self.file_label.pack(pady=(25, 15), padx=20)

        
        self.browse_btn = ctk.CTkButton(
            self.content_container, 
            text="Browse PDF File", 
            command=self._browse_file,
            font=ctk.CTkFont(weight="bold")
        )
        self.browse_btn.pack(pady=(0, 25))

        
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12, slant="italic"), text_color="gray60")

        
        self.action_btn = ctk.CTkButton(
            self, 
            text="Convert to PowerPoint", 
            state="disabled",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._execute_tool
        )
        self.action_btn.grid(row=5, column=0, pady=30)

    def _browse_file(self):
        """Triggers file dialog window to choose a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select PDF Presentation",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            
            self.file_label.configure(
                text=f"Selected: {filename}", 
                text_color=("#1ABC9C", "#2ECC71"), 
                font=ctk.CTkFont(size=14, weight="bold")
            )
            self.action_btn.configure(state="normal")

    def _execute_tool(self):
        """Triggers output destination choices and handles threading pipelines"""
        if not self.selected_file:
            return

        output_path = filedialog.asksaveasfilename(
            title="Save PowerPoint Presentation",
            defaultextension=".pptx",
            filetypes=[("PowerPoint Presentations", "*.pptx")],
            initialfile=os.path.splitext(os.path.basename(self.selected_file))[0] + ".pptx"
        )
        if not output_path:
            return

        self.progress_bar.grid(row=3, column=0, pady=(10, 5))
        self.progress_bar.set(0)
        self.status_label.grid(row=4, column=0, pady=5)
        
        self.action_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")

        threading.Thread(
            target=self._run_conversion_worker, 
            args=(self.selected_file, output_path), 
            daemon=True
        ).start()

    def _run_conversion_worker(self, infile, outfile):
        try:
            def update_progress(pct, msg):
                self.progress_bar.set(pct / 100.0)
                self.status_label.configure(text=msg)

            from tools.pdf_pptx import pdf_to_pptx
            pdf_to_pptx(infile, outfile, progress_cb=update_progress)
            
            show_success(self.app, "Success", "Your PDF has been successfully converted into a PowerPoint file!")
            self.file_label.configure(text="No file selected", text_color="gray50", font=ctk.CTkFont(size=14, slant="italic"))
            self.selected_file = None
            
        except NotImplementedError as nie:
            show_error(self.app, "Feature Notice", str(nie))
        except Exception as e:
            traceback.print_exc()
            show_error(self.app, "Conversion Error", f"An unexpected error occurred:\n{str(e)}")
        finally:
            self.progress_bar.grid_forget()
            self.status_label.grid_forget()
            self.browse_btn.configure(state="normal")


class PptxToPdfFrame(BaseToolFrame):
    """PPTX to PDF — convert a PowerPoint presentation into a PDF file."""

    def __init__(self, master, app):
        super().__init__(
            master, app, "PPTX to PDF Converter",
            "Convert PowerPoint (.pptx) presentations into PDF files."
        )

        self.input_path = None
        self.output_path = None

        self.content.grid_rowconfigure(4, weight=1)

        # --- Input file selection ---
        ctk.CTkLabel(
            self.content, text="1. Select PowerPoint File (.pptx)",
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

        # --- Output file selection ---
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

        # --- Action area ---
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
            title="Select PowerPoint File",
            filetypes=[("PowerPoint Files", "*.pptx"), ("All Files", "*.*")]
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
            show_error(self.app, "Missing Input", "Please select a valid .pptx file first.")
            return
        if not self.output_path:
            show_error(self.app, "Missing Output", "Please choose where to save the PDF.")
            return
        self._set_busy(True, "Converting... please wait.")
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            def progress_cb(pct, msg):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            from tools.pptx_pdf import pptx_to_pdf
            pptx_to_pdf(self.input_path, self.output_path, progress_cb=progress_cb)
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


class WordToPptxFrame(BaseToolFrame):
    """Word to PPTX — convert a Word document into a PowerPoint presentation."""

    def __init__(self, master, app):
        super().__init__(
            master, app, "Word to PPTX Converter",
            "Convert Word (.docx) documents into editable PowerPoint (.pptx) presentations."
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

        # --- Output file selection ---
        ctk.CTkLabel(
            self.content, text="2. Choose Output Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        output_row = ctk.CTkFrame(self.content, fg_color="transparent")
        output_row.grid(row=3, column=0, sticky="ew", padx=20)
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            output_row, placeholder_text="Output PPTX path...", state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            output_row, text="Browse", width=100, command=self.browse_output
        ).grid(row=0, column=1)

        # --- Action area ---
        action_area = ctk.CTkFrame(self.content, fg_color="transparent")
        action_area.grid(row=4, column=0, sticky="sew", padx=20, pady=20)
        action_area.grid_columnconfigure(0, weight=1)

        self.convert_btn = ctk.CTkButton(
            action_area, text="Convert to PPTX", height=45,
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
            self.output_path = base + ".pptx"
            self._set_entry(self.output_entry, self.output_path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save PowerPoint Presentation As",
            defaultextension=".pptx",
            filetypes=[("PowerPoint Presentations", "*.pptx")]
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
            show_error(self.app, "Missing Output", "Please choose where to save the PPTX.")
            return
        self._set_busy(True, "Converting... please wait.")
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            def progress_cb(pct, msg):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            word_to_pptx(self.input_path, self.output_path, progress_cb=progress_cb)
            self.app.after(0, self._on_success)
        except Exception:
            err_text = traceback.format_exc(limit=3)
            self.app.after(0, lambda: self._on_failure(err_text))

    def _on_success(self):
        self._set_busy(False, "Done!")
        show_success(self.app, "Success", f"PowerPoint saved to:\n{self.output_path}")

    def _on_failure(self, err_text):
        self._set_busy(False, "Failed.")
        show_error(self.app, "Conversion Failed", err_text)

    def _set_busy(self, busy, status_text):
        if busy:
            self.convert_btn.configure(state="disabled", text="Converting...")
            self.progress_bar.start()
        else:
            self.convert_btn.configure(state="normal", text="Convert to PPTX")
            self.progress_bar.stop()
            self.progress_bar.set(0)
        self.status_label.configure(text=status_text)


class PptxToWordFrame(BaseToolFrame):
    """PPTX to Word — convert a PowerPoint presentation into a Word document."""

    def __init__(self, master, app):
        super().__init__(
            master, app, "PPTX to Word Converter",
            "Convert PowerPoint (.pptx) presentations into editable Word (.docx) documents."
        )

        self.input_path = None
        self.output_path = None

        self.content.grid_rowconfigure(4, weight=1)

        # --- Input file selection ---
        ctk.CTkLabel(
            self.content, text="1. Select PowerPoint File (.pptx)",
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

        # --- Output file selection ---
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

        # --- Action area ---
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
            title="Select PowerPoint File",
            filetypes=[("PowerPoint Files", "*.pptx"), ("All Files", "*.*")]
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
            show_error(self.app, "Missing Input", "Please select a valid .pptx file first.")
            return
        if not self.output_path:
            show_error(self.app, "Missing Output", "Please choose where to save the Word document.")
            return
        self._set_busy(True, "Converting... please wait.")
        threading.Thread(target=self._run_conversion, daemon=True).start()

    def _run_conversion(self):
        try:
            def progress_cb(pct, msg):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            pptx_to_word(self.input_path, self.output_path, progress_cb=progress_cb)
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


class OcrImageTextFrame(BaseToolFrame):
    """
    Feature 7 — OCR: Image to Text.
    Extracts text from any image file using easyocr (primary) or
    pytesseract (fallback). Results are displayed in a live text box
    with copy-to-clipboard and save-as-.txt actions.
    Logic lives in tools/ocr.py.
    """

    # Supported image types for the file dialog
    _IMAGE_TYPES = [
        ("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp"),
        ("PNG",  "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("BMP",  "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
        ("All Files", "*.*"),
    ]

    def __init__(self, master, app):
        super().__init__(
            master, app,
            "OCR: Image → Text Extractor",
            "Extract text from any image (PNG, JPG, BMP, TIFF, WebP) "
            "using AI-powered optical character recognition."
        )

        self.input_path: str | None = None

        # ── Give content frame a two-column layout ──────────────────
        # Left column: controls  |  Right column: text preview (expandable)
        self.content.grid_columnconfigure(0, weight=0, minsize=270)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        # ── LEFT PANEL ──────────────────────────────────────────────
        left = ctk.CTkFrame(self.content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        left.grid_columnconfigure(0, weight=1)

        # Image thumbnail placeholder
        self.thumb_frame = ctk.CTkFrame(left, width=230, height=160, corner_radius=10)
        self.thumb_frame.grid(row=0, column=0, pady=(0, 14), sticky="ew")
        self.thumb_frame.grid_propagate(False)
        self.thumb_label = ctk.CTkLabel(
            self.thumb_frame, text="🖼️\nNo image selected",
            font=ctk.CTkFont(size=13), text_color=("gray40", "gray60")
        )
        self.thumb_label.place(relx=0.5, rely=0.5, anchor="center")

        # Browse button
        ctk.CTkButton(
            left, text="📂  Browse Image", height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.browse_image
        ).grid(row=1, column=0, sticky="ew", pady=(0, 12))

        # Language selector
        ctk.CTkLabel(
            left, text="OCR Language", font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self._lang_map = {
            "English":              "en",
            "French":               "fr",
            "German":               "de",
            "Spanish":              "es",
            "Italian":              "it",
            "Portuguese":           "pt",
            "Russian":              "ru",
            "Arabic":               "ar",
            "Hindi":                "hi",
            "Japanese":             "ja",
            "Korean":               "ko",
            "Chinese (Simplified)": "ch_sim",
            "Chinese (Traditional)":"ch_tra",
            "Turkish":              "tr",
        }
        self.lang_menu = ctk.CTkOptionMenu(
            left, values=list(self._lang_map.keys()),
            font=ctk.CTkFont(size=13)
        )
        self.lang_menu.set("English")
        self.lang_menu.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        # Run OCR button
        self.run_btn = ctk.CTkButton(
            left, text="🔍  Run OCR", height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_ocr
        )
        self.run_btn.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(left, mode="indeterminate")
        self.progress_bar.grid(row=5, column=0, sticky="ew", pady=(0, 6))
        self.progress_bar.set(0)

        # Status label
        self.status_label = ctk.CTkLabel(
            left, text="Ready.", font=ctk.CTkFont(size=12),
            text_color=("gray35", "gray65"), wraplength=230, justify="left"
        )
        self.status_label.grid(row=6, column=0, sticky="w")

        # ── Separator ───────────────────────────────────────────────
        sep = ctk.CTkFrame(self.content, width=2, fg_color=("gray75", "gray28"))
        sep.grid(row=0, column=0, sticky="ns", padx=(268, 0), pady=20)

        # ── RIGHT PANEL — text preview ───────────────────────────────
        right = ctk.CTkFrame(self.content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Toolbar above text box
        toolbar = ctk.CTkFrame(right, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        ctk.CTkLabel(
            toolbar, text="Extracted Text",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            toolbar, text="💾 Save .txt", width=100, height=30,
            font=ctk.CTkFont(size=12), command=self.save_text
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            toolbar, text="📋 Copy", width=80, height=30,
            font=ctk.CTkFont(size=12), command=self.copy_text
        ).pack(side="right", padx=(6, 0))

        ctk.CTkButton(
            toolbar, text="🗑 Clear", width=70, height=30,
            font=ctk.CTkFont(size=12), fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"), command=self.clear_text
        ).pack(side="right")

        # The main text area
        self.text_box = ctk.CTkTextbox(
            right, font=ctk.CTkFont(family="Courier New", size=13),
            wrap="word", corner_radius=10
        )
        self.text_box.grid(row=1, column=0, sticky="nsew")
        self.text_box.insert("0.0", "OCR output will appear here…")
        self.text_box.configure(state="disabled")

        # Word / char counter row
        self.counter_label = ctk.CTkLabel(
            right, text="Words: 0  |  Characters: 0",
            font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")
        )
        self.counter_label.grid(row=2, column=0, sticky="e", pady=(4, 0))

    # ── Helpers ─────────────────────────────────────────────────────
    def browse_image(self):
        path = filedialog.askopenfilename(
            title="Select Image File", filetypes=self._IMAGE_TYPES
        )
        if not path:
            return
        self.input_path = path

        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((226, 156))
            photo = ImageTk.PhotoImage(img)
            self._thumb_photo = photo
            self.thumb_label.configure(image=photo, text="")
        except Exception:
            fname = os.path.basename(path)
            self.thumb_label.configure(
                image=None,
                text=f"🖼️\n{fname}"
            )

        self.status_label.configure(text=f"Loaded: {os.path.basename(path)}")

    def start_ocr(self):
        if not self.input_path or not os.path.isfile(self.input_path):
            show_error(self.app, "No Image", "Please select an image file first.")
            return

        self._set_busy(True, "Initialising OCR engine…")
        lang_code = self._lang_map.get(self.lang_menu.get(), "en")
        threading.Thread(
            target=self._run_ocr, args=(lang_code,), daemon=True
        ).start()

    def _run_ocr(self, lang_code: str):
        try:
            def progress_cb(pct: int, msg: str):
                self.app.after(0, lambda: self.status_label.configure(text=msg))

            text = extract_text_from_image(
                self.input_path, lang=lang_code, progress_cb=progress_cb
            )
            self.app.after(0, lambda: self._on_success(text))
        except Exception:
            err = traceback.format_exc(limit=4)
            self.app.after(0, lambda: self._on_failure(err))

    def _on_success(self, text: str):
        self._set_busy(False, "OCR complete ✓")
        self._write_text(text)
        words = len(text.split())
        chars = len(text)
        self.counter_label.configure(text=f"Words: {words}  |  Characters: {chars}")

    def _on_failure(self, err: str):
        self._set_busy(False, "OCR failed.")
        show_error(self.app, "OCR Failed", err)

    def _write_text(self, text: str):
        self.text_box.configure(state="normal")
        self.text_box.delete("0.0", "end")
        self.text_box.insert("0.0", text)
        self.text_box.configure(state="disabled")

    def copy_text(self):
        self.text_box.configure(state="normal")
        text = self.text_box.get("0.0", "end").strip()
        self.text_box.configure(state="disabled")
        if text and text != "OCR output will appear here…":
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            show_info(self.app, "Copied", "Text copied to clipboard.")

    def save_text(self):
        self.text_box.configure(state="normal")
        text = self.text_box.get("0.0", "end").strip()
        self.text_box.configure(state="disabled")
        if not text or text == "OCR output will appear here…":
            show_error(self.app, "Nothing to Save", "Run OCR first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Extracted Text",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            show_success(self.app, "Saved", f"Text saved to:\n{path}")

    def clear_text(self):
        self._write_text("OCR output will appear here…")
        self.counter_label.configure(text="Words: 0  |  Characters: 0")
        self.status_label.configure(text="Ready.")

    def _set_busy(self, busy: bool, msg: str):
        if busy:
            self.run_btn.configure(state="disabled", text="Running OCR…")
            self.progress_bar.start()
        else:
            self.run_btn.configure(state="normal", text="🔍  Run OCR")
            self.progress_bar.stop()
            self.progress_bar.set(0)
        self.status_label.configure(text=msg)


class TextEditorFrame(BaseToolFrame):
   

    _FONTS = [
        "Helvetica", "Arial", "Courier New", "Times New Roman",
        "Georgia", "Verdana", "Trebuchet MS", "Consolas",
    ]
    _SIZES = [9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 28, 32, 36, 42, 48]

    def __init__(self, master, app):
        super().__init__(
            master, app,
            "Text Visualization Enhancer",
            "Load, edit, and stylise text with custom fonts, colours, highlights, "
            "and live formatting controls."
        )

        # Internal state
        self._font_family = "Helvetica"
        self._font_size   = 14
        self._bold        = False
        self._italic      = False
        self._underline   = False
        self._fg_color    = ""
        self._hl_color    = ""
        self._line_spacing = 4

        # ── Layout: toolbar on top, text area below ──────────────────
        self.content.grid_rowconfigure(2, weight=1)

        # ── TOOLBAR ROW 1 — Font controls ────────────────────────────
        bar1 = ctk.CTkFrame(self.content, fg_color="transparent")
        bar1.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))

        ctk.CTkLabel(bar1, text="Font:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))

        self.font_menu = ctk.CTkOptionMenu(
            bar1, values=self._FONTS, width=160,
            font=ctk.CTkFont(size=12),
            command=self._on_font_change
        )
        self.font_menu.set("Helvetica")
        self.font_menu.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(bar1, text="Size:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))

        self.size_var = ctk.StringVar(value="14")
        self.size_menu = ctk.CTkOptionMenu(
            bar1, values=[str(s) for s in self._SIZES], width=72,
            variable=self.size_var, font=ctk.CTkFont(size=12),
            command=self._on_size_change
        )
        self.size_menu.pack(side="left", padx=(0, 14))

        toggle_cfg = dict(width=36, height=32, font=ctk.CTkFont(size=13, weight="bold"))
        self.bold_btn = ctk.CTkButton(
            bar1, text="B", **toggle_cfg,
            fg_color=("gray75", "gray30"),
            command=self._toggle_bold
        )
        self.bold_btn.pack(side="left", padx=2)

        self.italic_btn = ctk.CTkButton(
            bar1, text="I", **toggle_cfg,
            fg_color=("gray75", "gray30"),
            command=self._toggle_italic
        )
        self.italic_btn.pack(side="left", padx=2)

        self.underline_btn = ctk.CTkButton(
            bar1, text="U", **toggle_cfg,
            fg_color=("gray75", "gray30"),
            command=self._toggle_underline
        )
        self.underline_btn.pack(side="left", padx=(2, 14))

        ctk.CTkButton(
            bar1, text="🎨 Text Colour", height=32, width=115,
            font=ctk.CTkFont(size=12), command=self._pick_fg
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            bar1, text="🖊 Highlight", height=32, width=100,
            font=ctk.CTkFont(size=12), command=self._pick_highlight
        ).pack(side="left", padx=2)

        self.clear_hl_btn = ctk.CTkButton(
            bar1, text="✖ Clear HL", height=32, width=90,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray28"), hover_color=("gray60", "gray38"),
            command=self._clear_highlight
        )
        self.clear_hl_btn.pack(side="left", padx=(2, 14))

        ctk.CTkLabel(bar1, text="Spacing:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        self.spacing_slider = ctk.CTkSlider(
            bar1, from_=0, to=20, number_of_steps=20, width=120,
            command=self._on_spacing_change
        )
        self.spacing_slider.set(self._line_spacing)
        self.spacing_slider.pack(side="left")

        # ── TOOLBAR ROW 2 — Find & file actions ──────────────────────
        bar2 = ctk.CTkFrame(self.content, fg_color="transparent")
        bar2.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkButton(
            bar2, text="📂 Load .txt", height=30, width=100,
            font=ctk.CTkFont(size=12), command=self.load_file
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            bar2, text="💾 Save .txt", height=30, width=100,
            font=ctk.CTkFont(size=12), command=self.save_file
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            bar2, text="🗑 Clear All", height=30, width=90,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray28"), hover_color=("gray60", "gray38"),
            command=self.clear_all
        ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(bar2, text="Find:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        self.find_entry = ctk.CTkEntry(bar2, placeholder_text="keyword…", width=160, height=30)
        self.find_entry.pack(side="left", padx=(0, 6))
        self.find_entry.bind("<Return>", lambda _e: self.find_highlight())

        ctk.CTkButton(
            bar2, text="🔎 Find & Highlight", height=30, width=140,
            font=ctk.CTkFont(size=12), command=self.find_highlight
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            bar2, text="✖ Clear Find", height=30, width=90,
            font=ctk.CTkFont(size=12),
            fg_color=("gray70", "gray28"), hover_color=("gray60", "gray38"),
            command=self._clear_find_tags
        ).pack(side="left")

        self.counter_label = ctk.CTkLabel(
            bar2, text="Words: 0  |  Chars: 0",
            font=ctk.CTkFont(size=11), text_color=("gray40", "gray60")
        )
        self.counter_label.pack(side="right", padx=6)

        # ── TEXT AREA ─────────────────────────────────────────────────
        text_container = ctk.CTkFrame(self.content, corner_radius=10)
        text_container.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            text_container,
            font=ctk.CTkFont(family="Helvetica", size=14),
            wrap="word", corner_radius=10
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")

        self._tk_text: tk.Text = self.textbox._textbox
        self._tk_text.bind("<<Modified>>", self._on_text_modified)
        self._tk_text.bind("<KeyRelease>", self._on_text_modified)

        self.textbox.insert("0.0", "Type or paste your text here, or load a .txt file…")
        self._apply_base_tag()

    # ── Tag helpers ───────────────────────────────────────────────────
    def _base_tag_name(self) -> str:
        return (
            f"base__{self._font_family}__{self._font_size}"
            f"__{'b' if self._bold else ''}__{'i' if self._italic else ''}"
            f"__{'u' if self._underline else ''}"
        )

    def _apply_base_tag(self):
        import tkinter.font as tkfont
        weight = "bold"   if self._bold    else "normal"
        slant  = "italic" if self._italic  else "roman"
        font   = tkfont.Font(
            family=self._font_family, size=self._font_size,
            weight=weight, slant=slant,
            underline=1 if self._underline else 0
        )
        tag = self._base_tag_name()
        cfg: dict = {"font": font, "spacing3": self._line_spacing}
        if self._fg_color:
            cfg["foreground"] = self._fg_color
        self._tk_text.tag_configure(tag, **cfg)
        self._tk_text.tag_add(tag, "1.0", "end")
        self._tk_text.tag_raise(tag)

    def _apply_hl_tag(self, color: str):
        try:
            sel_start = self._tk_text.index("sel.first")
            sel_end   = self._tk_text.index("sel.last")
        except tk.TclError:
            sel_start, sel_end = "1.0", "end"
        tag = f"hl__{color}"
        self._tk_text.tag_configure(tag, background=color)
        self._tk_text.tag_add(tag, sel_start, sel_end)

    def _clear_highlight(self):
        for tag in self._tk_text.tag_names():
            if tag.startswith("hl__"):
                self._tk_text.tag_remove(tag, "1.0", "end")

    def _clear_find_tags(self):
        self._tk_text.tag_remove("find_hl", "1.0", "end")

    # ── Toolbar callbacks ─────────────────────────────────────────────
    def _on_font_change(self, value: str):
        self._font_family = value
        self._apply_base_tag()

    def _on_size_change(self, value: str):
        try:
            self._font_size = int(value)
        except ValueError:
            return
        self._apply_base_tag()

    def _toggle_bold(self):
        self._bold = not self._bold
        active_color = ("gray55", "gray50")
        off_color    = ("gray75", "gray30")
        self.bold_btn.configure(fg_color=active_color if self._bold else off_color)
        self._apply_base_tag()

    def _toggle_italic(self):
        self._italic = not self._italic
        active_color = ("gray55", "gray50")
        off_color    = ("gray75", "gray30")
        self.italic_btn.configure(fg_color=active_color if self._italic else off_color)
        self._apply_base_tag()

    def _toggle_underline(self):
        self._underline = not self._underline
        active_color = ("gray55", "gray50")
        off_color    = ("gray75", "gray30")
        self.underline_btn.configure(fg_color=active_color if self._underline else off_color)
        self._apply_base_tag()

    def _pick_fg(self):
        color = colorchooser.askcolor(
            color=self._fg_color or None, title="Choose Text Colour"
        )
        if color and color[1]:
            self._fg_color = color[1]
            self._apply_base_tag()

    def _pick_highlight(self):
        color = colorchooser.askcolor(
            color=self._hl_color or None, title="Choose Highlight Colour"
        )
        if color and color[1]:
            self._hl_color = color[1]
            self._apply_hl_tag(self._hl_color)

    def _on_spacing_change(self, value):
        self._line_spacing = int(value)
        self._apply_base_tag()

    def _on_text_modified(self, _event=None):
        try:
            text = self._tk_text.get("1.0", "end-1c")
            words = len(text.split()) if text.strip() else 0
            chars = len(text)
            self.counter_label.configure(text=f"Words: {words}  |  Chars: {chars}")
        except Exception:
            pass

    # ── Find & Highlight ─────────────────────────────────────────────
    def find_highlight(self):
        keyword = self.find_entry.get().strip()
        if not keyword:
            return
        self._clear_find_tags()
        self._tk_text.tag_configure(
            "find_hl", background="#FFDD57", foreground="#000000"
        )
        start = "1.0"
        count_var = tk.IntVar()
        found = 0
        while True:
            pos = self._tk_text.search(keyword, start, stopindex="end",
                                       count=count_var, nocase=True)
            if not pos:
                break
            end = f"{pos}+{count_var.get()}c"
            self._tk_text.tag_add("find_hl", pos, end)
            start = end
            found += 1
        if found == 0:
            show_info(self.app, "Not Found", f'No matches for "{keyword}".')
        else:
            first = self._tk_text.tag_ranges("find_hl")
            if first:
                self._tk_text.see(first[0])

    # ── File I/O ──────────────────────────────────────────────────────
    def load_file(self):
        path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            self.textbox.delete("0.0", "end")
            self.textbox.insert("0.0", content)
            self._apply_base_tag()
            self._on_text_modified()
        except Exception as exc:
            show_error(self.app, "Load Failed", str(exc))

    def save_file(self):
        text = self._tk_text.get("1.0", "end-1c")
        if not text.strip():
            show_error(self.app, "Nothing to Save", "The editor is empty.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Text File", defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            show_success(self.app, "Saved", f"File saved to:\n{path}")

    def clear_all(self):
        self.textbox.delete("0.0", "end")
        self._clear_find_tags()
        self._clear_highlight()
        self._on_text_modified()


class FileCompressorFrame(BaseToolFrame):
    """Compress multiple files into a single .zip archive."""

    def __init__(self, master, app):
        super().__init__(
            master, app, "File Compressor",
            "Select multiple files and compress them into a single .zip archive."
        )

        self.selected_files = []
        self.output_path = None

        self.content.grid_rowconfigure(4, weight=1)

        # --- File list label ---
        ctk.CTkLabel(
            self.content, text="1. Select Files to Compress",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        file_row = ctk.CTkFrame(self.content, fg_color="transparent")
        file_row.grid(row=1, column=0, sticky="ew", padx=20)
        file_row.grid_columnconfigure(0, weight=1)

        self.files_entry = ctk.CTkEntry(
            file_row, placeholder_text="No files selected...", state="readonly"
        )
        self.files_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            file_row, text="Browse", width=100, command=self.browse_files
        ).grid(row=0, column=1)

        # --- Output zip location ---
        ctk.CTkLabel(
            self.content, text="2. Choose Output .zip Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        output_row = ctk.CTkFrame(self.content, fg_color="transparent")
        output_row.grid(row=3, column=0, sticky="ew", padx=20)
        output_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            output_row, placeholder_text="Output .zip path...", state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            output_row, text="Browse", width=100, command=self.browse_output
        ).grid(row=0, column=1)

        # --- Action area ---
        action_area = ctk.CTkFrame(self.content, fg_color="transparent")
        action_area.grid(row=4, column=0, sticky="sew", padx=20, pady=20)
        action_area.grid_columnconfigure(0, weight=1)

        self.compress_btn = ctk.CTkButton(
            action_area, text="Compress Files", height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_compression
        )
        self.compress_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(action_area)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            action_area, text="Ready.", font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        self.status_label.grid(row=2, column=0, sticky="w")

    def browse_files(self):
        paths = filedialog.askopenfilenames(title="Select Files to Compress")
        if paths:
            self.selected_files = list(paths)
            display = f"{len(paths)} file(s) selected"
            self._set_entry(self.files_entry, display)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save ZIP As", defaultextension=".zip",
            filetypes=[("ZIP Archive", "*.zip")]
        )
        if path:
            self.output_path = path
            self._set_entry(self.output_entry, path)

    def _set_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="readonly")

    def start_compression(self):
        if not self.selected_files:
            show_error(self.app, "No Files", "Please select at least one file.")
            return
        if not self.output_path:
            show_error(self.app, "No Output", "Please choose where to save the .zip file.")
            return
        self._set_busy(True, "Compressing...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            from tools.file_compressor import compress_files

            def cb(pct, msg):
                self.app.after(0, lambda: (
                    self.progress_bar.set(pct / 100),
                    self.status_label.configure(text=msg)
                ))

            compress_files(self.selected_files, self.output_path, progress_cb=cb)
            self.app.after(0, self._on_success)
        except Exception:
            err = traceback.format_exc(limit=3)
            self.app.after(0, lambda: self._on_failure(err))

    def _on_success(self):
        self._set_busy(False, "Done!")
        show_success(self.app, "Success", f"ZIP saved to:\n{self.output_path}")

    def _on_failure(self, err):
        self._set_busy(False, "Failed.")
        show_error(self.app, "Compression Failed", err)

    def _set_busy(self, busy, msg):
        if busy:
            self.compress_btn.configure(state="disabled", text="Compressing...")
        else:
            self.compress_btn.configure(state="normal", text="Compress Files")
        self.status_label.configure(text=msg)


class ImageCompressorFrame(BaseToolFrame):
    """Compress images by reducing quality and optionally resizing."""

    _IMAGE_TYPES = [
        ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"),
        ("All Files", "*.*"),
    ]

    def __init__(self, master, app):
        super().__init__(
            master, app, "Image Compressor",
            "Reduce image file size by adjusting quality and optionally resizing."
        )

        self.input_path = None
        self.output_path = None

        self.content.grid_rowconfigure(6, weight=1)

        # --- Input ---
        ctk.CTkLabel(
            self.content, text="1. Select Image",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        in_row = ctk.CTkFrame(self.content, fg_color="transparent")
        in_row.grid(row=1, column=0, sticky="ew", padx=20)
        in_row.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(
            in_row, placeholder_text="No image selected...", state="readonly"
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            in_row, text="Browse", width=100, command=self.browse_input
        ).grid(row=0, column=1)

        # --- Output ---
        ctk.CTkLabel(
            self.content, text="2. Choose Output Location",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        out_row = ctk.CTkFrame(self.content, fg_color="transparent")
        out_row.grid(row=3, column=0, sticky="ew", padx=20)
        out_row.grid_columnconfigure(0, weight=1)

        self.output_entry = ctk.CTkEntry(
            out_row, placeholder_text="Output image path...", state="readonly"
        )
        self.output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            out_row, text="Browse", width=100, command=self.browse_output
        ).grid(row=0, column=1)

        # --- Quality slider ---
        ctk.CTkLabel(
            self.content, text="3. JPEG Quality (ignored for PNG)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(20, 5))

        slider_row = ctk.CTkFrame(self.content, fg_color="transparent")
        slider_row.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.quality_label = ctk.CTkLabel(slider_row, text="Quality: 70", width=90)
        self.quality_label.pack(side="left", padx=(0, 10))

        self.quality_slider = ctk.CTkSlider(
            slider_row, from_=10, to=95, number_of_steps=85,
            command=self._on_quality_change
        )
        self.quality_slider.set(70)
        self.quality_slider.pack(side="left", fill="x", expand=True)

        # --- Max dimension ---
        dim_row = ctk.CTkFrame(self.content, fg_color="transparent")
        dim_row.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            dim_row, text="Max Dimension (px, blank = no resize):",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))

        self.dim_entry = ctk.CTkEntry(dim_row, placeholder_text="e.g. 1920", width=120)
        self.dim_entry.pack(side="left")

        # --- Action area ---
        action_area = ctk.CTkFrame(self.content, fg_color="transparent")
        action_area.grid(row=7, column=0, sticky="sew", padx=20, pady=20)
        action_area.grid_columnconfigure(0, weight=1)

        self.compress_btn = ctk.CTkButton(
            action_area, text="Compress Image", height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.start_compression
        )
        self.compress_btn.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.progress_bar = ctk.CTkProgressBar(action_area)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            action_area, text="Ready.", font=ctk.CTkFont(size=12),
            text_color=("gray30", "gray70")
        )
        self.status_label.grid(row=2, column=0, sticky="w")

    def _on_quality_change(self, val):
        self.quality_label.configure(text=f"Quality: {int(val)}")

    def browse_input(self):
        path = filedialog.askopenfilename(
            title="Select Image", filetypes=self._IMAGE_TYPES
        )
        if path:
            self.input_path = path
            self._set_entry(self.input_entry, path)
            base, ext = os.path.splitext(path)
            self.output_path = base + "_compressed" + ext
            self._set_entry(self.output_entry, self.output_path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save Compressed Image As",
            filetypes=self._IMAGE_TYPES
        )
        if path:
            self.output_path = path
            self._set_entry(self.output_entry, path)

    def _set_entry(self, entry, text):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(state="readonly")

    def start_compression(self):
        if not self.input_path or not os.path.exists(self.input_path):
            show_error(self.app, "No Input", "Please select a valid image file.")
            return
        if not self.output_path:
            show_error(self.app, "No Output", "Please choose where to save the output.")
            return
        self._set_busy(True, "Compressing...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            from tools.image_compressor import compress_image

            quality = int(self.quality_slider.get())
            dim_text = self.dim_entry.get().strip()
            max_dim = int(dim_text) if dim_text.isdigit() else None

            def cb(pct, msg):
                self.app.after(0, lambda: (
                    self.progress_bar.set(pct / 100),
                    self.status_label.configure(text=msg)
                ))

            compress_image(self.input_path, self.output_path,
                           quality=quality, max_dimension=max_dim, progress_cb=cb)
            self.app.after(0, self._on_success)
        except Exception:
            err = traceback.format_exc(limit=3)
            self.app.after(0, lambda: self._on_failure(err))

    def _on_success(self):
        self._set_busy(False, "Done!")
        show_success(self.app, "Success", f"Compressed image saved to:\n{self.output_path}")

    def _on_failure(self, err):
        self._set_busy(False, "Failed.")
        show_error(self.app, "Compression Failed", err)

    def _set_busy(self, busy, msg):
        if busy:
            self.compress_btn.configure(state="disabled", text="Compressing...")
        else:
            self.compress_btn.configure(state="normal", text="Compress Image")
        self.status_label.configure(text=msg)



class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("DocuVerse: The Ultimate Document Toolkit")
        self.geometry("1100x680")
        self.minsize(900, 600)

        # Single window full-width grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "gray10"))
        self.main_area.grid(row=0, column=0, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # Store the class blueprints instead of instantiating them immediately
        self.frame_classes = {
            "word_to_pdf": WordToPdfFrame,
            "pdf_to_word": PdfToWordFrame,
            "pdf_to_pptx": PdfToPptxFrame,
            "pptx_to_pdf": PptxToPdfFrame,
            "word_to_pptx": WordToPptxFrame,
            "pptx_to_word": PptxToWordFrame,
            "ocr_image_text": OcrImageTextFrame,
            "text_editor": TextEditorFrame,
            "file_compressor": FileCompressorFrame,
            "image_compressor": ImageCompressorFrame,
        }

        # Cache for active, initialized frames
        self.frames = {}

        # Load ONLY the home dashboard frame on initial startup
        home = HomeDashboardFrame(self.main_area, self)
        home.grid(row=0, column=0, sticky="nsew")
        self.frames["home"] = home
        
        self.show_frame("home")

    def show_frame(self, key):
        """Raise the requested tool frame, initializing it lazily only when needed."""
        frame = self.frames.get(key)
        
        # If the tool hasn't been opened yet during this session, build it now
        if frame is None and key in self.frame_classes:
            frame_cls = self.frame_classes[key]
            frame = frame_cls(self.main_area, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[key] = frame
            
        if frame:
            frame.tkraise()

    def _on_appearance_change(self, value):
        ctk.set_appearance_mode(value.lower())



if __name__ == "__main__":
    app = App()
    app.mainloop()
