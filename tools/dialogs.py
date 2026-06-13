import customtkinter as ctk

class ErrorDialog(ctk.CTkToplevel):
    def __init__(self, master, title="Error", message="", kind="error"):
        super().__init__(master)
        self.title(title)
        self.geometry("420x220")
        self.resizable(False, False)
        self.grab_set()
        self.attributes("-topmost", True)

        colors = {
            "error": ("#E74C3C", "❌"),
            "warning": ("#F39C12", "⚠️"),
            "info": ("#3498DB", "ℹ️"),
            "success": ("#2ECC71", "✅"),
        }
        accent, icon = colors.get(kind, colors["error"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=accent, height=50, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text=f"{icon}  {title}", font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=10, padx=15, anchor="w")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=15)

        msg_label = ctk.CTkLabel(
            body, text=message, wraplength=370, justify="left",
            font=ctk.CTkFont(size=13)
        )
        msg_label.pack(expand=True, fill="both")

        ok_btn = ctk.CTkButton(
            self, text="OK", width=100, fg_color=accent,
            hover_color=accent, command=self.destroy
        )
        ok_btn.grid(row=2, column=0, pady=(0, 15))

        self.update_idletasks()
        try:
            px = master.winfo_rootx()
            py = master.winfo_rooty()
            pw = master.winfo_width()
            ph = master.winfo_height()
            x = px + (pw // 2) - (420 // 2)
            y = py + (ph // 2) - (220 // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

def show_error(master, title, message):
    ErrorDialog(master, title=title, message=message, kind="error")

def show_success(master, title, message):
    ErrorDialog(master, title=title, message=message, kind="success")