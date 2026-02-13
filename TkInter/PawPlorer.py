import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import datetime
import sys
import subprocess
import shutil

class PawPlorer:
    def __init__(self, root):
        self.root = root
        self.root.geometry("900x600")
        self.root.title("PawPlorer")
        
        # --- 1. Path Setup ---
        if getattr(sys, 'frozen', False):
            self.app_path = os.path.dirname(sys.executable)
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))

        self.icons_dir = os.path.join(self.app_path, "icons")
        self.icon_cache = {}

        # --- 2. Embedded Icons (Fallback) ---
        self.fallback_folder_data = "R0lGODlhEAAQAJEAAAAAAP///////wAAACH5BAEAAAIALAAAAAAQABAAQAJDlI+py+0PO5i02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yiAAA7"
        self.fallback_file_data = "R0lGODlhEAAQAJEAAAAAAP///8zMzAAAACH5BAEAAAMALAAAAAAQABAAQAJIhI+py+0PO5i02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yuVwAA7"

        try:
            self.default_folder_icon = tk.PhotoImage(data=self.fallback_folder_data)
            self.default_file_icon = tk.PhotoImage(data=self.fallback_file_data)
        except Exception:
            self.default_folder_icon = None
            self.default_file_icon = None

        self.TXT_FOLDER = "📁"
        self.TXT_FILE = "📄"
        
        # State for view toggle
        self.details_view = True

        # --- 3. UI Construction ---
        self.setup_ui()
        self.populate_roots()
        self.navigate_to(os.getcwd())

    def setup_ui(self):
        # Menu
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Folder", command=self.create_new_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Open", command=self.on_open)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Delete", command=self.delete_item)
        self.file_menu.add_command(label="Rename", command=self.rename_item)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Refresh", command=self.refresh_all)
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Toggle Details/List", command=self.toggle_view)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # Main Toolbar Frame
        self.top_frame = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # --- Quick Access Toolbar ---
        self.qa_toolbar = tk.Frame(self.top_frame)
        self.qa_toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        # Helper to create toolbar buttons
        def create_qa_btn(text, command):
            btn = tk.Button(self.qa_toolbar, text=text, command=command, relief=tk.RAISED, padx=5, pady=2)
            btn.pack(side=tk.LEFT, padx=2)
            return btn

        create_qa_btn("🆕 New Folder", self.create_new_folder)
        create_qa_btn("❌ Delete", self.delete_item)
        create_qa_btn("✏️ Rename", self.rename_item)
        tk.Frame(self.qa_toolbar, width=10).pack(side=tk.LEFT) # Spacer
        self.view_btn = create_qa_btn("📜 List View", self.toggle_view)

        # --- Address Bar Toolbar ---
        self.addr_toolbar = tk.Frame(self.top_frame)
        self.addr_toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=(0,2))

        self.up_btn = tk.Button(self.addr_toolbar, text=" ⬆ Up ", command=self.go_up, relief=tk.RAISED)
        self.up_btn.pack(side=tk.LEFT, padx=2, pady=2)

        tk.Label(self.addr_toolbar, text=" Path: ").pack(side=tk.LEFT, padx=2)
        self.addr_var = tk.StringVar()
        self.addr_entry = tk.Entry(self.addr_toolbar, textvariable=self.addr_var, bg="white", relief=tk.SUNKEN)
        self.addr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
        self.addr_entry.bind("<Return>", self.on_address_enter)

        # Split View
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Left: Tree
        self.left_frame = tk.Frame(self.paned_window, bd=2, relief=tk.SUNKEN)
        self.paned_window.add(self.left_frame, width=250)
        
        self.tree_scroll_y = tk.Scrollbar(self.left_frame)
        self.tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_scroll_x = tk.Scrollbar(self.left_frame, orient=tk.HORIZONTAL)
        self.tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.folder_tree = ttk.Treeview(self.left_frame, show="tree", 
                                        yscrollcommand=self.tree_scroll_y.set,
                                        xscrollcommand=self.tree_scroll_x.set)
        self.folder_tree.pack(fill=tk.BOTH, expand=True)
        self.tree_scroll_y.config(command=self.folder_tree.yview)
        self.tree_scroll_x.config(command=self.folder_tree.xview)
        
        self.folder_tree.bind("<<TreeviewOpen>>", self.on_tree_expand)
        self.folder_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right: List
        self.right_frame = tk.Frame(self.paned_window, bd=2, relief=tk.SUNKEN)
        self.paned_window.add(self.right_frame)
        self.list_scroll = tk.Scrollbar(self.right_frame)
        self.list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_list_columns = ("size", "date")
        self.file_list = ttk.Treeview(self.right_frame, columns=self.file_list_columns, show="tree headings", 
                                      yscrollcommand=self.list_scroll.set)
        
        self.file_list.heading("#0", text="Name", anchor=tk.W)
        self.file_list.heading("size", text="Size", anchor=tk.E)
        self.file_list.heading("date", text="Date Modified", anchor=tk.W)
        self.file_list.column("#0", width=300, anchor=tk.W)
        self.file_list.column("size", width=80, anchor=tk.E)
        self.file_list.column("date", width=140, anchor=tk.W)

        self.file_list.pack(fill=tk.BOTH, expand=True)
        self.list_scroll.config(command=self.file_list.yview)
        self.file_list.bind("<Double-1>", self.on_file_double_click)
        
        # Initial View State
        self.update_view_button()

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- ICON SYSTEM (Auto-Shrink Enabled) ---
    def get_icon(self, item_name, is_dir):
        if is_dir:
            key = "folder"
            ext_key = None
        else:
            _, extension = os.path.splitext(item_name)
            ext_key = extension.lower().replace(".", "")
            if not ext_key: ext_key = "file"
            key = "file"

        # Check Cache
        if ext_key and ext_key in self.icon_cache: return self.icon_cache[ext_key]
        if key in self.icon_cache: return self.icon_cache[key]

        # Load from disk with AUTO-RESIZE logic
        def try_load(name_code):
            candidates = [f"{name_code}.png", f"{name_code}.gif"]
            for filename in candidates:
                full_path = os.path.join(self.icons_dir, filename)
                if os.path.exists(full_path):
                    try:
                        # 1. Load the full-size image
                        photo = tk.PhotoImage(file=full_path)
                        
                        # 2. Get dimensions
                        w = photo.width()
                        h = photo.height()

                        # 3. Calculate subsample factor (Integer math only)
                        scale_factor = w // 16
                        
                        if scale_factor > 1:
                            # Apply the shrink
                            photo = photo.subsample(scale_factor, scale_factor)

                        self.icon_cache[name_code] = photo
                        return photo
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
            return None

        if ext_key:
            icon = try_load(ext_key)
            if icon: return icon

        if key not in self.icon_cache:
            icon = try_load(key)
            if icon: return icon

        # Fallback
        return self.default_folder_icon if is_dir else self.default_file_icon

    # --- NEW FILE OPERATIONS ---
    def get_selected_path(self):
        sel = self.file_list.selection()
        if not sel: return None
        item_text = self.file_list.item(sel[0], "text")
        clean_name = item_text.strip()
        for sym in [self.TXT_FOLDER, self.TXT_FILE]:
            clean_name = clean_name.replace(sym, "").strip()
        return os.path.join(self.current_path, clean_name)

    def create_new_folder(self):
        new_name = simpledialog.askstring("New Folder", "Enter folder name:", parent=self.root)
        if new_name:
            path = os.path.join(self.current_path, new_name)
            try:
                os.makedirs(path, exist_ok=False)
                self.refresh_all()
                self.status_var.set(f"Created folder: {new_name}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")

    def delete_item(self):
        path = self.get_selected_path()
        if not path:
            messagebox.showinfo("Delete", "Please select an item to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{path}?"):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh_all()
                self.status_var.set("Item deleted.")
            except OSError as e:
                messagebox.showerror("Error", f"Could not delete item: {e}")

    def rename_item(self):
        old_path = self.get_selected_path()
        if not old_path:
            messagebox.showinfo("Rename", "Please select an item to rename.")
            return
        
        old_name = os.path.basename(old_path)
        new_name = simpledialog.askstring("Rename", f"Enter new name for '{old_name}':", initialvalue=old_name, parent=self.root)
        
        if new_name and new_name != old_name:
            new_path = os.path.join(self.current_path, new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh_all()
                self.status_var.set(f"Renamed to: {new_name}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not rename item: {e}")

    # --- VIEW TOGGLE LOGIC ---
    def toggle_view(self):
        self.details_view = not self.details_view
        if self.details_view:
            # Show columns
            self.file_list["displaycolumns"] = self.file_list_columns
            self.view_btn.config(text="📜 List View")
        else:
            # Hide columns (show only tree #0)
            self.file_list["displaycolumns"] = ()
            self.view_btn.config(text="📅 Details View")
            
    def update_view_button(self):
         # Set initial state
        if self.details_view:
            self.file_list["displaycolumns"] = self.file_list_columns
            self.view_btn.config(text="📜 List View")
        else:
            self.file_list["displaycolumns"] = ()
            self.view_btn.config(text="📅 Details View")


    # --- CORE LOGIC ---
    def populate_roots(self):
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

        roots = []
        if sys.platform == "win32":
            import string
            from ctypes import windll
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.ascii_uppercase:
                if bitmask & 1: roots.append(f"{letter}:\\")
                bitmask >>= 1
        else:
            roots = ["/"]

        for path in roots:
            self.insert_tree_node("", path, path, is_folder=True)

    def insert_tree_node(self, parent, text, path, is_folder=True):
        icon = self.get_icon(text, is_folder)
        kw = {"values": [path], "open": False}
        if icon:
            kw["text"] = f" {text}"
            kw["image"] = icon
        else:
            sym = self.TXT_FOLDER if is_folder else self.TXT_FILE
            kw["text"] = f" {sym} {text}"

        node = self.folder_tree.insert(parent, tk.END, **kw)
        if is_folder:
            self.folder_tree.insert(node, tk.END, text="dummy")

    def on_tree_expand(self, event):
        item_id = self.folder_tree.focus()
        if not item_id: return
        values = self.folder_tree.item(item_id, "values")
        if not values: return
        path = values[0]

        if self.folder_tree.get_children(item_id):
            self.folder_tree.delete(*self.folder_tree.get_children(item_id))

        try:
            with os.scandir(path) as entries:
                sorted_entries = sorted(entries, key=lambda e: e.name.lower())
                for entry in sorted_entries:
                    if entry.is_dir(follow_symlinks=False):
                        try:
                            self.insert_tree_node(item_id, entry.name, entry.path, is_folder=True)
                        except PermissionError: pass
        except PermissionError: pass

    def on_tree_select(self, event):
        sel = self.folder_tree.selection()
        if sel:
            path = self.folder_tree.item(sel[0], "values")[0]
            self.load_file_list(path)

    def load_file_list(self, path):
        self.addr_var.set(path)
        self.current_path = path
        for item in self.file_list.get_children():
            self.file_list.delete(item)

        try:
            with os.scandir(path) as entries:
                entries = sorted(entries, key=lambda e: (not e.is_dir(), e.name.lower()))
                count = 0
                for entry in entries:
                    count += 1
                    try:
                        stats = entry.stat()
                        size = self.format_size(stats.st_size) if entry.is_file() else ""
                        mtime = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
                    except OSError:
                        size, mtime = "???", "???"

                    is_dir = entry.is_dir()
                    icon = self.get_icon(entry.name, is_dir)
                    
                    kw = {"values": (size, mtime)}
                    if icon:
                        kw["text"] = f" {entry.name}"
                        kw["image"] = icon
                    else:
                        sym = self.TXT_FOLDER if is_dir else self.TXT_FILE
                        kw["text"] = f" {sym} {entry.name}"
                    self.file_list.insert("", tk.END, **kw)
                self.status_var.set(f" Found {count} items.")
        except (PermissionError, FileNotFoundError):
            self.status_var.set(" Error accessing path.")

    def navigate_to(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.load_file_list(path)

    def on_file_double_click(self, event):
        path = self.get_selected_path()
        if not path: return

        if os.path.isdir(path):
            self.navigate_to(path)
        else:
            self.open_file_system(path)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.navigate_to(parent)

    def on_address_enter(self, event):
        self.navigate_to(self.addr_var.get())

    def on_open(self):
        self.on_file_double_click(None)

    def refresh_all(self):
        self.populate_roots()
        self.load_file_list(self.current_path)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024: return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def open_file_system(self, path):
        try:
            if sys.platform == 'win32': os.startfile(path)
            elif sys.platform == 'darwin': subprocess.call(('open', path))
            else: subprocess.call(('xdg-open', path))
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open: {e}")

    def show_about(self):
        messagebox.showinfo("About", "PawPlorer v2.5\nWith New Folder, Delete, Rename!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PawPlorer(root)
    root.mainloop()