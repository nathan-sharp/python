import tkinter as tk
from tkinter import filedialog, messagebox
import os

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.root.title("Untitled - PawPad")
        
        # --- 1. The Menu Bar ---
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open...", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit Menu
        # We use standard event_generate to leverage built-in OS clipboard functions
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self.select_all)

        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About PawPad", command=self.show_about)

        # --- 2. The Scrollbar & Text Area ---
        # Using standard Scrollbar and Text instead of ttk for that 'classic' unstyled look
        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # font="Courier" mimics the fixed-width font of old terminals/editors
        self.text_area = tk.Text(self.root, 
                                 font=("Courier", 10), 
                                 undo=True, 
                                 yscrollcommand=self.scrollbar.set)
        self.text_area.pack(fill=tk.BOTH, expand=1)
        
        # Link scrollbar to text area
        self.scrollbar.config(command=self.text_area.yview)

        # State variable for the current file path
        self.current_file = None

    # --- File Operations ---
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("Untitled - PawPad")

    def open_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt",
                                               filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path
            self.root.title(f"{os.path.basename(file_path)} - PawPad")
            self.text_area.delete(1.0, tk.END)
            with open(file_path, "r") as file:
                self.text_area.insert(1.0, file.read())

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(initialfile="Untitled.txt",
                                                 defaultextension=".txt",
                                                 filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.current_file = file_path
            self.root.title(f"{os.path.basename(file_path)} - PawPad")
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, tk.END))

    # --- Edit Operations ---
    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def show_about(self):
        messagebox.showinfo("About PawPad", "Python TkInter PawPad\n\nA simple text editor.\n\nCopyright (c)2026 Nathan James Sharp.")

if __name__ == "__main__":
    root = tk.Tk()
    app = Notepad(root)
    root.mainloop()
